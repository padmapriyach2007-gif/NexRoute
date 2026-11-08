"""
AURA Chat Storage & Conversation Management Engine
Provides persistent, multi-conversation ChatGPT-like history management:
- Persistent JSON file storage at data/aura_conversations.json
- Multi-conversation lifecycle (create, load, switch, rename, delete)
- Search across titles and message contents
- Automatic conversation title generation from initial user queries
- Crash resilience, thread-safe file operations, and page-refresh persistence
"""

import os
import json
import uuid
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path

logger = logging.getLogger("nexroute.aura_chat_store")

ROOT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT_DIR / "data"
STORAGE_FILE = DATA_DIR / "aura_conversations.json"


def _ensure_data_dir():
    try:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        logger.warning("Could not ensure data directory exists: %s", e)


def _generate_conv_title(first_user_message: str) -> str:
    """Generates a concise, readable conversation title from the first query."""
    if not first_user_message:
        return "New Trip Chat"
    clean = first_user_message.strip().replace("\n", " ")
    for prefix in ["plan a trip to ", "how to reach ", "route to ", "guide for ", "tell me about "]:
        if clean.lower().startswith(prefix):
            clean = clean[len(prefix):].capitalize()
            break
    if len(clean) > 36:
        clean = clean[:33].rstrip() + "..."
    return clean or "New Trip Chat"


class AuraConversationStore:
    """Manages persistent AURA chat sessions and conversations."""

    @staticmethod
    def load_store() -> Dict[str, Any]:
        """Loads all conversations from the persistent storage file."""
        _ensure_data_dir()
        if not STORAGE_FILE.exists():
            return {"conversations": {}, "active_conv_id": None}
        try:
            with open(STORAGE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, dict) and "conversations" in data:
                    return data
        except Exception as err:
            logger.error("Failed to load conversations store: %s", err)
        return {"conversations": {}, "active_conv_id": None}

    @staticmethod
    def save_store(store_data: Dict[str, Any]) -> bool:
        """Saves conversations data to disk atomically."""
        _ensure_data_dir()
        tmp_file = STORAGE_FILE.with_suffix(".tmp")
        try:
            with open(tmp_file, "w", encoding="utf-8") as f:
                json.dump(store_data, f, ensure_ascii=False, indent=2)
            tmp_file.replace(STORAGE_FILE)
            return True
        except Exception as err:
            logger.error("Failed to save conversations store: %s", err)
            try:
                if tmp_file.exists():
                    tmp_file.unlink()
            except Exception:
                pass
            return False

    @classmethod
    def list_conversations(cls, search_query: str = "") -> List[Dict[str, Any]]:
        """Returns sorted conversations (most recently updated first), optionally filtered by search."""
        store = cls.load_store()
        convs = list(store.get("conversations", {}).values())

        if search_query and search_query.strip():
            sq = search_query.strip().lower()
            filtered = []
            for c in convs:
                title_match = sq in c.get("title", "").lower()
                body_match = any(sq in m.get("content", "").lower() for m in c.get("messages", []))
                if title_match or body_match:
                    filtered.append(c)
            convs = filtered

        convs.sort(key=lambda x: x.get("updated_at", ""), reverse=True)
        return convs

    @classmethod
    def get_conversation(cls, conv_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves a single conversation by ID."""
        store = cls.load_store()
        return store.get("conversations", {}).get(conv_id)

    @classmethod
    def create_conversation(cls, initial_messages: Optional[List[Dict[str, Any]]] = None, title: Optional[str] = None) -> str:
        """Creates a new conversation and sets it as active."""
        store = cls.load_store()
        conv_id = f"conv_{int(datetime.now().timestamp())}_{uuid.uuid4().hex[:6]}"
        now_iso = datetime.now().isoformat()

        init_msgs = initial_messages or []
        conv_title = title or "New Trip Chat"

        # If initial messages contain user message, derive title
        if not title:
            for m in init_msgs:
                if m.get("role") == "user":
                    conv_title = _generate_conv_title(m.get("content", ""))
                    break

        new_conv = {
            "id": conv_id,
            "title": conv_title,
            "created_at": now_iso,
            "updated_at": now_iso,
            "messages": init_msgs
        }

        store.setdefault("conversations", {})[conv_id] = new_conv
        store["active_conv_id"] = conv_id
        cls.save_store(store)
        return conv_id

    @classmethod
    def update_messages(cls, conv_id: str, messages: List[Dict[str, Any]]) -> bool:
        """Updates the messages for a conversation and auto-titles if needed."""
        store = cls.load_store()
        conv = store.get("conversations", {}).get(conv_id)
        now_iso = datetime.now().isoformat()

        if not conv:
            # Create if it didn't exist
            conv = {
                "id": conv_id,
                "title": "New Trip Chat",
                "created_at": now_iso,
                "updated_at": now_iso,
                "messages": []
            }
            store.setdefault("conversations", {})[conv_id] = conv

        conv["messages"] = messages
        conv["updated_at"] = now_iso

        # Auto-update title if it's currently generic
        if conv.get("title") in ["New Trip Chat", "New Conversation", "AURA Chat", None]:
            for m in messages:
                if m.get("role") == "user":
                    conv["title"] = _generate_conv_title(m.get("content", ""))
                    break

        store["active_conv_id"] = conv_id
        return cls.save_store(store)

    @classmethod
    def rename_conversation(cls, conv_id: str, new_title: str) -> bool:
        """Renames an existing conversation."""
        store = cls.load_store()
        if conv_id in store.get("conversations", {}):
            store["conversations"][conv_id]["title"] = new_title.strip() or "Untitled Chat"
            store["conversations"][conv_id]["updated_at"] = datetime.now().isoformat()
            return cls.save_store(store)
        return False

    @classmethod
    def delete_conversation(cls, conv_id: str) -> bool:
        """Deletes a conversation from storage."""
        store = cls.load_store()
        if conv_id in store.get("conversations", {}):
            del store["conversations"][conv_id]
            if store.get("active_conv_id") == conv_id:
                remaining = list(store.get("conversations", {}).keys())
                store["active_conv_id"] = remaining[0] if remaining else None
            return cls.save_store(store)
        return False

    @classmethod
    def get_or_create_active_id(cls, default_messages: Optional[List[Dict[str, Any]]] = None) -> str:
        """Returns the current active conversation ID or creates one."""
        store = cls.load_store()
        active_id = store.get("active_conv_id")
        if active_id and active_id in store.get("conversations", {}):
            return active_id
        convs = list(store.get("conversations", {}).values())
        if convs:
            convs.sort(key=lambda x: x.get("updated_at", ""), reverse=True)
            store["active_conv_id"] = convs[0]["id"]
            cls.save_store(store)
            return convs[0]["id"]
        return cls.create_conversation(initial_messages=default_messages)

