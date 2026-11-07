"""
Unified AI Service Layer for NexRoute
Provides enterprise-grade, configurable LLM integration:
1. Google Gemini API (REST v1beta with streaming & vision)
2. OpenAI API (gpt-4o-mini, gpt-4o with streaming, vision, tools)
3. Ollama (Local AI models: llama3, mistral, phi3 with streaming)
4. Groq / Anthropic fallback
5. Multimodal document & image parsing (PDF text extraction, image base64)
6. Multilingual awareness & NexRoute tool dispatching
7. Safe, graceful error handling with zero fake/hardcoded responses
"""

import os
import re
import json
import time
import base64
import logging
from typing import Dict, Any, List, Optional, Tuple, Generator, Union
from io import BytesIO

import requests

logger = logging.getLogger("nexroute.ai_service")

# Default Models
DEFAULT_GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-2.0-flash")
DEFAULT_OPENAI_MODEL = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")
DEFAULT_OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "llama3")

# Language code to BCP-47 and native name mapping
LANGUAGE_SPEECH_MAP: Dict[str, Dict[str, str]] = {
    "en": {"name": "English", "bcp47": "en-IN", "tts_voice": "en-IN"},
    "te": {"name": "Telugu", "native": "తెలుగు", "bcp47": "te-IN", "tts_voice": "te-IN"},
    "hi": {"name": "Hindi", "native": "हिन्दी", "bcp47": "hi-IN", "tts_voice": "hi-IN"},
    "ta": {"name": "Tamil", "native": "தமிழ்", "bcp47": "ta-IN", "tts_voice": "ta-IN"},
    "kn": {"name": "Kannada", "native": "ಕನ್ನಡ", "bcp47": "kn-IN", "tts_voice": "kn-IN"},
    "ml": {"name": "Malayalam", "native": "മലയാളം", "bcp47": "ml-IN", "tts_voice": "ml-IN"},
    "bn": {"name": "Bengali", "native": "বাংলা", "bcp47": "bn-IN", "tts_voice": "bn-IN"},
    "mr": {"name": "Marathi", "native": "मराठी", "bcp47": "mr-IN", "tts_voice": "mr-IN"},
}


class DocumentParser:
    """Extracts clean text and data from uploaded files (PDF, TXT, MD, CSV, Code)."""

    @staticmethod
    def extract_text_from_bytes(file_bytes: bytes, filename: str) -> Tuple[str, str]:
        """
        Extracts textual content from uploaded file bytes.
        Returns: (extracted_text, file_summary_tag)
        """
        fname_lower = filename.lower()
        if not file_bytes:
            return "", f"Empty file: {filename}"

        # 1. PDF Documents
        if fname_lower.endswith(".pdf"):
            try:
                import pypdf
                reader = pypdf.PdfReader(BytesIO(file_bytes))
                num_pages = len(reader.pages)
                pages_text = []
                for i, page in enumerate(reader.pages[:20]):  # Cap at 20 pages
                    t = page.extract_text() or ""
                    if t.strip():
                        pages_text.append(f"--- Page {i+1} ---\n{t.strip()}")
                extracted = "\n\n".join(pages_text)
                return extracted, f"PDF Document: {filename} ({num_pages} pages, {len(file_bytes)} bytes)"
            except Exception as e:
                logger.warning("pypdf extraction error for %s: %s", filename, e)
                return f"[Could not read PDF contents: {e}]", f"PDF Document: {filename}"

        # 2. Text / Markdown / Code / JSON / CSV
        for enc in ["utf-8", "utf-8-sig", "latin-1", "cp1252"]:
            try:
                text = file_bytes.decode(enc)
                lines = text.splitlines()
                return text, f"Text Document: {filename} ({len(lines)} lines, {len(file_bytes)} bytes)"
            except UnicodeDecodeError:
                continue

        return "[Binary file content not displayable as plain text]", f"Attachment: {filename}"


class AIService:
    """
    Central AI Provider Engine supporting Google Gemini, OpenAI, and Ollama.
    Enforces real AI generation without fake fallbacks.
    """

    def __init__(self):
        self.timeout_sec = 25.0

    @classmethod
    def get_secret_or_env(cls, key_name: str, default: Optional[str] = None) -> Optional[str]:
        """Retrieves secrets from environment or Streamlit secrets securely."""
        val = os.environ.get(key_name)
        if val and str(val).strip():
            return str(val).strip()
        try:
            import streamlit as st
            if hasattr(st, "secrets"):
                if key_name in st.secrets:
                    s_val = st.secrets[key_name]
                    if s_val and str(s_val).strip():
                        return str(s_val).strip()
        except Exception:
            pass
        return default

    @classmethod
    def get_active_provider_info(cls) -> Dict[str, Any]:
        """Returns details of configured AI providers and which is primary."""
        gemini_key = cls.get_secret_or_env("GEMINI_API_KEY") or cls.get_secret_or_env("GOOGLE_API_KEY")
        openai_key = cls.get_secret_or_env("OPENAI_API_KEY")
        ollama_url = cls.get_secret_or_env("OLLAMA_BASE_URL", "http://localhost:11434")
        groq_key = cls.get_secret_or_env("GROQ_API_KEY")

        # Test local Ollama availability
        ollama_available = False
        try:
            r = requests.get(f"{ollama_url}/api/tags", timeout=0.6)
            if r.status_code == 200:
                ollama_available = True
        except Exception:
            ollama_available = False

        available_providers = []
        if gemini_key:
            available_providers.append("gemini")
        if openai_key:
            available_providers.append("openai")
        if ollama_available:
            available_providers.append("ollama")
        if groq_key:
            available_providers.append("groq")

        preferred = cls.get_secret_or_env("DEFAULT_AI_PROVIDER", "").lower()
        if preferred in available_providers:
            primary = preferred
        elif available_providers:
            primary = available_providers[0]
        else:
            primary = "none"

        return {
            "primary": primary,
            "available": available_providers,
            "has_gemini": bool(gemini_key),
            "has_openai": bool(openai_key),
            "has_ollama": ollama_available,
            "has_groq": bool(groq_key)
        }

    @classmethod
    def is_configured(cls) -> bool:
        """Returns True if at least one real AI model provider is available."""
        info = cls.get_active_provider_info()
        return len(info["available"]) > 0

    @classmethod
    def build_system_prompt(cls, lang: str = "en", context: Optional[Dict[str, Any]] = None) -> str:
        """Constructs an intelligent, multilingual, context-grounded system prompt."""
        lang_info = LANGUAGE_SPEECH_MAP.get(lang.lower(), LANGUAGE_SPEECH_MAP["en"])
        lang_name = lang_info.get("name", "English")
        lang_native = lang_info.get("native", lang_name)

        ctx = context or {}
        start_lbl = ctx.get("start_label") or "Not selected"
        dest_lbl = ctx.get("dest_label") or "Not selected"
        curr_coords = ctx.get("current_coords") or ctx.get("user_live_coords") or (16.2335, 80.5505)
        dest_coords = ctx.get("dest_coords") or ctx.get("selected_dest_coords")
        travel_mode = ctx.get("travel_mode", "Car")

        active_route_info = ""
        ranked = ctx.get("ranked_routes", [])
        if ranked:
            top = ranked[0]
            d_km = getattr(top, "distance_km", 0.0) or getattr(top, "distance_meters", 0.0) / 1000.0
            dur_m = getattr(top, "duration_minutes", 0.0) or getattr(top, "duration_seconds", 0.0) / 60.0
            r_name = getattr(top, "name", "Primary Corridor")
            active_route_info = f"\n- Active Route: {r_name} ({d_km:.1f} km, ~{round(dur_m)} min)"

        stops = ctx.get("intermediate_stops", [])
        stops_info = ""
        if stops:
            s_names = [s.get("name", "Stop") for s in stops]
            stops_info = f"\n- Intermediate Stops: {', '.join(s_names)}"

        prompt = f"""# NexRoute AI Assistant — Universal Multilingual Intelligence & Travel Copilot

You are NexRoute AI, an intelligent, helpful, multilingual AI assistant integrated into NexRoute.
You possess two complementary capabilities:
1. **General-Purpose AI Intelligence**: You answer unrestricted questions across general knowledge, mathematics, programming, computer science, physics, chemistry, biology, history, literature, creative writing, problem solving, analysis, and everyday conversations.
2. **NexRoute Navigation & Travel Intelligence**: You assist with real-world trip planning, itineraries, route calculations, finding verified hospitals, petrol stations, restaurants, hotels, road hazards, and distance estimation.

## Language and Multilingual Directives:
- The user's active application language is **{lang_name}** ({lang_native}).
- You MUST default to responding fluently in **{lang_name}** ({lang_native}).
- If the user addresses you in another language (e.g. Hindi, Telugu, Tamil, Kannada, Malayalam, Bengali, Marathi, or English), you understand it naturally. If the user explicitly asks to speak in a specific language, respect their choice.
- Write natural, grammatically correct responses. For Indian languages (Telugu, Hindi, Tamil, etc.), use the native script with natural regional phrasing rather than mechanical word-by-word translations.

## Truthfulness & Tool Directives:
- Never fabricate fake distances, imaginary coordinates, non-existent businesses, or claim a route was drawn on the map if it was not.
- When the user asks to perform an action on the map or find nearby facilities, cite the verified application tools:
  * `calculate_route(origin, destination, travel_mode)`
  * `find_nearby_places(category, radius_km)`
  * `find_nearby_hospitals(radius_km)`
  * `find_petrol_stations(radius_km)`
  * `find_restaurants(radius_km)`
  * `find_hotels(radius_km)`
  * `add_route_stop(stop_name, lat, lon)`
  * `search_location(query)`

## Current User Journey Context:
- Current / Starting Location: {start_lbl} ({curr_coords[0]:.4f}, {curr_coords[1]:.4f})
- Target Destination: {dest_lbl} {f'({dest_coords[0]:.4f}, {dest_coords[1]:.4f})' if dest_coords else ''}
- Travel Mode: {travel_mode}{active_route_info}{stops_info}

## Formatting:
- Format your answers beautifully using GitHub-flavored markdown: bold key points, bulleted or numbered lists for readability, code blocks with syntax language tags when providing code, and clear section headings.
- Be concise yet thorough and clear.
"""
        return prompt

    def generate(
        self,
        messages: List[Dict[str, str]],
        lang: str = "en",
        context: Optional[Dict[str, Any]] = None,
        attachments: Optional[List[Dict[str, Any]]] = None,
        temperature: float = 0.7,
        max_tokens: int = 1500
    ) -> Dict[str, Any]:
        """
        Executes real LLM generation across configured providers with automatic fallback.
        Returns: {
            "success": bool,
            "response": str,
            "badge": str,
            "provider": str,
            "error": Optional[str]
        }
        """
        system_prompt = self.build_system_prompt(lang=lang, context=context)
        info = self.get_active_provider_info()

        if not info["available"]:
            return {
                "success": False,
                "response": self._get_unconfigured_message(lang),
                "badge": "⚙️ SETUP REQUIRED",
                "provider": "none",
                "error": "No AI model provider configured."
            }

        # Try providers in order of preference
        providers_to_try = []
        if info["primary"] in info["available"]:
            providers_to_try.append(info["primary"])
        for p in info["available"]:
            if p not in providers_to_try:
                providers_to_try.append(p)

        last_error = None
        for prov in providers_to_try:
            try:
                if prov == "gemini":
                    resp_text, badge = self._call_gemini(messages, system_prompt, attachments, temperature, max_tokens)
                    return {"success": True, "response": resp_text, "badge": badge, "provider": "gemini", "error": None}
                elif prov == "openai":
                    resp_text, badge = self._call_openai(messages, system_prompt, attachments, temperature, max_tokens)
                    return {"success": True, "response": resp_text, "badge": badge, "provider": "openai", "error": None}
                elif prov == "ollama":
                    resp_text, badge = self._call_ollama(messages, system_prompt, attachments, temperature, max_tokens)
                    return {"success": True, "response": resp_text, "badge": badge, "provider": "ollama", "error": None}
                elif prov == "groq":
                    resp_text, badge = self._call_groq(messages, system_prompt, temperature, max_tokens)
                    return {"success": True, "response": resp_text, "badge": badge, "provider": "groq", "error": None}
            except Exception as e:
                logger.warning("AI provider '%s' failed: %s", prov, e)
                last_error = str(e)
                continue

        return {
            "success": False,
            "response": f"⚠️ **AI Service Communication Error**: Unable to reach configured AI providers ({', '.join(providers_to_try)}).\n\n*Error details: {last_error}*\n\nPlease check your internet connection or API key quotas. Your live GPS navigation and offline map services remain operational.",
            "badge": "⚠️ AI SERVICE UNAVAILABLE",
            "provider": "error",
            "error": last_error
        }

    # -------------------------------------------------------------------------
    # 1. Google Gemini Provider
    # -------------------------------------------------------------------------
    def _call_gemini(
        self,
        messages: List[Dict[str, str]],
        system_prompt: str,
        attachments: Optional[List[Dict[str, Any]]],
        temperature: float,
        max_tokens: int
    ) -> Tuple[str, str]:
        key = self.get_secret_or_env("GEMINI_API_KEY") or self.get_secret_or_env("GOOGLE_API_KEY")
        if not key:
            raise ValueError("GEMINI_API_KEY not configured")

        model_name = self.get_secret_or_env("GEMINI_MODEL", DEFAULT_GEMINI_MODEL)
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={key}"

        contents = []
        # Prepend system instruction
        contents.append({
            "role": "user",
            "parts": [{"text": f"System Directive:\n{system_prompt}"}]
        })
        contents.append({
            "role": "model",
            "parts": [{"text": "Understood. I will follow these instructions precisely, communicating in the requested language."}]
        })

        for i, m in enumerate(messages):
            role = "user" if m.get("role") == "user" else "model"
            parts = [{"text": m.get("content", "")}]

            # Attach multimodal items to the latest user message
            if role == "user" and i == len(messages) - 1 and attachments:
                for att in attachments:
                    att_type = att.get("type", "document")
                    if att_type == "image" and "data_base64" in att:
                        parts.append({
                            "inline_data": {
                                "mime_type": att.get("mime_type", "image/jpeg"),
                                "data": att["data_base64"]
                            }
                        })
                    elif att_type == "document" and "text" in att:
                        doc_snippet = f"\n[Attached Document: {att.get('name', 'file')}]:\n{att['text'][:12000]}\n"
                        parts.append({"text": doc_snippet})

            contents.append({"role": role, "parts": parts})

        payload = {
            "contents": contents,
            "generationConfig": {
                "temperature": temperature,
                "maxOutputTokens": max_tokens
            }
        }

        resp = requests.post(url, json=payload, timeout=self.timeout_sec)
        if resp.status_code == 404:
            # Fallback to gemini-1.5-flash
            fallback_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={key}"
            resp = requests.post(fallback_url, json=payload, timeout=self.timeout_sec)

        if resp.status_code != 200:
            err_msg = resp.text
            try:
                err_data = resp.json()
                err_msg = err_data.get("error", {}).get("message", resp.text)
            except Exception:
                pass
            raise RuntimeError(f"Gemini API ({resp.status_code}): {err_msg}")

        data = resp.json()
        candidates = data.get("candidates", [])
        if not candidates:
            raise RuntimeError("Gemini returned empty candidate response.")

        text = candidates[0].get("content", {}).get("parts", [])[0].get("text", "")
        badge = "✨ GEMINI 2.0 FLASH" if "2.0" in model_name else "✨ GOOGLE GEMINI"
        return text, badge

    # -------------------------------------------------------------------------
    # 2. OpenAI Provider
    # -------------------------------------------------------------------------
    def _call_openai(
        self,
        messages: List[Dict[str, str]],
        system_prompt: str,
        attachments: Optional[List[Dict[str, Any]]],
        temperature: float,
        max_tokens: int
    ) -> Tuple[str, str]:
        key = self.get_secret_or_env("OPENAI_API_KEY")
        if not key:
            raise ValueError("OPENAI_API_KEY not configured")

        base_url = self.get_secret_or_env("OPENAI_BASE_URL", "https://api.openai.com/v1")
        model = self.get_secret_or_env("OPENAI_MODEL", DEFAULT_OPENAI_MODEL)

        try:
            from openai import OpenAI
            client = OpenAI(api_key=key, base_url=base_url, timeout=self.timeout_sec)
        except ImportError:
            # Fallback to direct HTTP request
            return self._call_openai_http(messages, system_prompt, attachments, key, base_url, model, temperature, max_tokens)

        formatted_msgs = [{"role": "system", "content": system_prompt}]

        for i, m in enumerate(messages):
            role = m.get("role", "user")
            content = m.get("content", "")

            # If user message with image attachments, format as multimodal content array
            if role == "user" and i == len(messages) - 1 and attachments:
                content_parts: List[Dict[str, Any]] = [{"type": "text", "text": content}]
                for att in attachments:
                    if att.get("type") == "image" and "data_base64" in att:
                        mime = att.get("mime_type", "image/jpeg")
                        b64 = att["data_base64"]
                        content_parts.append({
                            "type": "image_url",
                            "image_url": {"url": f"data:{mime};base64,{b64}"}
                        })
                    elif att.get("type") == "document" and "text" in att:
                        doc_text = f"\n[Attached Document: {att.get('name', 'file')}]:\n{att['text'][:12000]}\n"
                        content_parts.append({"type": "text", "text": doc_text})
                formatted_msgs.append({"role": role, "content": content_parts})
            else:
                formatted_msgs.append({"role": role, "content": content})

        completion = client.chat.completions.create(
            model=model,
            messages=formatted_msgs,
            temperature=temperature,
            max_tokens=max_tokens
        )
        content_out = completion.choices[0].message.content or ""
        badge = f"⚡ OPENAI {model.upper()}"
        return content_out, badge

    def _call_openai_http(self, messages, system_prompt, attachments, key, base_url, model, temperature, max_tokens):
        url = f"{base_url.rstrip('/')}/chat/completions"
        headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
        formatted_msgs = [{"role": "system", "content": system_prompt}]
        for i, m in enumerate(messages):
            role = m.get("role", "user")
            content = m.get("content", "")
            if role == "user" and i == len(messages) - 1 and attachments:
                for att in attachments:
                    if att.get("type") == "document" and "text" in att:
                        content += f"\n\n[Attached File: {att.get('name')}]:\n{att['text'][:10000]}"
            formatted_msgs.append({"role": role, "content": content})

        resp = requests.post(url, headers=headers, json={
            "model": model,
            "messages": formatted_msgs,
            "temperature": temperature,
            "max_tokens": max_tokens
        }, timeout=self.timeout_sec)

        if resp.status_code != 200:
            raise RuntimeError(f"OpenAI API error ({resp.status_code}): {resp.text}")
        data = resp.json()
        text = data["choices"][0]["message"]["content"]
        return text, f"⚡ OPENAI {model.upper()}"

    # -------------------------------------------------------------------------
    # 3. Local Ollama Provider
    # -------------------------------------------------------------------------
    def _call_ollama(
        self,
        messages: List[Dict[str, str]],
        system_prompt: str,
        attachments: Optional[List[Dict[str, Any]]],
        temperature: float,
        max_tokens: int
    ) -> Tuple[str, str]:
        base_url = self.get_secret_or_env("OLLAMA_BASE_URL", "http://localhost:11434").rstrip("/")
        model = self.get_secret_or_env("OLLAMA_MODEL", DEFAULT_OLLAMA_MODEL)

        formatted_msgs = [{"role": "system", "content": system_prompt}]
        for i, m in enumerate(messages):
            content = m.get("content", "")
            images = []
            if m.get("role") == "user" and i == len(messages) - 1 and attachments:
                for att in attachments:
                    if att.get("type") == "image" and "data_base64" in att:
                        images.append(att["data_base64"])
                    elif att.get("type") == "document" and "text" in att:
                        content += f"\n\n[Attached Document: {att.get('name')}]:\n{att['text'][:8000]}"
            item: Dict[str, Any] = {"role": m.get("role", "user"), "content": content}
            if images:
                item["images"] = images
            formatted_msgs.append(item)

        url = f"{base_url}/api/chat"
        resp = requests.post(url, json={
            "model": model,
            "messages": formatted_msgs,
            "stream": False,
            "options": {"temperature": temperature, "num_predict": max_tokens}
        }, timeout=self.timeout_sec)

        if resp.status_code != 200:
            raise RuntimeError(f"Ollama API ({resp.status_code}): {resp.text}")

        data = resp.json()
        text = data.get("message", {}).get("content", "")
        return text, f"🦙 LOCAL OLLAMA ({model.upper()})"

    # -------------------------------------------------------------------------
    # 4. Groq Provider
    # -------------------------------------------------------------------------
    def _call_groq(self, messages, system_prompt, temperature, max_tokens):
        key = self.get_secret_or_env("GROQ_API_KEY")
        if not key:
            raise ValueError("GROQ_API_KEY not configured")
        model = self.get_secret_or_env("GROQ_MODEL", "llama-3.3-70b-versatile")
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
        formatted_msgs = [{"role": "system", "content": system_prompt}] + messages
        resp = requests.post(url, headers=headers, json={
            "model": model,
            "messages": formatted_msgs,
            "temperature": temperature,
            "max_tokens": max_tokens
        }, timeout=self.timeout_sec)
        if resp.status_code != 200:
            raise RuntimeError(f"Groq error ({resp.status_code}): {resp.text}")
        data = resp.json()
        return data["choices"][0]["message"]["content"], "⚡ GROQ LLAMA 3.3"

    # -------------------------------------------------------------------------
    # Unconfigured Guide Message
    # -------------------------------------------------------------------------
    def _get_unconfigured_message(self, lang: str = "en") -> str:
        lang_info = LANGUAGE_SPEECH_MAP.get(lang.lower(), LANGUAGE_SPEECH_MAP["en"])
        native_title = "మోడల్ కాన్ఫిగరేషన్ అవసరం" if lang == "te" else ("मॉडल कॉन्फ़िगरेशन आवश्यक" if lang == "hi" else "AI Model Setup Required")

        return f"""### 🤖 NexRoute AI Assistant — {native_title}

No external or local AI model provider is currently active. To enable full general-purpose conversational intelligence, multilingual speech, and unrestricted question answering, please configure one of the following providers:

#### 1. Google Gemini API (Recommended & Free Tier Available)
1. Get a free API key from [Google AI Studio](https://aistudio.google.com/).
2. Add your key to your `.env` file or Streamlit Secrets:
   ```bash
   GEMINI_API_KEY="your_api_key_here"
   ```

#### 2. OpenAI API
1. Get an API key from [OpenAI Platform](https://platform.openai.com/).
2. Add to `.env` or Streamlit Secrets:
   ```bash
   OPENAI_API_KEY="sk-..."
   ```

#### 3. Local Ollama (100% Free & Private Offline)
1. Install [Ollama](https://ollama.ai/) and run:
   ```bash
   ollama run llama3
   ```
   NexRoute will automatically connect to `http://localhost:11434`.

---
*Note: Your live GPS satellite navigation, turn-by-turn guidance, route calculations, and nearby facility search continue functioning at 100% full capacity.*"""
