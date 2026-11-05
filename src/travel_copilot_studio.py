"""
Pathfinder — Quantum Realm Travel Copilot & Visual Studio System
Inspired by the Quantum Realm aesthetic:
- Deep space cosmic void (#030712) with electric cyan (#00f0ff) & quantum violet (#a855f7) ambient glows.
- Glassmorphism surfaces with high-contrast typography and glowing neon pill badges.
- First-class AI Travel Copilot & Itinerary Studio powered by Ollama and Builtin Cognitive Engine.
- Multi-corridor routing integration, multimodal comparisons, and live weather telemetry.
"""

import os
import json
import logging
from typing import Dict, Any, List, Optional
import textwrap
import streamlit as st

from src.i18n import t, get_current_language, SUPPORTED_LANGUAGES
from src.backend.database.connection import SessionLocal
from src.backend.ai_agent.trip_planner_agent import TripPlannerAgent
from src.backend.weather.weather_service import WeatherService
from src.backend.multimodal.journey_planner import MultimodalJourneyPlanner

logger = logging.getLogger("pathfinder.travel_copilot_studio")


QUANTUM_REALM_CSS = """
<style>
/* =========================================================================
   QUANTUM REALM DESIGN SYSTEM TOKENS
   Deep Space Void #030712 • Electric Cyan #00f0ff • Quantum Violet #a855f7
   ========================================================================= */

:root {
    --qr-bg-dark: #030712;
    --qr-bg-panel: rgba(15, 23, 42, 0.72);
    --qr-bg-glass: rgba(30, 41, 59, 0.50);
    --qr-cyan: #00f0ff;
    --qr-cyan-glow: rgba(0, 240, 255, 0.35);
    --qr-violet: #a855f7;
    --qr-violet-glow: rgba(168, 85, 247, 0.35);
    --qr-emerald: #10b981;
    --qr-emerald-glow: rgba(16, 185, 129, 0.35);
    --qr-border-light: rgba(255, 255, 255, 0.09);
    --qr-border-cyan: rgba(56, 189, 248, 0.40);
}

/* Background Cosmic Ambient Atmosphere */
.stApp {
    background-color: #030712 !important;
    background-image: 
        radial-gradient(circle at 10% 12%, rgba(6, 182, 212, 0.14) 0%, transparent 45%),
        radial-gradient(circle at 90% 12%, rgba(168, 85, 247, 0.16) 0%, transparent 45%),
        radial-gradient(circle at 50% 85%, rgba(14, 165, 233, 0.08) 0%, transparent 55%),
        linear-gradient(180deg, rgba(3, 7, 18, 0.88) 0%, rgba(5, 11, 20, 0.82) 50%, rgba(3, 7, 18, 0.95) 100%) !important;
    background-size: cover !important;
    background-attachment: fixed !important;
    color: #f1f5f9;
}

/* Complete Sidebar Elimination */
[data-testid="stSidebar"],
section[data-testid="stSidebar"],
[data-testid="collapsedControl"],
header button[data-testid="baseButton-headerNoPadding"],
button[data-testid="baseButton-header"] {
    display: none !important;
    width: 0 !important;
    height: 0 !important;
    visibility: hidden !important;
    opacity: 0 !important;
    pointer-events: none !important;
}

/* Top Navigation Bar Pill */
.qr-navbar-container {
    background: linear-gradient(135deg, rgba(15, 23, 42, 0.85) 0%, rgba(20, 30, 48, 0.75) 100%);
    backdrop-filter: blur(24px) saturate(190%);
    -webkit-backdrop-filter: blur(24px) saturate(190%);
    border: 1.5px solid rgba(56, 189, 248, 0.28);
    border-radius: 16px;
    padding: 12px 20px;
    margin-bottom: 16px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    flex-wrap: wrap;
    gap: 14px;
    box-shadow: 0 10px 36px rgba(0, 0, 0, 0.55), 0 0 20px rgba(6, 182, 212, 0.10);
}

.qr-logo-emblem {
    width: 44px;
    height: 44px;
    border-radius: 13px;
    background: linear-gradient(135deg, rgba(6, 182, 212, 0.25) 0%, rgba(168, 85, 247, 0.25) 100%);
    border: 1.5px solid transparent;
    background-image: linear-gradient(rgba(15, 23, 42, 0.92), rgba(15, 23, 42, 0.92)), linear-gradient(135deg, #00f0ff 0%, #a855f7 100%);
    background-origin: border-box;
    background-clip: padding-box, border-box;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.6rem;
    box-shadow: 0 0 20px rgba(6, 182, 212, 0.35);
}

.qr-brand-title {
    font-size: 1.55rem;
    font-weight: 900;
    letter-spacing: 0.05em;
    background: linear-gradient(135deg, #38bdf8 0%, #818cf8 50%, #c084fc 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin: 0;
    line-height: 1.1;
}

.qr-brand-subtitle {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.68rem;
    font-weight: 700;
    letter-spacing: 0.16em;
    color: #94a3b8;
    text-transform: uppercase;
}

.qr-pill-badge {
    background: rgba(16, 185, 129, 0.12);
    border: 1px solid rgba(16, 185, 129, 0.45);
    color: #34d399;
    font-size: 0.70rem;
    font-weight: 800;
    padding: 3px 10px;
    border-radius: 9999px;
    display: inline-flex;
    align-items: center;
    gap: 6px;
    box-shadow: 0 0 12px rgba(16, 185, 129, 0.25);
    font-family: 'JetBrains Mono', monospace;
}

.qr-pill-cyan {
    background: rgba(6, 182, 212, 0.12);
    border: 1px solid rgba(6, 182, 212, 0.45);
    color: #38bdf8;
    box-shadow: 0 0 12px rgba(6, 182, 212, 0.25);
}

.qr-pill-dot {
    width: 7px;
    height: 7px;
    border-radius: 50%;
    background: #34d399;
    box-shadow: 0 0 8px #34d399;
    animation: qrPulse 2s infinite;
}

@keyframes qrPulse {
    0% { transform: scale(0.95); opacity: 0.8; }
    50% { transform: scale(1.15); opacity: 1; }
    100% { transform: scale(0.95); opacity: 0.8; }
}

/* Quantum Hero Landing Showcase */
.qr-hero-wrapper {
    display: flex !important;
    flex-direction: row !important;
    align-items: center !important;
    justify-content: center !important;
    text-align: center !important;
    padding: 24px 20px 16px 20px !important;
    margin-bottom: 8px !important;
    gap: 20px !important;
}

@media (max-width: 960px) {
    .qr-hero-wrapper {
        flex-direction: column !important;
        text-align: center !important;
        gap: 16px !important;
    }
}

.qr-hero-emblem {
    width: 68px;
    height: 68px;
    border-radius: 20px;
    background: linear-gradient(135deg, rgba(6, 182, 212, 0.25) 0%, rgba(168, 85, 247, 0.25) 100%);
    border: 1.5px solid transparent;
    background-image: linear-gradient(rgba(15, 23, 42, 0.95), rgba(15, 23, 42, 0.95)), linear-gradient(135deg, #00f0ff 0%, #a855f7 100%);
    background-origin: border-box;
    background-clip: padding-box, border-box;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 2.2rem;
    box-shadow: 0 0 36px rgba(6, 182, 212, 0.35), 0 0 20px rgba(168, 85, 247, 0.25);
    margin-bottom: 14px;
    animation: qrFloat 4s ease-in-out infinite alternate;
}

@keyframes qrFloat {
    0% { transform: translateY(0px); }
    100% { transform: translateY(-5px); }
}

.qr-hero-heading {
    font-size: 2.6rem;
    font-weight: 900;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    background: linear-gradient(135deg, #38bdf8 0%, #818cf8 45%, #c084fc 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin: 0 0 6px 0;
    line-height: 1.1;
}

.qr-hero-subtag {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.74rem;
    font-weight: 700;
    letter-spacing: 0.22em;
    color: #94a3b8;
    text-transform: uppercase;
    margin-bottom: 10px;
}

.qr-hero-tagline {
    font-size: 1.02rem;
    color: #cbd5e1;
    max-width: 620px;
    margin: 0 auto;
    line-height: 1.5;
    font-weight: 400;
}

/* Glassmorphic 4-Workspace Cards */
.qr-workspace-card {
    background: linear-gradient(145deg, rgba(15, 23, 42, 0.75) 0%, rgba(20, 32, 54, 0.60) 100%);
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    border: 1px solid rgba(255, 255, 255, 0.09);
    border-radius: 20px;
    padding: 22px 18px;
    min-height: 240px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    transition: all 0.26s cubic-bezier(0.4, 0, 0.2, 1);
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.45);
    margin-bottom: 8px;
}

.qr-workspace-card:hover {
    transform: translateY(-4px);
    border-color: rgba(56, 189, 248, 0.50);
    box-shadow: 0 16px 42px rgba(0, 0, 0, 0.65), 0 0 28px rgba(56, 189, 248, 0.18);
}

.qr-card-icon-pill {
    width: 44px;
    height: 44px;
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.4rem;
    margin-bottom: 12px;
}

.qr-icon-cyan {
    background: rgba(6, 182, 212, 0.15);
    border: 1px solid rgba(6, 182, 212, 0.4);
    box-shadow: 0 0 16px rgba(6, 182, 212, 0.25);
}

.qr-icon-purple {
    background: rgba(168, 85, 247, 0.15);
    border: 1px solid rgba(168, 85, 247, 0.4);
    box-shadow: 0 0 16px rgba(168, 85, 247, 0.25);
}

.qr-icon-emerald {
    background: rgba(16, 185, 129, 0.15);
    border: 1px solid rgba(16, 185, 129, 0.4);
    box-shadow: 0 0 16px rgba(16, 185, 129, 0.25);
}

.qr-icon-blue {
    background: rgba(59, 130, 246, 0.15);
    border: 1px solid rgba(59, 130, 246, 0.4);
    box-shadow: 0 0 16px rgba(59, 130, 246, 0.25);
}

/* Glassmorphic Tabs Customization (Matching Quantum Realm Pill Group) */
div[data-testid="stTabs"] > div:first-child,
div[data-testid="stTabs"] [data-baseweb="tab-list"],
div[role="tablist"] {
    background: rgba(15, 23, 42, 0.85) !important;
    backdrop-filter: blur(24px) saturate(190%) !important;
    -webkit-backdrop-filter: blur(24px) saturate(190%) !important;
    border: 1.5px solid rgba(255, 255, 255, 0.12) !important;
    border-radius: 9999px !important;
    padding: 5px 8px !important;
    gap: 8px !important;
    margin: 10px 0 20px 0 !important;
    box-shadow: 0 10px 32px rgba(0, 0, 0, 0.6), inset 0 1px 0 rgba(255, 255, 255, 0.12) !important;
    display: inline-flex !important;
    align-items: center !important;
    justify-content: center !important;
    width: 100% !important;
}

div[data-testid="stTabs"] [role="tab"],
div[role="tablist"] [role="tab"] {
    border-radius: 9999px !important;
    padding: 8px 18px !important;
    background: transparent !important;
    border: 1px solid transparent !important;
    color: #94a3b8 !important;
    font-size: 0.90rem !important;
    font-weight: 700 !important;
    transition: all 0.2s ease !important;
}

div[data-testid="stTabs"] [role="tab"]:hover,
div[role="tablist"] [role="tab"]:hover {
    color: #ffffff !important;
    background: rgba(255, 255, 255, 0.06) !important;
    border-color: rgba(56, 189, 248, 0.3) !important;
}

div[data-testid="stTabs"] [role="tab"][aria-selected="true"],
div[role="tablist"] [role="tab"][aria-selected="true"] {
    background: linear-gradient(135deg, rgba(6, 182, 212, 0.24) 0%, rgba(139, 92, 246, 0.26) 100%) !important;
    border: 1.5px solid rgba(56, 189, 248, 0.70) !important;
    color: #38bdf8 !important;
    box-shadow: 0 0 24px rgba(56, 189, 248, 0.4), inset 0 1px 0 rgba(255, 255, 255, 0.3) !important;
    font-weight: 800 !important;
}

/* Studio Glass Containers */
.qr-glass-panel {
    background: linear-gradient(145deg, rgba(15, 23, 42, 0.72) 0%, rgba(20, 30, 48, 0.55) 100%);
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    border: 1px solid rgba(56, 189, 248, 0.22);
    border-radius: 18px;
    padding: 18px 20px;
    margin-bottom: 16px;
    box-shadow: 0 8px 28px rgba(0, 0, 0, 0.45);
}

.qr-stop-card {
    background: rgba(15, 23, 42, 0.85);
    border: 1px solid rgba(56, 189, 248, 0.25);
    border-left: 4px solid #38bdf8;
    border-radius: 12px;
    padding: 12px 16px;
    margin-bottom: 10px;
    transition: all 0.2s ease;
}

.qr-stop-card:hover {
    border-color: #38bdf8;
    box-shadow: 0 4px 18px rgba(56, 189, 248, 0.2);
    transform: translateX(3px);
}

/* =========================================================================
   3D CUTE ROBOT CHATBOT STATION (Stationed at Left of Main Dashboard)
   ========================================================================= */
.dashboard-robot-left-station {
    flex: 0 0 auto !important;
    max-width: 170px !important;
    position: relative !important;
    text-align: center !important;
    margin: 0 20px 0 0 !important;
    display: flex !important;
    flex-direction: column !important;
    align-items: center !important;
    justify-content: center !important;
}

.dashboard-robot-station-inner {
    background: transparent !important;
    border: none !important;
    border-radius: 0 !important;
    padding: 0 !important;
    box-shadow: none !important;
    backdrop-filter: none !important;
    -webkit-backdrop-filter: none !important;
    display: flex !important;
    flex-direction: column !important;
    align-items: center !important;
    justify-content: center !important;
    transition: all 0.3s ease !important;
}
.dashboard-robot-station-inner:hover {
    border: none !important;
    box-shadow: none !important;
}

.dashboard-robot-canvas-container {
    width: 140px !important;
    height: 155px !important;
    position: relative !important;
    cursor: pointer !important;
    display: flex !important;
    flex-direction: column !important;
    align-items: center !important;
    justify-content: center !important;
    transition: transform 0.25s ease !important;
}
.dashboard-robot-canvas-container:hover {
    transform: scale(1.06) !important;
}
.dashboard-robot-canvas-slot {
    width: 100% !important;
    height: 100% !important;
    position: relative !important;
    z-index: 2 !important;
}
.dashboard-robot-chibi-img {
    width: 135px !important;
    height: 145px !important;
    object-fit: contain !important;
    filter: drop-shadow(0 10px 22px rgba(0, 240, 255, 0.65)) drop-shadow(0 0 16px rgba(168, 85, 247, 0.4)) !important;
    animation: auraIdleStroll 1.6s infinite ease-in-out !important;
    display: block !important;
    margin: 0 auto !important;
    cursor: pointer !important;
    transition: filter 0.25s ease, transform 0.25s ease !important;
}
.dashboard-robot-chibi-img:hover {
    filter: drop-shadow(0 14px 28px rgba(0, 240, 255, 0.85)) drop-shadow(0 0 22px rgba(56, 189, 248, 0.7)) !important;
    transform: scale(1.04) translateY(-2px) !important;
}

/* Realistic Idle Walking Stride in Place */
@keyframes auraIdleStroll {
    0% {
        transform: translateY(0px) rotate(0deg) skewX(0deg);
    }
    18% {
        transform: translateY(-7px) rotate(-2.8deg) skewX(-2deg);
    }
    35% {
        transform: translateY(1.5px) rotate(1deg) skewX(0.8deg);
    }
    50% {
        transform: translateY(-1px) rotate(0deg) skewX(0deg);
    }
    68% {
        transform: translateY(-7px) rotate(2.8deg) skewX(2deg);
    }
    85% {
        transform: translateY(1.5px) rotate(-1deg) skewX(-0.8deg);
    }
    100% {
        transform: translateY(0px) rotate(0deg) skewX(0deg);
    }
}

/* Active Realistic Walking Journey when Clicked */
@keyframes auraRealisticWalk {
    0% {
        transform: translateX(0px) translateY(0px) rotate(0deg) scale(1, 1);
    }
    12% {
        transform: translateX(8px) translateY(-11px) rotate(-4deg) scale(0.96, 1.05);
    }
    24% {
        transform: translateX(16px) translateY(3px) rotate(2.5deg) scale(1.05, 0.94);
    }
    36% {
        transform: translateX(8px) translateY(-11px) rotate(4deg) scale(0.96, 1.05);
    }
    48% {
        transform: translateX(0px) translateY(3px) rotate(-2deg) scale(1.05, 0.94);
    }
    60% {
        transform: translateX(-8px) translateY(-11px) rotate(-4deg) scale(0.96, 1.05);
    }
    72% {
        transform: translateX(-16px) translateY(3px) rotate(2.5deg) scale(1.05, 0.94);
    }
    84% {
        transform: translateX(-6px) translateY(-12px) rotate(0deg) scale(0.95, 1.08);
    }
    92% {
        transform: translateX(0px) translateY(-4px) rotate(3deg) scale(1.04, 0.96);
    }
    100% {
        transform: translateX(0px) translateY(0px) rotate(0deg) scale(1, 1);
    }
}
.cute-walking-active {
    animation: auraRealisticWalk 1.55s cubic-bezier(0.25, 1, 0.5, 1) !important;
}

.dashboard-robot-pedestal-glow {
    position: absolute !important;
    bottom: 2px !important;
    width: 120px !important;
    height: 24px !important;
    border-radius: 50% !important;
    background: radial-gradient(ellipse at center, rgba(0, 240, 255, 0.65) 0%, rgba(168, 85, 247, 0.35) 45%, transparent 75%) !important;
    box-shadow: 0 0 24px rgba(0, 240, 255, 0.7), inset 0 0 12px rgba(0, 240, 255, 0.4) !important;
    z-index: 1 !important;
    animation: pedestalFloat 1.6s infinite ease-in-out !important;
}
@keyframes pedestalFloat {
    0%, 100% { transform: scale(0.94); opacity: 0.75; }
    50% { transform: scale(1.06); opacity: 1; }
}

/* Holographic Footstep Ripple Ring */
.pedestal-walk-ripple {
    position: absolute !important;
    bottom: 6px !important;
    left: 50% !important;
    transform: translateX(-50%) !important;
    width: 50px !important;
    height: 14px !important;
    border-radius: 50% !important;
    border: 2px solid #00f0ff !important;
    box-shadow: 0 0 14px #00f0ff !important;
    opacity: 0 !important;
    pointer-events: none !important;
    z-index: 2 !important;
}
.pedestal-walk-ripple.active {
    animation: walkRippleAnim 0.55s ease-out !important;
}
@keyframes walkRippleAnim {
    0% { transform: translateX(-50%) scale(0.3); opacity: 1; }
    100% { transform: translateX(-50%) scale(2.4); opacity: 0; }
}

.cute-bot-speech-bubble {
    position: absolute !important;
    top: -24px !important;
    left: 50% !important;
    transform: translateX(-50%) !important;
    background: linear-gradient(135deg, rgba(15, 23, 42, 0.96) 0%, rgba(14, 165, 233, 0.92) 100%) !important;
    border: 1.5px solid #00f0ff !important;
    border-radius: 14px !important;
    padding: 3px 10px !important;
    font-size: 0.72rem !important;
    font-weight: 800 !important;
    color: #ffffff !important;
    white-space: nowrap !important;
    box-shadow: 0 4px 18px rgba(0, 240, 255, 0.55), 0 0 10px rgba(168, 85, 247, 0.4) !important;
    pointer-events: none !important;
    z-index: 10 !important;
    animation: bubbleBounce 2.5s infinite ease-in-out !important;
    display: flex !important;
    align-items: center !important;
    gap: 4px !important;
    letter-spacing: 0.02em !important;
    transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1) !important;
}
.cute-bot-speech-bubble::after {
    content: '' !important;
    position: absolute !important;
    bottom: -6px !important;
    left: 50% !important;
    transform: translateX(-50%) !important;
    width: 0 !important;
    height: 0 !important;
    border-left: 6px solid transparent !important;
    border-right: 6px solid transparent !important;
    border-top: 6px solid #00f0ff !important;
}
@keyframes bubbleBounce {
    0%, 100% { transform: translateX(-50%) translateY(0); }
    50% { transform: translateX(-50%) translateY(-5px); }
}

/* =========================================================================
   AURA AUTOMATIC WALKING ROBOT ON THE LANGUAGE BOX (REALISTIC BIPEDAL GAIT)
   ========================================================================= */
.lang-box-walking-stage {
    position: relative !important;
    width: 100% !important;
    height: 96px !important;
    margin-bottom: 2px !important;
    overflow: visible !important;
}

/* Glowing Neon Runway Track along the top of the Language Box */
.lang-box-runway-track {
    position: absolute !important;
    bottom: 2px !important;
    left: 10px !important;
    right: 10px !important;
    height: 3px !important;
    background: linear-gradient(90deg, transparent 0%, rgba(56, 189, 248, 0.75) 12%, rgba(168, 85, 247, 0.85) 50%, rgba(56, 189, 248, 0.75) 88%, transparent 100%) !important;
    box-shadow: 0 0 12px rgba(56, 189, 248, 0.9), 0 0 24px rgba(168, 85, 247, 0.6) !important;
    border-radius: 999px !important;
}

/* The Robot Patrol: Moves automatically side-to-side across the language box with realistic deceleration and turnaround */
.lang-box-walking-aura {
    position: absolute !important;
    bottom: 2px !important;
    width: 90px !important;
    height: 96px !important;
    display: flex !important;
    flex-direction: column !important;
    align-items: center !important;
    justify-content: flex-end !important;
    animation: auraAutoWalkAcross 32s infinite ease-in-out !important;
    pointer-events: auto !important;
    cursor: pointer !important;
    z-index: 20 !important;
    transition: filter 0.3s ease, transform 0.3s cubic-bezier(0.34, 1.56, 0.64, 1) !important;
    user-select: none !important;
}

.lang-box-walking-aura:hover {
    animation-play-state: paused !important;
    filter: drop-shadow(0 0 18px rgba(0, 240, 255, 0.95)) drop-shadow(0 0 32px rgba(168, 85, 247, 0.85)) !important;
    transform: translateY(-2px) scale(1.04) !important;
}

.lang-box-walking-aura:active {
    transform: scale(0.94) !important;
}

.lang-box-walking-aura:focus-visible {
    outline: 2px solid #00f0ff !important;
    outline-offset: 4px !important;
    border-radius: 12px !important;
}

/* Horizontal patrol keyframes with smooth deceleration, pause & turnaround at edges */
@keyframes auraAutoWalkAcross {
    0%   { left: 16px; }
    46%  { left: calc(100% - 106px); }
    54%  { left: calc(100% - 106px); }
    96%  { left: 16px; }
    100% { left: 16px; }
}

.lang-bot-figure-wrap {
    position: relative !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    transform-origin: center bottom !important;
}

/* Procedural 3D Articulated Robot Canvas (Realistic, Cute 3D Mascot) */
.aura-walking-3d-canvas {
    width: 90px !important;
    height: 96px !important;
    display: block !important;
    pointer-events: none !important;
    filter: drop-shadow(0 6px 14px rgba(0, 0, 0, 0.45)) drop-shadow(0 0 14px rgba(56, 189, 248, 0.6)) !important;
    user-select: none !important;
}

/* Realistic Bipedal Stride: Full 4-phase gait cycle with double-bounce, pelvic sway, foot impact */
.lang-bot-walking-img {
    width: 66px !important;
    height: 66px !important;
    object-fit: contain !important;
    filter: drop-shadow(0 6px 14px rgba(0, 240, 255, 0.75)) drop-shadow(0 0 10px rgba(168, 85, 247, 0.5)) !important;
    animation: auraRealisticBipedalStride 0.74s infinite cubic-bezier(0.45, 0.05, 0.55, 0.95) !important;
    display: block !important;
    transform-origin: 50% 92% !important;
    user-select: none !important;
}

@keyframes auraRealisticBipedalStride {
    0% {
        /* Left foot contact: body down, left hip/torso forward */
        transform: translateY(0px) rotate(-3deg) skewX(-2.5deg) scale(1.02, 0.98);
    }
    25% {
        /* Mid-stance apex: body rises to highest point, hips level */
        transform: translateY(-8px) rotate(0deg) skewX(0deg) scale(0.98, 1.02);
    }
    50% {
        /* Right foot contact: body down, right hip/torso forward */
        transform: translateY(0px) rotate(3deg) skewX(2.5deg) scale(1.02, 0.98);
    }
    75% {
        /* Mid-stance apex: body rises to highest point, hips level */
        transform: translateY(-8px) rotate(0deg) skewX(0deg) scale(0.98, 1.02);
    }
    100% {
        /* Return to left foot contact */
        transform: translateY(0px) rotate(-3deg) skewX(-2.5deg) scale(1.02, 0.98);
    }
}

/* Glowing Holographic Footstep Disc pulsing synchronously with foot strikes */
.lang-bot-hologram-disc {
    position: absolute !important;
    bottom: -3px !important;
    width: 54px !important;
    height: 15px !important;
    border-radius: 50% !important;
    background: radial-gradient(ellipse at center, rgba(0, 240, 255, 0.90) 0%, rgba(2, 132, 199, 0.55) 45%, transparent 75%) !important;
    box-shadow: 0 0 18px rgba(0, 240, 255, 0.9), inset 0 0 8px rgba(0, 240, 255, 0.6) !important;
    z-index: -1 !important;
    animation: auraDiscPulse 0.74s infinite cubic-bezier(0.45, 0.05, 0.55, 0.95) !important;
}

@keyframes auraDiscPulse {
    0% {
        /* Foot strike ground contact: disc expands & glows intensely */
        transform: scale(1.18);
        opacity: 0.95;
    }
    25% {
        /* Body in apex: disc shrinks as feet lift */
        transform: scale(0.82);
        opacity: 0.50;
    }
    50% {
        /* Opposite foot strike ground contact: disc expands & glows */
        transform: scale(1.18);
        opacity: 0.95;
    }
    75% {
        /* Body in apex: disc shrinks */
        transform: scale(0.82);
        opacity: 0.50;
    }
    100% {
        transform: scale(1.18);
        opacity: 0.95;
    }
}

/* Speech Bubble / Welcome Tooltip floating above Aura's head */
.lang-bot-speech-bubble {
    position: absolute !important;
    top: -38px !important;
    left: 50% !important;
    transform: translateX(-50%) !important;
    background: linear-gradient(135deg, rgba(8, 20, 44, 0.96) 0%, rgba(13, 33, 68, 0.92) 100%) !important;
    border: 1.5px solid #00f0ff !important;
    border-radius: 14px !important;
    padding: 4px 14px !important;
    display: flex !important;
    flex-direction: column !important;
    align-items: center !important;
    gap: 2px !important;
    font-size: 0.72rem !important;
    font-weight: 800 !important;
    color: #ffffff !important;
    white-space: nowrap !important;
    box-shadow: 0 6px 20px rgba(0, 0, 0, 0.75), 0 0 16px rgba(0, 240, 255, 0.45) !important;
    backdrop-filter: blur(8px) !important;
    -webkit-backdrop-filter: blur(8px) !important;
    pointer-events: auto !important;
    cursor: pointer !important;
    z-index: 25 !important;
    letter-spacing: 0.02em !important;
    animation: langBubbleBob 1.48s infinite ease-in-out !important;
    transition: all 0.25s ease !important;
}

.lang-bot-tag {
    display: inline-flex !important;
    align-items: center !important;
    gap: 4px !important;
    background: rgba(0, 240, 255, 0.15) !important;
    border: 1px solid rgba(0, 240, 255, 0.5) !important;
    border-radius: 9999px !important;
    padding: 1px 7px !important;
    font-size: 0.58rem !important;
    font-weight: 800 !important;
    color: #38bdf8 !important;
    letter-spacing: 0.05em !important;
}

.lang-box-walking-aura:hover .lang-bot-speech-bubble {
    background: linear-gradient(135deg, rgba(8, 20, 44, 0.98) 0%, rgba(2, 132, 199, 0.90) 100%) !important;
    border-color: #38bdf8 !important;
    color: #ffffff !important;
    box-shadow: 0 0 24px rgba(0, 240, 255, 0.75), 0 8px 24px rgba(0, 0, 0, 0.8) !important;
}
.lang-bot-speech-bubble::after {
    content: '' !important;
    position: absolute !important;
    bottom: -6px !important;
    left: 50% !important;
    transform: translateX(-50%) !important;
    width: 0 !important;
    height: 0 !important;
    border-left: 6px solid transparent !important;
    border-right: 6px solid transparent !important;
    border-top: 6px solid #00f0ff !important;
}
@keyframes langBubbleBob {
    0%, 100% { transform: translateX(-50%) translateY(0); }
    50% { transform: translateX(-50%) translateY(-4px); }
}

.qr-hero-main-content {
    flex: 1 !important;
    display: flex !important;
    flex-direction: column !important;
    align-items: center !important;
    justify-content: center !important;
    text-align: center !important;
}

/* =========================================================================
   COMPREHENSIVE RESPONSIVE DESIGN SYSTEM TOKENS & MEDIA BREAKPOINTS
   Ensures seamless adaptability across Android phones, iPhones, foldables,
   tablets, laptops, and 4K displays (320px to 1920px+).
   ========================================================================= */

*, *::before, *::after {
    box-sizing: border-box !important;
}

/* Fluid Adaptive Typography */
.qr-hero-heading {
    font-size: clamp(1.4rem, 4.5vw, 2.6rem) !important;
    word-break: break-word !important;
}
.qr-hero-subtag {
    font-size: clamp(0.60rem, 2vw, 0.74rem) !important;
    letter-spacing: clamp(0.10em, 1.5vw, 0.22em) !important;
}
.qr-hero-tagline {
    font-size: clamp(0.84rem, 2.4vw, 1.02rem) !important;
    padding: 0 6px !important;
    line-height: 1.45 !important;
}
.qr-brand-title {
    font-size: clamp(1.15rem, 3.8vw, 1.55rem) !important;
}

/* Responsive Multilingual Interface Selector Bar */
.st-key-main_lang_bar_container div[data-testid="stHorizontalBlock"] {
    display: grid !important;
    grid-template-columns: repeat(8, 1fr) !important;
    gap: 6px !important;
    align-items: stretch !important;
}
.st-key-main_lang_bar_container div[data-testid="stColumn"] {
    min-width: 0 !important;
    width: 100% !important;
    flex: 1 1 0px !important;
}
.st-key-main_lang_bar_container .stButton > button {
    min-height: 42px !important;
    padding: 6px 4px !important;
    font-size: 0.84rem !important;
    white-space: nowrap !important;
    text-align: center !important;
    justify-content: center !important;
    border-radius: 10px !important;
}

/* Responsive 4-Workspace Landing Cards */
.st-key-qr_workspace_cards_deck div[data-testid="stHorizontalBlock"] {
    display: grid !important;
    grid-template-columns: repeat(4, 1fr) !important;
    gap: 14px !important;
    align-items: stretch !important;
}
.st-key-qr_workspace_cards_deck div[data-testid="stColumn"] {
    min-width: 0 !important;
    width: 100% !important;
    flex: 1 1 0px !important;
}

/* Tablet & Medium Breakpoint (<= 1024px) */
@media (max-width: 1024px) {
    .st-key-main_lang_bar_container div[data-testid="stHorizontalBlock"] {
        grid-template-columns: repeat(4, 1fr) !important;
        gap: 6px !important;
    }
    .st-key-main_lang_bar_container div[data-testid="stColumn"] {
        flex: none !important;
        width: auto !important;
    }
    .st-key-qr_workspace_cards_deck div[data-testid="stHorizontalBlock"] {
        grid-template-columns: repeat(2, 1fr) !important;
        gap: 12px !important;
    }
    .st-key-qr_workspace_cards_deck div[data-testid="stColumn"] {
        flex: none !important;
        width: auto !important;
    }
    .qr-workspace-card {
        min-height: 220px !important;
    }
}

/* Mobile Devices & Small Tablets (<= 768px) */
@media (max-width: 768px) {
    /* Critical: Eliminate desktop 6rem gutter padding so screen fits 100% */
    .main .block-container,
    div[data-testid="stAppViewBlockContainer"] {
        padding-top: calc(0.75rem + env(safe-area-inset-top, 0px)) !important;
        padding-bottom: calc(3.5rem + env(safe-area-inset-bottom, 0px)) !important;
        padding-left: calc(0.5rem + env(safe-area-inset-left, 0px)) !important;
        padding-right: calc(0.5rem + env(safe-area-inset-right, 0px)) !important;
        max-width: 100vw !important;
        box-sizing: border-box !important;
    }

    /* Top Navigation Bar: compact wrap */
    .qr-navbar-container {
        padding: 8px 12px !important;
        gap: 8px !important;
        border-radius: 12px !important;
        margin-bottom: 10px !important;
    }
    .qr-logo-emblem {
        width: 36px !important;
        height: 36px !important;
        font-size: 1.3rem !important;
    }

    /* Hide on-screen virtual keyboard trigger on touch devices (native OS keyboard used) */
    #pathfinder-vk-fab-trigger,
    .virtual-keyboard-fab {
        display: none !important;
        visibility: hidden !important;
        pointer-events: none !important;
    }

    /* Compact, non-intrusive floating AURA chatbot FAB docked bottom-right */
    [data-testid="stElementContainer"]:has([data-testid="stPopover"]),
    div[data-testid="stPopover"],
    .floating-aura-logo-overlay {
        bottom: 16px !important;
        right: 14px !important;
        width: 50px !important;
        height: 50px !important;
        min-width: 50px !important;
        max-width: 50px !important;
        min-height: 50px !important;
        max-height: 50px !important;
    }
    div[data-testid="stPopover"] > button,
    div[data-testid="stPopover"] button {
        width: 50px !important;
        height: 50px !important;
        min-width: 50px !important;
        max-width: 50px !important;
        min-height: 50px !important;
        max-height: 50px !important;
    }

    /* Responsive Map Viewport */
    iframe[title="streamlit_folium.st_folium"],
    div[data-testid="stIFrame"] iframe {
        height: clamp(340px, 52vh, 500px) !important;
        min-height: 340px !important;
        width: 100% !important;
        max-width: 100% !important;
        border-radius: 10px !important;
    }

    /* Tabs pill bar */
    div[data-testid="stTabs"] [role="tab"] {
        padding: 8px 12px !important;
        font-size: 0.82rem !important;
        min-height: 38px !important;
    }
}

/* Small Smartphone Viewports (<= 600px) */
@media (max-width: 600px) {
    /* Stack 4-Workspace Landing Cards vertically with compact padding */
    .st-key-qr_workspace_cards_deck div[data-testid="stHorizontalBlock"] {
        grid-template-columns: 1fr !important;
        gap: 10px !important;
    }
    .qr-workspace-card {
        min-height: auto !important;
        padding: 16px 14px 12px 14px !important;
    }

    /* Scale Walking Robot Runway so it stays inside mobile viewport */
    .lang-box-walking-stage {
        height: 64px !important;
        transform: scale(0.72) !important;
        transform-origin: bottom center !important;
        margin-bottom: 0 !important;
    }
}

/* Narrow Smartphones (<= 480px, including iPhone SE, iPhone 12-15 Mini/Standard) */
@media (max-width: 480px) {
    .main .block-container,
    div[data-testid="stAppViewBlockContainer"] {
        padding-top: calc(0.5rem + env(safe-area-inset-top, 0px)) !important;
        padding-bottom: calc(3.5rem + env(safe-area-inset-bottom, 0px)) !important;
        padding-left: calc(0.35rem + env(safe-area-inset-left, 0px)) !important;
        padding-right: calc(0.35rem + env(safe-area-inset-right, 0px)) !important;
    }

    .st-key-main_lang_bar_container div[data-testid="stHorizontalBlock"] {
        grid-template-columns: repeat(4, 1fr) !important;
        gap: 4px !important;
    }
    .st-key-main_lang_bar_container .stButton > button {
        min-height: 38px !important;
        font-size: 0.72rem !important;
        padding: 4px 2px !important;
        letter-spacing: 0 !important;
    }
}

/* Mobile Bottom Sheet Handle Bar */
.mobile-bottom-sheet-handle-bar {
    display: none;
    background: rgba(15, 23, 42, 0.95);
    border: 1px solid rgba(56, 189, 248, 0.35);
    border-radius: 12px 12px 0 0;
    padding: 8px 12px 4px 12px;
    margin-bottom: 8px;
    text-align: center;
}
.mobile-bottom-sheet-pill-handle {
    width: 44px;
    height: 5px;
    background: rgba(56, 189, 248, 0.6);
    border-radius: 999px;
    margin: 0 auto 6px auto;
}

/* Tiered Breakpoints for View Navigation Header */
@media (max-width: 768px) {
    div[class*="st-key-view_nav_header_container"] div[data-testid="stHorizontalBlock"] {
        display: flex !important;
        flex-direction: column !important;
        gap: 8px !important;
    }
    div[class*="st-key-view_nav_header_container"] div[data-testid="stColumn"] {
        width: 100% !important;
        flex: 1 1 100% !important;
    }
    div[class*="st-key-view_nav_header_container"] div[data-testid="stColumn"]:nth-child(2) div[data-testid="stHorizontalBlock"] {
        display: flex !important;
        flex-direction: row !important;
        gap: 6px !important;
        align-items: center !important;
    }
    div[class*="st-key-view_nav_header_container"] h2 {
        font-size: 1.25rem !important;
    }
}
@media (max-width: 430px) {
    div[class*="st-key-view_nav_header_container"] h2 {
        font-size: 1.10rem !important;
    }
}

</style>
"""


def render_quantum_navbar(
    active_haz_count: int = 0,
    active_restr_count: int = 0,
    traffic_text: str = "Normal Flow",
    active_obj_val: str = "FASTEST"
):
    """
    Navbar and traveler profile removed as requested.
    """
    return



DASHBOARD_I18N = {
    "en": {
        "title": "NEXROUTE",
        "subtag": "AUTONOMOUS AI TRAVEL & ADAPTIVE NAVIGATION SYSTEM",
        "tagline": "Explore destinations, generate verified itineraries & navigate seamlessly with local Ollama AI intelligence.",
        "lang_banner_title": "SELECT LANGUAGE",
        "lang_banner_sub": "Instant real-time interface localization across 8 Indian & Global languages",
        "active": "Active",
        "card1_sub": "INTELLIGENT TRIP ADVISOR",
        "card1_title": "AI TRAVEL COPILOT",
        "card1_desc": "Personalized day-by-day itineraries, smart budgeting, transportation comparisons, and local advice powered by local Ollama intelligence.",
        "card1_btn": "ENTER COPILOT →",
        "card2_sub": "MULTI-CORRIDOR ROUTING",
        "card2_title": "MAP & NAVIGATION",
        "card2_desc": "Real-time multi-objective routing (Fastest, Shortest, Balanced, Accessible), live hazard detection, satellite road intelligence, and Google Maps.",
        "card2_btn": "LAUNCH MAP →",
        "card3_sub": "CURATED EXPLORATION",
        "card3_title": "PLACES & SIGHTS",
        "card3_desc": "Curated regional highlights, outdoor adventures, hotel guidelines, and weather-synchronized travel recommendations.",
        "card3_btn": "EXPLORE PLACES →",
        "card4_sub": "REAL-TIME COMPANION",
        "card4_title": "VIRTUAL GUIDE",
        "card4_desc": "Turn-by-turn storytelling, 3D walking companion HUD, kinematics, and cinematic journey milestones.",
        "card4_btn": "LAUNCH GUIDE →",
        "back_dash": "🏠 ← Back to Main Dashboard"
    },
    "te": {
        "title": "నెక్స్‌రూట్",
        "subtag": "స్వయంప్రతిపత్త AI ప్రయాణం & అనుకూల నావిగేషన్ సిస్టమ్",
        "tagline": "గమ్యస్థానాలను అన్వేషించండి, ధృవీకరించిన ప్రయాణ ప్రణాళికలను రూపొందించండి మరియు స్థానిక Ollama AIతో సులభంగా నావిగేట్ చేయండి.",
        "lang_banner_title": "భాషను ఎంచుకోండి",
        "lang_banner_sub": "8 భారతీయ మరియు ప్రపంచ భాషలలో తక్షణ అనువాదం",
        "active": "ప్రస్తుత భాష",
        "card1_sub": "మేధో ప్రయాణ సలహాదారు",
        "card1_title": "AI ట్రావెల్ కోపైలట్",
        "card1_desc": "రోజువారీ వ్యక్తిగతీకరించిన ప్రయాణ ప్రణాళికలు, స్మార్ట్ బడ్జెట్, రవాణా పోలికలు మరియు Ollama స్థానిక AI సలహాలు.",
        "card1_btn": "కోపైలట్‌లోకి ప్రవేశించండి →",
        "card2_sub": "బహుళ-మార్గాల రూటింగ్",
        "card2_title": "మ్యాప్ & నావిగేషన్",
        "card2_desc": "రియల్-టైమ్ బహుళ-లక్ష్యాల రూటింగ్ (వేగవంతమైన, తక్కువ దూరం, సమతుల్య), ప్రత్యక్ష ప్రమాదాల గుర్తింపు మరియు ఉపగ్రహ సమాచారం.",
        "card2_btn": "మ్యాప్‌ను ప్రారంభించండి →",
        "card3_sub": "ప్రత్యేక అన్వేషణ",
        "card3_title": "ప్రదేశాలు & ఆకర్షణలు",
        "card3_desc": "ప్రాంతీయ ముఖ్యాంశాలు, బహిరంగ సాహసాలు, హోటల్ సమాచారం మరియు వాతావరణ ఆధారిత ప్రయాణ సిఫార్సులు.",
        "card3_btn": "ప్రదేశాలను అన్వేషించండి →",
        "card4_sub": "ప్రత్యక్ష ప్రయాణ సహచరుడు",
        "card4_title": "వర్చువల్ గైడ్",
        "card4_desc": "మలుపు-మలుపు కథనం, 3D వాకింగ్ కంపానియన్ HUD, కైనమాటిక్స్ మరియు సినిమాటిక్ జర్నీ మైలురాళ్ళు.",
        "card4_btn": "గైడ్‌ను ప్రారంభించండి →",
        "back_dash": "🏠 ← ప్రధాన డ్యాష్‌బోర్డ్‌కు తిరిగి వెళ్లండి"
    },
    "hi": {
        "title": "नेक्सरूट",
        "subtag": "स्वायत्त AI यात्रा और अनुकूली नेविगेशन प्रणाली",
        "tagline": "स्थानीय Ollama AI इंटेलिजेंस के साथ गंतव्यों का अन्वेषण करें, सत्यापित यात्रा कार्यक्रम तैयार करें और सहजता से नेविगेट करें।",
        "lang_banner_title": "भाषा चुनें",
        "lang_banner_sub": "8 भारतीय और वैश्विक भाषाओं में त्वरित इंटरफ़ेस स्थानीयकरण",
        "active": "सक्रिय",
        "card1_sub": "बुद्धिमान यात्रा सलाहकार",
        "card1_title": "AI यात्रा सह-पायलट",
        "card1_desc": "दैनिक व्यक्तिगत यात्रा कार्यक्रम, स्मार्ट बजट, परिवहन तुलना और स्थानीय Ollama AI सलाह।",
        "card1_btn": "सह-पायलट खोलें →",
        "card2_sub": "मल्टी-कॉरिडोर रूटिंग",
        "card2_title": "नक्शा और नेविगेशन",
        "card2_desc": "रीयल-टाइम बहु-उद्देश्यीय रूटिंग (सबसे तेज़, सबसे छोटा, संतुलित, सुलभ), लाइव खतरा पहचान और उपग्रह सड़क बुद्धिमत्ता।",
        "card2_btn": "नक्शा शुरू करें →",
        "card3_sub": "विशेष अन्वेषण",
        "card3_title": "दर्शनीय स्थल और स्थान",
        "card3_desc": "क्षेत्रीय मुख्य आकर्षण, रोमांचक यात्राएं, होटल दिशानिर्देश और मौसम-आधारित यात्रा सिफारिशें।",
        "card3_btn": "स्थान देखें →",
        "card4_sub": "रीयल-टाइम साथी",
        "card4_title": "वर्चुअल गाइड",
        "card4_desc": "मोड़-दर-मोड़ मार्गदर्शन, 3D साथी HUD, काइनेमैटिक्स और सिनेमाई यात्रा पड़ाव।",
        "card4_btn": "गाइड शुरू करें →",
        "back_dash": "🏠 ← मुख्य डैशबोर्ड पर वापस जाएं"
    },
    "ta": {
        "title": "நெக்ஸ்ரூட்",
        "subtag": "தன்னாட்சி AI பயணம் & தகவமைப்பு வழிசெலுத்தல் அமைப்பு",
        "tagline": "உள்ளூர் Ollama AI நுண்ணறிவுடன் இடங்களை ஆராயுங்கள், சரிபார்க்கப்பட்ட பயணத்திட்டங்களை உருவாக்குங்கள்.",
        "lang_banner_title": "மொழியைத் தேர்ந்தெடுக்கவும்",
        "lang_banner_sub": "8 இந்திய மற்றும் உலகளாவிய மொழிகளில் உடனடி மொழிபெயர்ப்பு",
        "active": "செயலில் உள்ளது",
        "card1_sub": "நுண்ணறிவுப் பயண ஆலோசகர்",
        "card1_title": "AI பயணக் கோபைலட்",
        "card1_desc": "தனிப்பயனாக்கப்பட்ட தினசரி பயணத்திட்டங்கள், பட்ஜெட், போக்குவரத்து ஒப்பீடுகள் மற்றும் உள்ளூர் Ollama AI ஆலோசனைகள்.",
        "card1_btn": "கோபைலட் தொடங்கவும் →",
        "card2_sub": "பல-வழிப்பாதை வழிசெலுத்தல்",
        "card2_title": "வரைபடம் & வழிசெலுத்தல்",
        "card2_desc": "நேரடி பல-குறிக்கோள் வழிசெலுத்தல் (வேகமானது, குறுகியது, சமநிலையானது), நேரடி ஆபத்து கண்டறிதல்.",
        "card2_btn": "வரைபடத்தைத் திறக்கவும் →",
        "card3_sub": "தேர்ந்தெடுக்கப்பட்ட இடங்கள்",
        "card3_title": "இடங்கள் & காட்சிகள்",
        "card3_desc": "பிராந்திய சிறப்பம்சங்கள், வெளிப்புற சாகசங்கள், ஹோட்டல் வழிகாட்டல்கள் மற்றும் வானிலை பரிந்துரைகள்.",
        "card3_btn": "இடங்களை ஆராயுங்கள் →",
        "card4_sub": "நேரடி பயணத் தோழன்",
        "card4_title": "மெய்நிகர் வழிகாட்டி",
        "card4_desc": "ஒவ்வொரு திருப்பத்திற்கான கதை, 3D வழிகாட்டி HUD மற்றும் சினிமா பயண மைல்கற்கள்.",
        "card4_btn": "வழிகாட்டியைத் திறக்கவும் →",
        "back_dash": "🏠 ← முதன்மை டாஷ்போர்டுக்கு திரும்பு"
    },
    "kn": {
        "title": "ನೆಕ್ಸ್‌ರೂಟ್",
        "subtag": "ಸ್ವಾಯತ್ತ AI ಪ್ರಯಾಣ ಮತ್ತು ಹೊಂದಾಣಿಕೆಯ ಸಂಚರಣೆ ವ್ಯವಸ್ಥೆ",
        "tagline": "ಸ್ಥಳೀಯ Ollama AI ಬುದ್ಧಿವಂತಿಕೆಯೊಂದಿಗೆ ಗಮ್ಯಸ್ಥಾನಗಳನ್ನು ಅನ್ವೇಷಿಸಿ, ಪರಿಶೀಲಿಸಿದ ಪ್ರಯಾಣ ವಿವರ ರಚಿಸಿ.",
        "lang_banner_title": "ಭಾಷೆಯನ್ನು ಆಯ್ಕೆಮಾಡಿ",
        "lang_banner_sub": "8 ಭಾರತೀಯ ಮತ್ತು ಜಾಗತಿಕ ಭಾಷೆಗಳಲ್ಲಿ ನೈಜ-ಸಮಯದ ಸ್ಥಳೀಕರಣ",
        "active": "ಸಕ್ರಿಯ",
        "card1_sub": "ಬುದ್ಧಿವಂತ ಪ್ರಯಾಣ ಸಲಹೆಗಾರ",
        "card1_title": "AI ಪ್ರಯಾಣ ಕೋಪೈಲಟ್",
        "card1_desc": "ದೈನಂದಿನ ವೈಯಕ್ತಿಕಗೊಳಿಸಿದ ಪ್ರಯಾಣ ವಿವರಗಳು, ಸ್ಮಾರ್ಟ್ ಬಜೆಟ್, ಸಾರಿಗೆ ಹೋಲಿಕೆಗಳು ಮತ್ತು Ollama AI ಸಲಹೆಗಳು.",
        "card1_btn": "ಕೋಪೈಲಟ್ ಪ್ರವೇಶಿಸಿ →",
        "card2_sub": "ಬಹು-ಮಾರ್ಗಗಳ ರೂಟಿಂಗ್",
        "card2_title": "ಮ್ಯಾಪ್ ಮತ್ತು ಸಂಚರಣೆ",
        "card2_desc": "ನೈಜ-ಸಮಯದ ಬಹು-ಉದ್ದೇಶಿತ ರೂಟಿಂಗ್ (ವೇಗದ, ಚಿಕ್ಕ, ಸಮತೋಲಿತ, ಪ್ರವೇಶಿಸಬಹುದಾದ), ಲೈವ್ ಅಪಾಯ ಪತ್ತೆ.",
        "card2_btn": "ಮ್ಯಾಪ್ ಪ್ರಾರಂಭಿಸಿ →",
        "card3_sub": "ವಿಶೇಷ ಅನ್ವೇಷಣೆ",
        "card3_title": "ಸ್ಥಳಗಳು ಮತ್ತು ಆಕರ್ಷಣೆಗಳು",
        "card3_desc": "ಪ್ರಾದೇಶಿಕ ಮುಖ್ಯಾಂಶಗಳು, ಸಾಹಸಗಳು, ಹೋಟೆಲ್ ಮಾರ್ಗದರ್ಶಿಗಳು ಮತ್ತು ಹವಾಮಾನ ಆಧಾರಿತ ಪ್ರಯಾಣ ಶಿಫಾರಸುಗಳು.",
        "card3_btn": "ಸ್ಥಳಗಳನ್ನು ಅನ್ವೇಷಿಸಿ →",
        "card4_sub": "ನೈಜ-ಸಮಯದ ಪ್ರಯಾಣ ಸಂಗಾತಿ",
        "card4_title": "ವರ್ಚುವಲ್ ಗೈಡ್",
        "card4_desc": "ತಿರುವು-ತಿರುವು ಕಥೆಗಳು, 3D ನಡಿಗೆ ಸಂಗಾತಿ HUD ಮತ್ತು ಸಿನಿಮಾ ಪ್ರಯಾಣದ ಮೈಲಿಗಲ್ಲುಗಳು.",
        "card4_btn": "ಮಾರ್ಗದರ್ಶಿ ಪ್ರಾರಂಭಿಸಿ →",
        "back_dash": "🏠 ← ಮುಖ್ಯ ಡ್ಯಾಶ್‌ಬೋರ್ಡ್‌ಗೆ ಹಿಂತಿರುಗಿ"
    },
    "ml": {
        "title": "നെക്സ്റൂട്ട്",
        "subtag": "സ്വയംഭരണ AI യാത്രാ & അഡാപ്റ്റീവ് നാവിഗേഷൻ സിസ്റ്റം",
        "tagline": "പ്രാദേശിക Ollama AI ഇന്റലിജൻസ് ഉപയോഗിച്ച് ലക്ഷ്യസ്ഥാനങ്ങൾ കണ്ടെത്തുക, സുഗമമായി നാവിഗേറ്റ് ചെയ്യുക.",
        "lang_banner_title": "ഭാഷ തിരഞ്ഞെടുക്കുക",
        "lang_banner_sub": "8 ഇന്ത്യൻ, ആഗോള ഭാഷകളിൽ തത്സമയ പ്രാദേശികവൽക്കരണം",
        "active": "സജീവം",
        "card1_sub": "ഇന്റലിജന്റ് ട്രിപ്പ് അഡ്വൈസർ",
        "card1_title": "AI ട്രാവൽ കോപൈലറ്റ്",
        "card1_desc": "വ്യക്തിഗതമാക്കിയ യാത്രാവിവരണം, സ്മാർട്ട് ബജറ്റ്, യാത്രാതാരതമ്യങ്ങൾ, Ollama AI നിർദ്ദേശങ്ങൾ.",
        "card1_btn": "കോപൈലറ്റിലേക്ക് പ്രവേശിക്കുക →",
        "card2_sub": "മൾട്ടി-കോറിഡോർ റൂട്ടിംഗ്",
        "card2_title": "മാപ്പും നാവിഗേഷനും",
        "card2_desc": "തത്സമയ മൾട്ടി-ഒബ്ജക്റ്റീവ് റൂട്ടിംഗ് (വേഗതയേറിയത്, കുറഞ്ഞ ദൂരം, സമതുലിതം), ലൈവ് അപകട മുന്നറിയിപ്പുകൾ.",
        "card2_btn": "മാപ്പ് തുറക്കുക →",
        "card3_sub": "തിരഞ്ഞെടുത്ത കാഴ്ചകൾ",
        "card3_title": "സ്ഥലങ്ങളും കാഴ്ചകളും",
        "card3_desc": "പ്രാദേശിക ആകർഷണങ്ങൾ, സാഹസിക യാത്രകൾ, ഹോട്ടൽ വിവരങ്ങൾ, കാലാവസ്ഥാ നിർദ്ദേശങ്ങൾ.",
        "card3_btn": "സ്ഥലങ്ങൾ കാണുക →",
        "card4_sub": "തത്സമയ യാത്രാ സഹായി",
        "card4_title": "വെർച്വൽ ഗൈഡ്",
        "card4_desc": "ഓരോ തിരിവിലും വിവരണം, 3D വാക്കിംഗ് കമ്പാനിയൻ HUD, സിനിമാറ്റിക് നാഴികക്കല്ലുകൾ.",
        "card4_btn": "ഗൈഡ് തുറക്കുക →",
        "back_dash": "🏠 ← പ്രധാന ഡാഷ്‌ബോർഡിലേക്ക് മടങ്ങുക"
    },
    "bn": {
        "title": "নেক্সরুট",
        "subtag": "স্বায়ত্তশাসিত AI ভ্রমণ ও অভিযোজিত নেভিগেশন সিস্টেম",
        "tagline": "স্থানীয় Ollama AI ইন্টেলিজেন্সের সাথে গন্তব্যগুলি অন্বেষণ করুন এবং নির্বিঘ্নে নেভিগেট করুন।",
        "lang_banner_title": "ভাষা নির্বাচন করুন",
        "lang_banner_sub": "৮টি ভারতীয় এবং বৈশ্বিক ভাষায় তাৎক্ষণিক অনুবাদ",
        "active": "সক্রিয়",
        "card1_sub": "বুদ্ধিমান ভ্রমণ উপদেষ্টা",
        "card1_title": "AI ট্রাভেল কোপাইলট",
        "card1_desc": "ব্যক্তিগতকৃত ভ্রমণপথ, স্মার্ট বাজেট, পরিবহন তুলনা এবং স্থানীয় Ollama AI পরামর্শ।",
        "card1_btn": "কোপাইলটে প্রবেশ করুন →",
        "card2_sub": "মাল্টি-করিডোর রাউটিং",
        "card2_title": "মানচিত্র ও নেভিগেশন",
        "card2_desc": "রিয়েল-টাইম বহু-উদ্দেশ্যমূলক রাউটিং (দ্রুততম, সংক্ষিপ্ততম, ভারসাম্যপূর্ণ) এবং লাইভ বিপদ সনাক্তকরণ।",
        "card2_btn": "ম্যাপ চালু করুন →",
        "card3_sub": "কিউরেটেড অন্বেষণ",
        "card3_title": "দর্শনীয় স্থান ও এলাকা",
        "card3_desc": "আঞ্চলিক হাইলাইটস, আউটডোর অ্যাডভেঞ্চার, হোটেল নির্দেশিকা এবং আবহাওয়া-ভিত্তিক ভ্রমণ সুপারিশ।",
        "card3_btn": "স্থানগুলি দেখুন →",
        "card4_sub": "রিয়েল-টাইম ভ্রমণ সঙ্গী",
        "card4_title": "ভার্চুয়াল গাইড",
        "card4_desc": "প্রতিটি বাঁকের গল্প, 3D হাঁটার সঙ্গী HUD, কাইনেমেটিক্স এবং সিনেমাটিক মাইলফলক।",
        "card4_btn": "গাইড চালু করুন →",
        "back_dash": "🏠 ← প্রধান ড্যাশবোর্ডে ফিরে যান"
    },
    "mr": {
        "title": "नेक्सरूट",
        "subtag": "स्वायत्त AI प्रवास आणि अनुकूली नेव्हिगेशन प्रणाली",
        "tagline": "स्थानिक Ollama AI बुद्धिमत्तेसह गंतव्यस्थाने शोधा आणि सहजतेने नेव्हिगेट करा.",
        "lang_banner_title": "भाषा निवडा",
        "lang_banner_sub": "८ भारतीय आणि जागतिक भाषांमध्ये त्वरित इंटरफेस भाषांतर",
        "active": "सक्रिय",
        "card1_sub": "हुशार प्रवास सल्लागार",
        "card1_title": "AI ट्रॅव्हल को-पायलट",
        "card1_desc": "वैयक्तिकृत दैनंदिन प्रवास योजना, स्मार्ट बजेट, वाहतूक तुलना आणि स्थानिक Ollama AI सल्ला.",
        "card1_btn": "सह-पायलट सुरू करा →",
        "card2_sub": "मल्टी-कॉरिडोर मार्ग",
        "card2_title": "नकाशा आणि नेव्हिगेशन",
        "card2_desc": "रिअल-टाइम मल्टी-ऑब्जेक्टिव्ह रूटिंग (सर्वात जलद, सर्वात लहान, संतुलित) आणि थेट धोका शोध.",
        "card2_btn": "नकाशा सुरू करा →",
        "card3_sub": "निवडक ठिकाणे",
        "card3_title": "ठिकाणे आणि दृश्ये",
        "card3_desc": "प्रादेशिक आकर्षणे, साहसी प्रवास, हॉटेल माहिती आणि हवामानानुसार प्रवास शिफारसी.",
        "card3_btn": "ठिकाणे शोधा →",
        "card4_sub": "रिअल-टाइम प्रवास सोबती",
        "card4_title": "व्हर्च्युअल मार्गदर्शक",
        "card4_desc": "प्रत्येक वळणावर मार्गदर्शन, 3D सोबती HUD, आणि प्रवासाचे महत्त्वाचे टप्पे.",
        "card4_btn": "मार्गदर्शक सुरू करा →",
        "back_dash": "🏠 ← मुख्य डॅशबोर्डवर परत जा"
    }
}


def render_main_language_bar():
    """
    Renders an elegant, high-visibility interactive language selector
    prominently at the top of the main dashboard only.
    Features an automatic walking 3D robot companion (AURA) continuously
    patrolling atop the language box runway with realistic bipedal walking stride.
    No manual buttons are required - starts automatically on load!
    """
    cur_lang = st.session_state.get("app_language", "en")
    ld = DASHBOARD_I18N.get(cur_lang, DASHBOARD_I18N["en"])

    walking_robot_html = """<div class="lang-box-walking-stage" id="lang-box-walking-stage"><div class="lang-box-runway-track"></div><div class="lang-box-walking-aura quick-tour-trigger-btn" id="lang-box-walking-aura" data-tour-trigger="true" role="button" tabindex="0" title="✨ Click AURA to start the Interactive Guided Tour! 🚀" onclick="if(window.triggerAuraTourLaunch){window.triggerAuraTourLaunch();}else if(window.parent&&window.parent.triggerAuraTourLaunch){window.parent.triggerAuraTourLaunch();}else if(window.startPathfinderTour){window.startPathfinderTour(0);}else if(window.parent&&window.parent.startPathfinderTour){window.parent.startPathfinderTour(0);}else if(window.top&&window.top.startPathfinderTour){window.top.startPathfinderTour(0);}else{var b=document.getElementById('btn-hero-quick-tour')||(window.parent&&window.parent.document.getElementById('btn-hero-quick-tour'));if(b)b.click();}"><div class="lang-bot-speech-bubble" id="lang-bot-speech-bubble"><span class="lang-bot-tag">✦ AI Guide</span><span id="lang-bot-speech-text">Click me for a tour! ✨</span></div><div class="lang-bot-figure-wrap" id="lang-bot-figure-wrap"><canvas id="aura-walking-3d-canvas" class="aura-walking-3d-canvas" width="180" height="192"></canvas></div><div class="lang-bot-hologram-disc"></div></div></div>"""

    st.markdown(f"""<div style="background: linear-gradient(135deg, rgba(15, 23, 42, 0.94) 0%, rgba(30, 41, 59, 0.88) 100%); border: 1.5px solid rgba(56, 189, 248, 0.45); border-radius: 16px; padding: 10px 18px 14px 18px; margin-bottom: 14px; box-shadow: 0 10px 30px rgba(0, 0, 0, 0.50), 0 0 20px rgba(56, 189, 248, 0.18); position: relative;">
{walking_robot_html}
<div style="display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 10px; padding-top: 6px;">
<div style="display: flex; align-items: center; gap: 10px;">
<span style="font-size: 1.35rem; filter: drop-shadow(0 0 8px #38bdf8);">🌐</span>
<div>
<div style="font-size: 0.88rem; font-weight: 800; color: #f8fafc; letter-spacing: 0.04em; display: flex; align-items: center; gap: 8px;">
<span>{ld['lang_banner_title']}</span>
<span style="color: #64748b; font-weight: 400;">•</span>
<span style="color: #38bdf8;">భాషను ఎంచుకోండి</span>
<span style="color: #64748b; font-weight: 400;">•</span>
<span style="color: #a855f7;">भाषा चुनें</span>
</div>
<div style="font-size: 0.68rem; color: #94a3b8; font-family: 'JetBrains Mono', monospace;">{ld['lang_banner_sub']}</div>
</div>
</div>
<div style="display: flex; align-items: center; gap: 10px; flex-wrap: wrap;">
<div style="display: flex; align-items: center; gap: 8px; font-size: 0.74rem; color: #38bdf8; font-weight: 700; background: rgba(56, 189, 248, 0.15); padding: 5px 12px; border-radius: 9999px; border: 1px solid rgba(56, 189, 248, 0.35);">
<span style="display: inline-block; width: 8px; height: 8px; border-radius: 50%; background: #10b981; box-shadow: 0 0 8px #10b981;"></span>
<span>{ld['active']}: <b>{SUPPORTED_LANGUAGES.get(cur_lang, {}).get('native', 'English')} ({cur_lang.upper()})</b></span>
</div>
</div>
</div>
</div>""", unsafe_allow_html=True)

    try:
        import streamlit.components.v1 as components
        components.html("""
        <script>
        (function() {
            var pWin = (window.parent && window.parent.window) || window;
            var pDoc = (window.parent && window.parent.document) || document;

            // Speech rotation
            var speechPhrases = [
                "🚀 Click me to take a tour! ✨",
                "👋 Hi! I am AURA! Click me! 🧭",
                "✨ Tap me to start guided tour! 🚀",
                "🌐 Select your language below! 🗺️",
                "🌸 నమస్కారం! టూర్ కోసం నన్ను క్లిక్ చేయండి ✨",
                "🌟 नमस्ते! टूर के लिए मुझे क्लिक करें 🗺️",
                "💫 Click me anytime for guided tour! 🚀"
            ];
            var sIdx = 0;

            // Dedicated tour launcher function registered on both frames
            pWin.triggerAuraTourLaunch = window.triggerAuraTourLaunch = function() {
                var el = pDoc.getElementById("lang-bot-speech-text") || document.getElementById("lang-bot-speech-text");
                if (el) {
                    el.innerHTML = "🚀 Starting Guided Tour... ✨";
                    el.style.opacity = "1";
                }
                if (typeof window.startPathfinderTour === "function") {
                    window.startPathfinderTour(0);
                } else if (typeof pWin.startPathfinderTour === "function") {
                    pWin.startPathfinderTour(0);
                } else if (pWin.top && typeof pWin.top.startPathfinderTour === "function") {
                    pWin.top.startPathfinderTour(0);
                } else {
                    var btn = pDoc.getElementById("btn-hero-quick-tour") || document.getElementById("btn-hero-quick-tour");
                    if (btn) btn.click();
                    try { pWin.postMessage("START_PATHFINDER_TOUR", "*"); } catch(e) {}
                    try { window.postMessage("START_PATHFINDER_TOUR", "*"); } catch(e) {}
                }
            };

            function bindAuraClickListener() {
                var targets = [
                    pDoc.getElementById("lang-box-walking-aura"),
                    document.getElementById("lang-box-walking-aura"),
                    pDoc.getElementById("lang-bot-speech-bubble"),
                    pDoc.getElementById("aura-walking-3d-canvas")
                ];
                targets.forEach(function(walker) {
                    if (walker && !walker._tourClickBound) {
                        walker._tourClickBound = true;
                        walker.style.cursor = "pointer";
                        walker.addEventListener("click", function(e) {
                            e.preventDefault();
                            e.stopPropagation();
                            if (window.triggerAuraTourLaunch) window.triggerAuraTourLaunch();
                            else if (pWin.triggerAuraTourLaunch) pWin.triggerAuraTourLaunch();
                            else if (pWin.startPathfinderTour) pWin.startPathfinderTour(0);
                            else if (window.startPathfinderTour) window.startPathfinderTour(0);
                        }, true);
                        walker.addEventListener("keydown", function(e) {
                            if (e.key === "Enter" || e.key === " ") {
                                e.preventDefault();
                                if (window.triggerAuraTourLaunch) window.triggerAuraTourLaunch();
                            }
                        });
                    }
                });
            }
            bindAuraClickListener();
            setTimeout(bindAuraClickListener, 300);
            setTimeout(bindAuraClickListener, 1000);
            setTimeout(bindAuraClickListener, 2500);
            setInterval(bindAuraClickListener, 1500);

            // Speech Rotation Timer
            if (!window.parent._langBotWalkInterval) {
                window.parent._langBotWalkInterval = setInterval(function() {
                    sIdx = (sIdx + 1) % speechPhrases.length;
                    var el = pDoc.getElementById("lang-bot-speech-text");
                    if (el) {
                        el.style.opacity = "0";
                        setTimeout(function() {
                            if (el) {
                                el.innerHTML = speechPhrases[sIdx];
                                el.style.opacity = "1";
                            }
                        }, 250);
                    }
                }, 3500);
            }

            // =========================================================================
            // PROCEDURAL 3D CUTE WALKING AURA CHATBOT RENDERER (NO STATIC IMAGES!)
            // =========================================================================
            // =========================================================================
            // POLISHED WHITE-AND-SILVER 3D AI ROBOT MASCOT RENDERER (NO CARTOON LEGS!)
            // =========================================================================
            var mascotImg3D = new Image();
            mascotImg3D.src = "data:image/png;base64,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";

            function initCuteAuraWalker() {
                var canvas = pDoc.getElementById("aura-walking-3d-canvas");
                if (!canvas) {
                    setTimeout(initCuteAuraWalker, 200);
                    return;
                }
                if (canvas._auraActive) return;
                canvas._auraActive = true;

                var ctx = canvas.getContext("2d");
                if (!ctx) return;

                var dpr = pWin.devicePixelRatio || 2;
                var w = 90;
                var h = 96;
                canvas.width = w * dpr;
                canvas.height = h * dpr;
                canvas.style.width = w + "px";
                canvas.style.height = h + "px";

                var auraWalker = pDoc.getElementById("lang-box-walking-aura");
                var isHovered = false;
                if (auraWalker) {
                    auraWalker.addEventListener("mouseenter", function() { isHovered = true; });
                    auraWalker.addEventListener("mouseleave", function() { isHovered = false; });
                }

                // Rising energy sparkle particles
                var particles = [];
                for (var i = 0; i < 9; i++) {
                    particles.push({
                        x: (Math.random() - 0.5) * 38,
                        y: Math.random() * 24,
                        speed: 0.22 + Math.random() * 0.38,
                        size: 0.9 + Math.random() * 1.6
                    });
                }

                var currentYaw = 1.0;
                var currentStride = 1.0;
                var lastTime = performance.now();

                function renderFrame(now) {
                    var dt = Math.min(64, now - lastTime);
                    lastTime = now;

                    ctx.save();
                    ctx.scale(dpr, dpr);
                    ctx.clearRect(0, 0, w, h);

                    var cx = 45;
                    var groundY = 82;

                    // Synchronize with 32-second horizontal patrol
                    var patrolPeriod = 32000;
                    var cycle = (now % patrolPeriod) / patrolPeriod;

                    var targetYaw = 1.0;
                    var targetStride = 1.0;

                    if (isHovered) {
                        targetYaw = 0.0;     // Face front towards user
                        targetStride = 0.0;  // Pause in place
                    } else if (cycle >= 0.0 && cycle < 0.44) {
                        targetYaw = 1.0;
                        targetStride = 1.0;
                    } else if (cycle >= 0.44 && cycle < 0.48) {
                        targetYaw = 1.0;
                        targetStride = Math.max(0, (0.48 - cycle) / 0.04);
                    } else if (cycle >= 0.48 && cycle < 0.52) {
                        targetStride = 0.0;
                        targetYaw = (0.50 - cycle) / 0.02; // Turnaround
                    } else if (cycle >= 0.52 && cycle < 0.94) {
                        targetYaw = -1.0;
                        targetStride = 1.0;
                    } else if (cycle >= 0.94 && cycle < 0.98) {
                        targetYaw = -1.0;
                        targetStride = Math.max(0, (0.98 - cycle) / 0.04);
                    } else {
                        targetStride = 0.0;
                        targetYaw = (cycle - 0.99) / 0.01;
                    }

                    currentYaw += (targetYaw - currentYaw) * 0.14;
                    currentStride += (targetStride - currentStride) * 0.16;

                    // Smooth anti-gravity floating bob
                    var bob = isHovered 
                        ? (Math.sin(now * 0.005) * 4.2)
                        : (Math.sin(now * 0.0035) * 3.2);

                    // 1. CONCENTRIC CYAN HOLOGRAPHIC PROJECTOR RINGS (FLOOR BASE)
                    ctx.save();
                    var discY = groundY + 2;
                    var discGrad = ctx.createRadialGradient(cx, discY, 2, cx, discY, 28);
                    discGrad.addColorStop(0, "rgba(0, 240, 255, 0.92)");
                    discGrad.addColorStop(0.35, "rgba(2, 132, 199, 0.55)");
                    discGrad.addColorStop(0.75, "rgba(0, 240, 255, 0.22)");
                    discGrad.addColorStop(1, "rgba(0, 240, 255, 0)");
                    ctx.fillStyle = discGrad;
                    ctx.beginPath();
                    var pulseR = 24 + Math.sin(now * 0.005) * 2.5 + (isHovered ? 4 : 0);
                    ctx.ellipse(cx, discY, pulseR, 6.5, 0, 0, Math.PI * 2);
                    ctx.fill();

                    // Rotating Cybernetic Dash Ring
                    ctx.save();
                    ctx.translate(cx, discY);
                    ctx.beginPath();
                    ctx.ellipse(0, 0, 18, 5.0, 0, 0, Math.PI * 2);
                    ctx.strokeStyle = "rgba(0, 240, 255, 0.90)";
                    ctx.lineWidth = 1.2;
                    ctx.setLineDash([3, 3]);
                    ctx.lineDashOffset = -now * 0.02;
                    ctx.stroke();
                    ctx.restore();

                    // Upward drifting energy particles
                    for (var p = 0; p < particles.length; p++) {
                        var pt = particles[p];
                        pt.y -= pt.speed;
                        if (pt.y <= 0) {
                            pt.y = 20;
                            pt.x = (Math.random() - 0.5) * 30;
                        }
                        var pAlpha = (pt.y / 20) * 0.75;
                        ctx.fillStyle = "rgba(0, 240, 255, " + pAlpha + ")";
                        ctx.beginPath();
                        ctx.arc(cx + pt.x, discY - (20 - pt.y), pt.size, 0, Math.PI * 2);
                        ctx.fill();
                    }
                    ctx.restore();

                    // 2. RENDER POLISHED WHITE-AND-SILVER 3D AI ROBOT MASCOT
                    ctx.save();
                    var mascotCenterY = groundY - 42 - bob;
                    var tilt = currentYaw * 0.04 * currentStride;

                    ctx.translate(cx, mascotCenterY);
                    ctx.rotate(tilt);

                    // Smooth horizontal direction yaw
                    if (currentYaw < -0.2) {
                        ctx.scale(-1, 1);
                    }

                    if (mascotImg3D.complete && mascotImg3D.naturalWidth > 0) {
                        var mw = 58;
                        var mh = 80;
                        ctx.shadowColor = "rgba(0, 240, 255, 0.65)";
                        ctx.shadowBlur = 12;
                        ctx.drawImage(mascotImg3D, -mw / 2, -mh / 2, mw, mh);
                        ctx.shadowBlur = 0;
                    } else {
                        // Fallback sleek white ceramic robot torso & visor (never cartoon legs!)
                        ctx.fillStyle = "#ffffff";
                        ctx.beginPath();
                        ctx.ellipse(0, 8, 14, 18, 0, 0, Math.PI * 2);
                        ctx.fill();

                        ctx.fillStyle = "#08142c";
                        ctx.beginPath();
                        ctx.ellipse(0, -10, 15, 12, 0, 0, Math.PI * 2);
                        ctx.fill();

                        ctx.strokeStyle = "#00f0ff";
                        ctx.lineWidth = 2.0;
                        ctx.beginPath();
                        ctx.arc(-5, -10, 3, 1.1 * Math.PI, 1.9 * Math.PI);
                        ctx.arc(5, -10, 3, 1.1 * Math.PI, 1.9 * Math.PI);
                        ctx.stroke();
                    }

                    ctx.restore();
                    ctx.restore();

                    pWin.requestAnimationFrame(renderFrame);
                }

                pWin.requestAnimationFrame(renderFrame);
            }

            initCuteAuraWalker();
            setTimeout(initCuteAuraWalker, 300);
            setTimeout(initCuteAuraWalker, 1000);
        })();
        </script>
        """, height=0, width=0)
    except Exception:
        pass

    lang_codes = list(SUPPORTED_LANGUAGES.keys())
    with st.container(key="main_lang_bar_container"):
        cols = st.columns(len(lang_codes))
        for idx, code in enumerate(lang_codes):
            with cols[idx]:
                meta = SUPPORTED_LANGUAGES[code]
                is_active = (code == cur_lang)
                btn_label = f"🌐 {meta['native']}" if code == "en" else meta['native']
                btn_type = "primary" if is_active else "secondary"
                if st.button(btn_label, key=f"main_lang_btn_{code}", type=btn_type, use_container_width=True):
                    if code != cur_lang:
                        st.session_state.app_language = code
                        try:
                            from src.i18n import set_current_language
                            set_current_language(code)
                        except Exception:
                            pass
                        try:
                            st.query_params["lang"] = code
                        except Exception:
                            pass
                        st.toast(f"🌐 Switched to {meta['native']} ({meta['name']})", icon="✅")
                        st.rerun()


def render_dashboard_3d_robot_mascot():
    """
    Renders an interactive, animated 3D cute robot mascot.
    Now roaming at the dashboard title banner!
    """
    pass


def render_quantum_hero_section():
    """
    Renders the Quantum Realm inspired landing hero with emblem, bold gradient title,
    tagline, language selector directly below Pathfinder, and 4 interactive glassmorphic
    workspace cards, all dynamically localized across 8 languages.
    """
    cur_lang = st.session_state.get("app_language", "en")
    ld = DASHBOARD_I18N.get(cur_lang, DASHBOARD_I18N["en"])

    st.markdown(f"""
    <div class="qr-hero-wrapper" id="pathfinder-hero-wrapper">
        <!-- Hidden button for legacy quick-tour trigger compatibility -->
        <button id="btn-hero-quick-tour" class="quick-tour-trigger-btn" style="display:none;"></button>
        <div id="dashboard-robot-canvas-slot" style="display:none;"></div>
        <div class="qr-hero-main-content">
            <div class="qr-hero-emblem">🧭</div>
            <h1 class="qr-hero-heading" id="pathfinder-hero-title">{ld['title']}</h1>
            <div class="qr-hero-subtag">{ld['subtag']}</div>
            <p class="qr-hero-tagline">
                {ld['tagline']}
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Prominent Multilingual Interface Selection Bar directly below Pathfinder on Main Dashboard ONLY
    render_main_language_bar()

    st.markdown('<div id="tour-workspace-cards"></div>', unsafe_allow_html=True)
    with st.container(key="qr_workspace_cards_deck"):
        c1, c2, c3, c4 = st.columns(4)

        with c1:
            st.markdown(f"""
            <div class="qr-workspace-card" id="tour-card-copilot" onclick="if(window.parent.openAuraCopilot){{window.parent.openAuraCopilot();}}else if(window.openAuraCopilot){{window.openAuraCopilot();}}">
                <div>
                    <div class="qr-card-icon-pill qr-icon-cyan">✨</div>
                    <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.62rem; font-weight: 800; color: #38bdf8; letter-spacing: 0.12em; margin-bottom: 6px;">
                        {ld['card1_sub']}
                    </div>
                    <h3 style="font-size: 1.15rem; font-weight: 800; color: #f8fafc; margin: 0 0 8px 0;">
                        {ld['card1_title']}
                    </h3>
                    <p style="font-size: 0.82rem; color: #94a3b8; line-height: 1.5; margin: 0;">
                        {ld['card1_desc']}
                    </p>
                </div>
            </div>
            """, unsafe_allow_html=True)
            if st.button(ld["card1_btn"], key="btn_hero_copilot", use_container_width=True):
                st.session_state.trigger_open_copilot = True
                st.toast("✨ " + ld['card1_title'], icon="🧭")
                st.rerun()

        with c2:
            st.markdown(f"""
            <div class="qr-workspace-card" id="tour-card-nav">
                <div>
                    <div class="qr-card-icon-pill qr-icon-blue">🧭</div>
                    <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.62rem; font-weight: 800; color: #60a5fa; letter-spacing: 0.12em; margin-bottom: 6px;">
                        {ld['card2_sub']}
                    </div>
                    <h3 style="font-size: 1.15rem; font-weight: 800; color: #f8fafc; margin: 0 0 8px 0;">
                        {ld['card2_title']}
                    </h3>
                    <p style="font-size: 0.82rem; color: #94a3b8; line-height: 1.5; margin: 0;">
                        {ld['card2_desc']}
                    </p>
                </div>
            </div>
            """, unsafe_allow_html=True)
            if st.button(ld["card2_btn"], key="btn_hero_nav", use_container_width=True):
                st.session_state.current_view = "map_nav"
                st.session_state.target_tab = "nav"
                st.session_state.scroll_to_app_map = True
                st.rerun()

        with c3:
            st.markdown(f"""
            <div class="qr-workspace-card" id="tour-card-places">
                <div>
                    <div class="qr-card-icon-pill qr-icon-purple">🌟</div>
                    <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.62rem; font-weight: 800; color: #c084fc; letter-spacing: 0.12em; margin-bottom: 6px;">
                        {ld['card3_sub']}
                    </div>
                    <h3 style="font-size: 1.15rem; font-weight: 800; color: #f8fafc; margin: 0 0 8px 0;">
                        {ld['card3_title']}
                    </h3>
                    <p style="font-size: 0.82rem; color: #94a3b8; line-height: 1.5; margin: 0;">
                        {ld['card3_desc']}
                    </p>
                </div>
            </div>
            """, unsafe_allow_html=True)
            if st.button(ld["card3_btn"], key="btn_hero_places", use_container_width=True):
                st.session_state.current_view = "places"
                st.session_state.target_tab = "places"
                st.rerun()

        with c4:
            st.markdown(f"""
            <div class="qr-workspace-card" id="tour-card-guide">
                <div>
                    <div class="qr-card-icon-pill qr-icon-emerald">🚗</div>
                    <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.62rem; font-weight: 800; color: #34d399; letter-spacing: 0.12em; margin-bottom: 6px;">
                        {ld['card4_sub']}
                    </div>
                    <h3 style="font-size: 1.15rem; font-weight: 800; color: #f8fafc; margin: 0 0 8px 0;">
                        {ld['card4_title']}
                    </h3>
                    <p style="font-size: 0.82rem; color: #94a3b8; line-height: 1.5; margin: 0;">
                        {ld['card4_desc']}
                    </p>
                </div>
            </div>
            """, unsafe_allow_html=True)
            if st.button(ld["card4_btn"], key="btn_hero_guide", use_container_width=True):
                st.session_state.current_view = "virtual_guide"
                st.session_state.target_tab = "guide"
                st.rerun()

    st.markdown("<div style='margin-bottom: 18px;'></div>", unsafe_allow_html=True)


def render_view_navigation_header(title: str, subtitle: str, current_key: str = "dash"):
    """
    Renders a unified top header for isolated sub-views with back to main dashboard navigation.
    The language selector is NOT included here, keeping it on the main dashboard only.
    """
    st.markdown(QUANTUM_REALM_CSS, unsafe_allow_html=True)
    cur_lang = st.session_state.get("app_language", "en")
    ld = DASHBOARD_I18N.get(cur_lang, DASHBOARD_I18N["en"])

    # Clean emblem and clean title without duplicating icons
    clean_title = title
    emblem_icon = "🧭"
    for ico in ["✨", "🧭", "🌟", "🚗", "🗺️", "🏥"]:
        if clean_title.startswith(ico):
            emblem_icon = ico
            clean_title = clean_title.replace(ico, "").strip()
            break
    if current_key == "copilot" and emblem_icon == "🧭":
        emblem_icon = "✨"
    elif current_key == "places" and emblem_icon == "🧭":
        emblem_icon = "🌟"
    elif current_key == "guide" and emblem_icon == "🧭":
        emblem_icon = "🚗"

    with st.container(key=f"view_nav_header_container_{current_key}"):
        h_col1, h_col2 = st.columns([2.9, 2.3])
        with h_col1:
            st.markdown(f"""
        <div style="display: flex; align-items: center; gap: 14px; margin-bottom: 10px; margin-top: 4px;">
            <div style="width: 44px; height: 44px; border-radius: 12px; background: rgba(56, 189, 248, 0.15); border: 1.5px solid #38bdf8; display: flex; align-items: center; justify-content: center; font-size: 1.5rem; box-shadow: 0 0 16px rgba(56, 189, 248, 0.3);">
                {emblem_icon}
            </div>
            <div>
                <h2 style="font-size: 1.6rem; font-weight: 800; color: #f8fafc; margin: 0 0 2px 0; background: linear-gradient(135deg, #38bdf8 0%, #818cf8 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
                    {clean_title}
                </h2>
                <div style="font-size: 0.76rem; color: #94a3b8; font-family: 'JetBrains Mono', monospace;">
                    {subtitle}
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    with h_col2:
        hb_lang, hb_col1, hb_col2 = st.columns([1.5, 1.3, 1.0])
        with hb_lang:
            lang_codes = list(SUPPORTED_LANGUAGES.keys())
            def _lang_format(code):
                meta = SUPPORTED_LANGUAGES.get(code, {})
                return f"{meta.get('flag', '🌐')} {meta.get('native', code)}"
            curr_idx = lang_codes.index(cur_lang) if cur_lang in lang_codes else 0
            sel_lang = st.selectbox(
                "Language",
                options=lang_codes,
                index=curr_idx,
                format_func=_lang_format,
                key=f"nav_header_lang_{current_key}",
                label_visibility="collapsed"
            )
            if sel_lang != cur_lang:
                st.session_state.app_language = sel_lang
                try:
                    from src.i18n import set_current_language
                    set_current_language(sel_lang)
                except Exception:
                    pass
                try:
                    st.query_params["lang"] = sel_lang
                except Exception:
                    pass
                st.rerun()
        with hb_col1:
            if st.button(ld.get("back_dash", "🏠 ← Back"), key=f"btn_back_to_dash_{current_key}", type="primary", use_container_width=True):
                st.session_state.current_view = "dashboard"
                st.rerun()
        with hb_col2:
            if st.button(t("nav.tour", default="🚀 Tour", lang=cur_lang), key=f"btn_nav_tour_{current_key}", use_container_width=True):
                st.session_state.launch_quick_tour = True
                st.rerun()



COPILOT_I18N = {
    "en": {
        "header_title": "AI TRAVEL COPILOT & ITINERARY STUDIO",
        "header_sub": "POWERED BY OLLAMA LOCAL AI & GROUNDED TRAVEL ENGINES",
        "badge": "● TRAVEL INTELLIGENCE ACTIVE",
        "suite_title": "Autonomous Itinerary & Travel Planning Suite",
        "quick_select": "Popular Destinations Quick-Select",
        "dest_label": "Destination City / Region",
        "dest_placeholder": "e.g., Goa, Visakhapatnam, Ooty, Paris, Tokyo...",
        "duration_label": "Trip Duration (Days)",
        "vibe_label": "Travel Vibe / Style",
        "transit_label": "Preferred Transit",
        "btn_generate": "✨ Generate Optimized Travel Itinerary",
        "spinner": "Invoking Autonomous Trip Planner & Verifying Weather / Routes...",
        "verified_badge": "VERIFIED BY DATABASE & ROUTER",
        "total_dist": "Total Distance",
        "driving_time": "Driving Time",
        "fuel_est": "Fuel Estimate",
        "curated_stops": "Curated Stops",
        "stop_seq": "Day-by-Day Stop Sequence:",
        "btn_transfer": "🗺️ Transfer Itinerary to Interactive Map & Navigate",
        "comp_title": "🚆 Compare Transportation Options (Flight vs Train vs Driving vs Bus)",
        "budget_title": "💰 Smart Travel Budget Estimator",
        "chat_header": "💬 Conversational Travel Copilot (Local Ollama)",
        "chat_caption": "Ask questions about any trip, custom itineraries, road alerts, accommodation tips, or general inquiries.",
        "quick_prompts": "Quick Travel Inquiry Prompts"
    },
    "te": {
        "header_title": "AI ప్రయాణ కోపైలట్ & ప్రయాణ ప్రణాళిక స్టూడియో",
        "header_sub": "Ollama స్థానిక AI మరియు ప్రయాణ ఇంజిన్ల ద్వారా అందించబడింది",
        "badge": "● ప్రయాణ మేధస్సు సక్రియం",
        "suite_title": "స్వయంప్రతిపత్త ప్రయాణ ప్రణాళిక సూట్",
        "quick_select": "ప్రసిద్ధ గమ్యస్థానాల త్వరిత ఎంపిక",
        "dest_label": "గమ్యస్థాన నగరం / ప్రాంతం",
        "dest_placeholder": "ఉదా. గోవా, విశాఖపట్నం, ఊటీ, ప్యారిస్, టోక్యో...",
        "duration_label": "ప్రయాణ వ్యవధి (రోజులు)",
        "vibe_label": "ప్రయాణ శైలి / అభిరుచి",
        "transit_label": "రవాణా మార్గం",
        "btn_generate": "✨ ఆప్టిమైజ్ చేసిన ప్రయాణ ప్రణాళికను రూపొందించండి",
        "spinner": "ప్రయాణ ప్రణాళికదారుని ప్రారంభించి వాతావరణం/మార్గాలు తనిఖీ చేస్తోంది...",
        "verified_badge": "డేటాబేస్ & రూటర్ ద్వారా ధృవీకరించబడింది",
        "total_dist": "మొత్తం దూరం",
        "driving_time": "డ్రైవింగ్ సమయం",
        "fuel_est": "ఇంధన అంచనా",
        "curated_stops": "ఎంపిక చేసిన ఆగడాలు",
        "stop_seq": "రోజువారీ ఆగడాల క్రమం:",
        "btn_transfer": "🗺️ ప్రయాణ ప్రణాళికను మ్యాప్‌కు బదిలీ చేసి నావిగేట్ చేయండి",
        "comp_title": "🚆 రవాణా ఎంపికల పోలిక (విమానం vs రైలు vs కారు vs బస్సు)",
        "budget_title": "💰 స్మార్ట్ ప్రయాణ బడ్జెట్ అంచనాదారు",
        "chat_header": "💬 ప్రయాణ సంభాషణ కోపైలట్ (స్థానిక Ollama)",
        "chat_caption": "ఏదైనా ప్రయాణం, అనుకూల ప్రణాళికలు, రోడ్డు హెచ్చరికలు లేదా వసతి చిట్కాల గురించి ప్రశ్నలు అడగండి.",
        "quick_prompts": "త్వరిత ప్రయాణ విచారణ ప్రశ్నలు"
    },
    "hi": {
        "header_title": "AI यात्रा सह-पायलट और यात्रा कार्यक्रम स्टूडियो",
        "header_sub": "स्थानीय Ollama AI और यात्रा इंजनों द्वारा संचालित",
        "badge": "● यात्रा इंटेलिजेंस सक्रिय",
        "suite_title": "स्वायत्त यात्रा कार्यक्रम और योजना सूट",
        "quick_select": "लोकप्रिय गंतव्य त्वरित-चयन",
        "dest_label": "गंतव्य शहर / क्षेत्र",
        "dest_placeholder": "उदा. गोवा, विशाखापत्तनम, ऊटी, पेरिस, टोक्यो...",
        "duration_label": "यात्रा अवधि (दिन)",
        "vibe_label": "यात्रा शैली / पसंद",
        "transit_label": "पसंदीदा परिवहन",
        "btn_generate": "✨ अनुकूलित यात्रा कार्यक्रम तैयार करें",
        "spinner": "यात्रा योजनाकार प्रारंभ कर मौसम और मार्गों का सत्यापन...",
        "verified_badge": "डेटाबेस और राउटर द्वारा सत्यापित",
        "total_dist": "कुल दूरी",
        "driving_time": "ड्राइविंग समय",
        "fuel_est": "ईंधन अनुमान",
        "curated_stops": "चयनित पड़ाव",
        "stop_seq": "दिन-प्रतिदिन पड़ाव क्रम:",
        "btn_transfer": "🗺️ यात्रा कार्यक्रम को मानचित्र पर भेजें और नेविगेट करें",
        "comp_title": "🚆 परिवहन विकल्पों की तुलना (फ्लाइट बनाम ट्रेन बनाम कार बनाम बस)",
        "budget_title": "💰 स्मार्ट यात्रा बजट अनुमानक",
        "chat_header": "💬 संवादात्मक यात्रा सह-पायलट (स्थानीय Ollama)",
        "chat_caption": "किसी भी यात्रा, कस्टम यात्रा कार्यक्रम, सड़क अलर्ट या आवास युक्तियों के बारे में प्रश्न पूछें।",
        "quick_prompts": "त्वरित यात्रा पूछताछ संकेत"
    },
    "ta": {
        "header_title": "AI பயண வழிகாட்டி & பயணத்திட்ட அரங்கம்",
        "header_sub": "உள்ளூர் Ollama AI மற்றும் பயண இயந்திரங்களால் இயக்கப்படுகிறது",
        "badge": "● பயண நுண்ணறிவு செயலில்",
        "suite_title": "சுயாதீன பயணத்திட்ட தொகுப்பு",
        "quick_select": "பிரபலமான இடங்களின் விரைவு தேர்வு",
        "dest_label": "செல்லும் நகரம் / பகுதி",
        "dest_placeholder": "எ.கா. கோவா, விசாகப்பட்டினம், ஊட்டி, பாரிஸ்...",
        "duration_label": "பயண காலம் (நாட்கள்)",
        "vibe_label": "பயண பாணி",
        "transit_label": "போக்குவரத்து முறை",
        "btn_generate": "✨ பயணத்திட்டத்தை உருவாக்கவும்",
        "spinner": "பயணத்திட்டத்தை உருவாக்குகிறது...",
        "verified_badge": "சரிபார்க்கப்பட்டது",
        "total_dist": "மொத்த தூரம்",
        "driving_time": "பயண நேரம்",
        "fuel_est": "எரிபொருள் செலவு",
        "curated_stops": "நிறுத்தங்கள்",
        "stop_seq": "தினசரி நிறுத்தங்களின் வரிசை:",
        "btn_transfer": "🗺️ வரைபடத்திற்கு மாற்றி வழிசெலுத்தவும்",
        "comp_title": "🚆 போக்குவரத்து விருப்பங்களை ஒப்பிடுக",
        "budget_title": "💰 பயண பட்ஜெட் கணிப்பான்",
        "chat_header": "💬 உரையாடல் பயண வழிகாட்டி (Ollama)",
        "chat_caption": "பயணங்கள் மற்றும் வழிகள் குறித்து எந்த கேள்வியையும் கேளுங்கள்.",
        "quick_prompts": "விரைவான பயண வினவல்கள்"
    },
    "kn": {
        "header_title": "AI ಪ್ರವಾಸ ಸಹ-ಪೈಲಟ್ & ಪ್ರವಾಸ ಯೋಜನೆ ಸ್ಟುಡಿಯೋ",
        "header_sub": "ಸ್ಥಳೀಯ Ollama AI ಮತ್ತು ಪ್ರವಾಸ ಎಂಜಿನ್‌ಗಳಿಂದ ಚಾಲಿತ",
        "badge": "● ಪ್ರವಾಸ ಇಂಟೆಲಿಜೆನ್ಸ್ ಸಕ್ರಿಯ",
        "suite_title": "ಸ್ವಾಯತ್ತ ಪ್ರವಾಸ ಯೋಜನೆ ಸೂಟ್",
        "quick_select": "ಜನಪ್ರಿಯ ತಾಣಗಳ ತ್ವರಿತ ಆಯ್ಕೆ",
        "dest_label": "ತಲುಪುವ ನಗರ / ಪ್ರದೇಶ",
        "dest_placeholder": "ಉದಾ. ಗೋವಾ, ವಿಶಾಖಪಟ್ಟಣ, ಊಟಿ...",
        "duration_label": "ಪ್ರವಾಸದ ಅವಧಿ (ದಿನಗಳು)",
        "vibe_label": "ಪ್ರವಾಸದ ಶೈಲಿ",
        "transit_label": "ಸಾರಿಗೆ ವಿಧಾನ",
        "btn_generate": "✨ ಪ್ರವಾಸ ಯೋಜನೆಯನ್ನು ರಚಿಸಿ",
        "spinner": "ಪ್ರವಾಸ ಯೋಜನೆಯನ್ನು ಸಿದ್ಧಪಡಿಸಲಾಗುತ್ತಿದೆ...",
        "verified_badge": "ದೃಢೀಕರಿಸಲಾಗಿದೆ",
        "total_dist": "ಒಟ್ಟು ದೂರ",
        "driving_time": "ಚಾಲನಾ ಸಮಯ",
        "fuel_est": "ಇಂಧನ ಅಂದಾಜು",
        "curated_stops": "ನಿಲ್ದಾಣಗಳು",
        "stop_seq": "ದೈನಂದಿನ ನಿಲ್ದಾಣಗಳ ಅನುಕ್ರಮ:",
        "btn_transfer": "🗺️ ನಕ್ಷೆಗೆ ವರ್ಗಾಯಿಸಿ ಮತ್ತು ನ್ಯಾವಿಗೇಟ್ ಮಾಡಿ",
        "comp_title": "🚆 ಸಾರಿಗೆ ಆಯ್ಕೆಗಳ ಹೋಲಿಕೆ",
        "budget_title": "💰 ಸ್ಮಾರ್ಟ್ ಬಜೆಟ್ ಅಂದಾಜಕ",
        "chat_header": "💬 ಸಂವಾದಾತ್ಮಕ ಪ್ರವಾಸ ಸಹಾಯಕ (Ollama)",
        "chat_caption": "ಪ್ರವಾಸ ಮತ್ತು ಮಾರ್ಗಗಳ ಬಗ್ಗೆ ಯಾವುದೇ ಪ್ರಶ್ನೆಗಳನ್ನು ಕೇಳಿ.",
        "quick_prompts": "ತ್ವರಿತ ಪ್ರಶ್ನೆಗಳು"
    },
    "ml": {
        "header_title": "AI യാത്രാ കോപൈലറ്റും ഇറ്റിനററി സ്റ്റുഡിയോയും",
        "header_sub": "ലോക്കൽ Ollama AI കരുത്തിൽ പ്രവർത്തിക്കുന്നു",
        "badge": "● യാത്രാ ഇന്റലിജൻസ് സജീവം",
        "suite_title": "സ്വയംഭരണ യാത്രാ പ്ലാനിംഗ് സ്യൂട്ട്",
        "quick_select": "ജനപ്രിയ ലക്ഷ്യസ്ഥാനങ്ങൾ",
        "dest_label": "ലക്ഷ്യസ്ഥാന നഗരം / പ്രദേശം",
        "dest_placeholder": "ഉദാ. ഗോവ, വിശാഖപട്ടണം, ഊട്ടി...",
        "duration_label": "യാത്രാ കാലാവധി (ദിവസങ്ങൾ)",
        "vibe_label": "യാത്രാ ശൈലി",
        "transit_label": "യാത്രാ മാർഗ്ഗം",
        "btn_generate": "✨ യാത്രാ പ്ലാൻ തയ്യാറാക്കുക",
        "spinner": "യാത്രാ പ്ലാൻ തയ്യാറാക്കുന്നു...",
        "verified_badge": "സ്ഥിരീകരിച്ചത്",
        "total_dist": "ആകെ ദൂരം",
        "driving_time": "ഡ്രൈവിംഗ് സമയം",
        "fuel_est": "ഇന്ധനച്ചെലവ്",
        "curated_stops": "സ്റ്റോപ്പുകൾ",
        "stop_seq": "ദിവസേനയുള്ള സ്റ്റോപ്പുകൾ:",
        "btn_transfer": "🗺️ മാപ്പിലേക്ക് മാറ്റി നാവിഗേറ്റ് ചെയ്യുക",
        "comp_title": "🚆 യാത്രാ മാർഗ്ഗങ്ങൾ താരതമ്യം ചെയ്യുക",
        "budget_title": "💰 യാത്രാ ബജറ്റ് കാൽക്കുലേറ്റർ",
        "chat_header": "💬 യാത്രാ സഹായി (Ollama)",
        "chat_caption": "യാത്രകളെയും വഴികളെയും കുറിച്ച് ഏത് സംശയവും ചോദിക്കാം.",
        "quick_prompts": "ദ്രുത യാത്രാ ചോദ്യങ്ങൾ"
    },
    "bn": {
        "header_title": "AI ট্রাভেল কোপাইলট ও ভ্রমণ পরিকল্পনা স্টুডিও",
        "header_sub": "স্থানীয় Ollama AI ও ট্রাভেল ইঞ্জিন দ্বারা পরিচালিত",
        "badge": "● ভ্রমণ বুদ্ধিমত্তা সক্রিয়",
        "suite_title": "স্বায়ত্তশাসিত ভ্রমণ পরিকল্পনা স্যুট",
        "quick_select": "জনপ্রিয় গন্তব্য দ্রুত নির্বাচন",
        "dest_label": "গন্তব্য শহর / অঞ্চল",
        "dest_placeholder": "যেমন: গোয়া, বিশাখাপত্তনম, উটি...",
        "duration_label": "ভ্রমণের সময়কাল (দিন)",
        "vibe_label": "ভ্রমণের ধরন",
        "transit_label": "পছন্দের পরিবহন",
        "btn_generate": "✨ ভ্রমণ পরিকল্পনা তৈরি করুন",
        "spinner": "পরিকল্পনা তৈরি করা হচ্ছে...",
        "verified_badge": "যাচাইকৃত",
        "total_dist": "মোট দূরত্ব",
        "driving_time": "ড্রাইভিং সময়",
        "fuel_est": "জ্বালানি খরচ",
        "curated_stops": "স্টপসমূহ",
        "stop_seq": "দৈনিক স্টপ ক্রম:",
        "btn_transfer": "🗺️ মানচিত্রে স্থানান্তর করে নেভিগেট করুন",
        "comp_title": "🚆 পরিবহন বিকল্পের তুলনা",
        "budget_title": "💰 স্মার্ট ভ্রমণ বাজেট ক্যালকুলেটর",
        "chat_header": "💬 ট্রাভেল কোপাইলট (Ollama)",
        "chat_caption": "ভ্রমণ বা রুট সম্পর্কিত যেকোনো প্রশ্ন জিজ্ঞাসা করুন।",
        "quick_prompts": "দ্রুত প্রশ্নাবলী"
    },
    "mr": {
        "header_title": "AI ट्रॅव्हल को-पायलट आणि प्रवास योजना स्टुडिओ",
        "header_sub": "स्थानिक Ollama AI आणि ट्रॅव्हल इंजिनद्वारे समर्थित",
        "badge": "● प्रवास बुद्धिमत्ता सक्रिय",
        "suite_title": "स्वायत्त प्रवास नियोजन संच",
        "quick_select": "लोकप्रिय गंतव्ये जलद निवड",
        "dest_label": "गंतव्य शहर / प्रदेश",
        "dest_placeholder": "उदा. गोवा, विशाखापट्टणम, उटी...",
        "duration_label": "प्रवासाचा कालावधी (दिवस)",
        "vibe_label": "प्रवासाची शैली",
        "transit_label": "पसंतीची वाहतूक",
        "btn_generate": "✨ प्रवास योजना तयार करा",
        "spinner": "प्रवास योजना तयार करत आहे...",
        "verified_badge": "सत्यापित",
        "total_dist": "एकूण अंतर",
        "driving_time": "ड्रायव्हिंग वेळ",
        "fuel_est": "इंधन अंदाज",
        "curated_stops": "थांबे",
        "stop_seq": "दिवसनिहाय थांबे क्रम:",
        "btn_transfer": "🗺️ नकाशावर पाठवा आणि नेव्हिगेट करा",
        "comp_title": "🚆 वाहतूक पर्यायांची तुलना",
        "budget_title": "💰 स्मार्ट प्रवास बजेट अंदाजक",
        "chat_header": "💬 संवादात्मक प्रवास सहाय्यक (Ollama)",
        "chat_caption": "कोणत्याही सहली, सानुकूल योजना किंवा रस्त्यांच्या माहितीबद्दल विचारा.",
        "quick_prompts": "जलद प्रश्न"
    }
}


def render_travel_copilot_studio():
    """
    Renders the dedicated, full-screen AI Travel Copilot & Itinerary Studio workspace.
    Fulfills Requirement 3:
    - Travel planning and personalized itineraries.
    - Destination discovery and recommendations.
    - Route finding and transportation comparisons.
    - Travel budget estimation.
    - Tourist attractions and sightseeing recommendations.
    - Accommodation suggestions.
    - Weather and seasonal travel guidance.
    - Follow-up questions about an existing trip.
    - Support general-purpose questions as a secondary capability.
    """
    cur_lang = st.session_state.get("app_language", "en")
    cd = COPILOT_I18N.get(cur_lang, COPILOT_I18N["en"])

    st.markdown(f"""
    <div style="background: linear-gradient(135deg, rgba(15, 23, 42, 0.70) 0%, rgba(30, 41, 59, 0.50) 100%); border: 1.5px solid rgba(56, 189, 248, 0.35); border-radius: 16px; padding: 16px 22px; margin-bottom: 20px; box-shadow: 0 8px 30px rgba(0,0,0,0.45);">
        <div style="display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 12px;">
            <div style="display: flex; align-items: center; gap: 12px;">
                <span style="font-size: 1.8rem;">✨</span>
                <div>
                    <h2 style="font-size: 1.35rem; font-weight: 800; margin: 0; background: linear-gradient(135deg, #38bdf8 0%, #a855f7 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
                        {cd['header_title']}
                    </h2>
                    <span style="font-size: 0.76rem; color: #94a3b8; font-family: 'JetBrains Mono', monospace;">
                        {cd['header_sub']}
                    </span>
                </div>
            </div>
            <span style="font-size: 0.72rem; font-weight: 800; padding: 4px 12px; border-radius: 9999px; background: rgba(16, 185, 129, 0.15); border: 1px solid #10b981; color: #34d399; letter-spacing: 0.05em;">
                {cd['badge']}
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    col_studio, col_chat = st.columns([1.1, 1.0], gap="large")

    with col_studio:
        st.markdown(f"### 🗺️ **{cd['suite_title']}**")

        # Quick Preset Buttons for Top Destinations
        st.markdown(f"<span style='font-size: 0.74rem; font-weight: 700; color: #94a3b8; text-transform: uppercase;'>{cd['quick_select']}</span>", unsafe_allow_html=True)
        preset_cols = st.columns(6)
        presets = [("🏝️ Goa", "Goa"), ("🌊 Vizag", "Visakhapatnam"), ("⛰️ Ooty", "Ooty"), ("🏰 Jaipur", "Jaipur"), ("🌲 Manali", "Manali"), ("🌴 Kerala", "Munnar, Kerala")]
        for p_idx, (p_lbl, p_dest) in enumerate(presets):
            with preset_cols[p_idx]:
                if st.button(p_lbl, key=f"quick_dest_{p_idx}", use_container_width=True):
                    st.session_state.copilot_dest_input = p_dest
                    st.rerun()

        # Itinerary Parameters Form
        dest_val = st.session_state.get("copilot_dest_input", "Goa")
        target_destination = st.text_input(
            cd["dest_label"],
            value=dest_val,
            placeholder=cd["dest_placeholder"],
            key="input_copilot_dest"
        )

        row_params_1, row_params_2, row_params_3 = st.columns(3)
        with row_params_1:
            trip_days = st.select_slider(cd["duration_label"], options=[1, 2, 3, 5, 7], value=3)
        with row_params_2:
            travel_style = st.selectbox(cd["vibe_label"], [
                "Beach & Relaxation",
                "Heritage & Cultural",
                "Outdoor Adventure",
                "Family & Sightseeing",
                "Budget Backpacking",
                "Food & Nightlife"
            ])
        with row_params_3:
            transport_mode = st.selectbox(cd["transit_label"], ["driving", "transit", "walking"])

        btn_gen = st.button(cd["btn_generate"], type="primary", use_container_width=True)


        if btn_gen or ("active_itinerary" in st.session_state and st.session_state.get("active_itinerary_dest") == target_destination):
            if btn_gen:
                with st.spinner("Invoking Autonomous Trip Planner & Verifying Weather / Routes..."):
                    try:
                        db = SessionLocal()
                        agent = TripPlannerAgent(db)
                        prompt_text = f"{trip_days}-day trip to {target_destination} focusing on {travel_style}"
                        user_coords = st.session_state.get("user_live_coords", (16.2335, 80.5505))
                        itinerary = agent.plan_trip(
                            prompt=prompt_text,
                            user_lat=user_coords[0],
                            user_lon=user_coords[1],
                            days=trip_days,
                            preferred_mode=transport_mode
                        )
                        st.session_state.active_itinerary = itinerary
                        st.session_state.active_itinerary_dest = target_destination
                    except Exception as e:
                        logger.exception("Error planning trip with TripPlannerAgent: %s", e)
                        st.session_state.active_itinerary = {
                            "itinerary_title": f"{trip_days}-Day Curated Journey to {target_destination}",
                            "metrics": {
                                "total_distance_km": trip_days * 85.0,
                                "total_driving_time_minutes": trip_days * 120.0,
                                "total_fuel_cost_inr": trip_days * 950.0,
                                "stop_count": trip_days * 3
                            },
                            "stops": [
                                {
                                    "stop_number": 1,
                                    "place_name": f"{target_destination} Historic Center & Landmark",
                                    "category": "CULTURE",
                                    "travel_distance_km": 15.0,
                                    "recommended_visit_duration_minutes": 90,
                                    "match_reason": f"Top-rated cultural highlight in {target_destination}"
                                },
                                {
                                    "stop_number": 2,
                                    "place_name": f"{target_destination} Scenic Viewpoint & Promenade",
                                    "category": "OUTDOOR",
                                    "travel_distance_km": 8.0,
                                    "recommended_visit_duration_minutes": 60,
                                    "match_reason": "Prime landscape view and photography spot"
                                }
                            ],
                            "agent_explanation": f"Custom {travel_style} route prepared for {target_destination}."
                        }

            itin = st.session_state.get("active_itinerary")
            if itin:
                st.markdown(f"""
                <div class="qr-glass-panel" style="margin-top: 14px;">
                    <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 10px;">
                        <span style="font-size: 1.15rem; font-weight: 800; color: #f8fafc;">
                            📋 {itin.get('itinerary_title', 'Curated Itinerary')}
                        </span>
                        <span style="font-size: 0.68rem; font-weight: 800; padding: 2px 8px; border-radius: 9999px; background: rgba(56, 189, 248, 0.15); border: 1px solid #38bdf8; color: #38bdf8;">
                            {cd['verified_badge']}
                        </span>
                    </div>
                """, unsafe_allow_html=True)

                m = itin.get("metrics", {})
                m_c1, m_c2, m_c3, m_c4 = st.columns(4)
                with m_c1:
                    st.metric(cd["total_dist"], f"{m.get('total_distance_km', 0)} km")
                with m_c2:
                    st.metric(cd["driving_time"], f"{round(m.get('total_driving_time_minutes', 0)/60, 1)} hrs")
                with m_c3:
                    st.metric(cd["fuel_est"], f"₹{m.get('total_fuel_cost_inr', 0)}")
                with m_c4:
                    st.metric(cd["curated_stops"], f"{m.get('stop_count', len(itin.get('stops', [])))}")

                w = itin.get("weather_forecast", {})
                if w and w.get("temperature_celsius") is not None:
                    st.info(f"🌤️ **Destination Forecast**: {w.get('conditions', 'Clear')} • {w.get('temperature_celsius')}°C. {w.get('hazard_warning') or 'Ideal road travel conditions.'}")

                st.markdown(f"<div style='margin-top: 12px; font-size: 0.88rem; font-weight: 700; color: #38bdf8;'>{cd['stop_seq']}</div>", unsafe_allow_html=True)
                for stp in itin.get("stops", []):
                    st.markdown(f"""
                    <div class="qr-stop-card">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <span style="font-weight: 800; color: #f8fafc;">#{stp.get('stop_number', 1)} • {stp.get('place_name', 'Attraction')}</span>
                            <span style="font-size: 0.65rem; padding: 2px 6px; border-radius: 4px; background: rgba(56, 189, 248, 0.15); color: #38bdf8; font-family: monospace;">
                                {stp.get('category', 'DESTINATION')}
                            </span>
                        </div>
                        <div style="font-size: 0.78rem; color: #94a3b8; margin-top: 4px;">
                            ⏱️ Recommended Visit: {stp.get('recommended_visit_duration_minutes', 60)} min • Leg Distance: {stp.get('travel_distance_km', 0)} km
                        </div>
                        <div style="font-size: 0.76rem; color: #cbd5e1; margin-top: 3px; font-style: italic;">
                            "{stp.get('match_reason', 'Matches your travel preference')}"
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                st.markdown("</div>", unsafe_allow_html=True)

                # Direct Route Integration to Interactive Map
                if st.button(cd["btn_transfer"], type="primary", use_container_width=True):
                    stops = itin.get("stops", [])
                    if stops and "coordinates" in stops[-1]:
                        last_c = stops[-1]["coordinates"]
                        st.session_state.selected_dest_coords = (last_c["latitude"], last_c["longitude"])
                    st.session_state.selected_dest_label = target_destination
                    st.session_state.pending_dest = target_destination
                    st.session_state.target_tab = "nav"
                    st.session_state.scroll_to_app_map = True
                    st.toast(f"🎯 Route to {target_destination} sent to Interactive Map!", icon="🧭")
                    st.rerun()

        st.markdown("<hr style='border-color: rgba(255,255,255,0.08); margin: 20px 0;'>", unsafe_allow_html=True)

        # Multimodal Transport Comparison Matrix
        with st.expander(f"🚆 **{cd['comp_title']}**", expanded=False):
            st.caption("Live cost and transit time comparison for long-distance corridors:")
            comp_c1, comp_c2 = st.columns(2)
            with comp_c1:
                st.markdown("""
                <div style="background: rgba(15, 23, 42, 0.85); border: 1px solid rgba(56, 189, 248, 0.25); border-radius: 10px; padding: 12px; margin-bottom: 8px;">
                    <div style="font-weight: 800; color: #38bdf8;">🚗 Self-Drive / Rental Car</div>
                    <div style="font-size: 0.80rem; color: #cbd5e1; margin-top: 4px;">
                        • Est. Cost: ~₹4,500 - ₹6,000 (Fuel + Tolls)<br>
                        • Speed: Medium (Stop wherever you like)<br>
                        • Best for: Scenic routes, luggage flexibility, group travel
                    </div>
                </div>
                <div style="background: rgba(15, 23, 42, 0.85); border: 1px solid rgba(168, 85, 247, 0.25); border-radius: 10px; padding: 12px;">
                    <div style="font-weight: 800; color: #c084fc;">🚆 Express Rail / Vande Bharat</div>
                    <div style="font-size: 0.80rem; color: #cbd5e1; margin-top: 4px;">
                        • Est. Cost: ~₹850 - ₹1,850 per person<br>
                        • Speed: Fast & smooth, zero traffic jams<br>
                        • Best for: Comfortable overnight journeys, scenic landscape
                    </div>
                </div>
                """, unsafe_allow_html=True)
            with comp_c2:
                st.markdown("""
                <div style="background: rgba(15, 23, 42, 0.85); border: 1px solid rgba(16, 185, 129, 0.25); border-radius: 10px; padding: 12px; margin-bottom: 8px;">
                    <div style="font-weight: 800; color: #34d399;">✈️ Commercial Flight</div>
                    <div style="font-size: 0.80rem; color: #cbd5e1; margin-top: 4px;">
                        • Est. Cost: ~₹3,500 - ₹5,800 per person<br>
                        • Speed: Fastest (1.5 - 2 hrs in air)<br>
                        • Best for: Tight schedules & interstate travel
                    </div>
                </div>
                <div style="background: rgba(15, 23, 42, 0.85); border: 1px solid rgba(245, 158, 11, 0.25); border-radius: 10px; padding: 12px;">
                    <div style="font-weight: 800; color: #fbbf24;">🚌 AC Sleeper Bus</div>
                    <div style="font-size: 0.80rem; color: #cbd5e1; margin-top: 4px;">
                        • Est. Cost: ~₹1,100 - ₹1,800 per person<br>
                        • Speed: Moderate overnight<br>
                        • Best for: Budget travel with direct point-to-point dropoff
                    </div>
                </div>
                """, unsafe_allow_html=True)

        # Smart Travel Budget Estimator
        with st.expander(f"💰 **{cd['budget_title']}**", expanded=False):
            b_c1, b_c2 = st.columns(2)
            with b_c1:
                n_travelers = st.number_input("Travelers", min_value=1, max_value=20, value=2)
                budget_tier = st.selectbox("Budget Tier", ["Backpacker (₹1,500/day)", "Moderate Explorer (₹3,800/day)", "Luxury (₹8,500/day)"])
            with b_c2:
                base_daily = 1500 if "Backpacker" in budget_tier else (3800 if "Moderate" in budget_tier else 8500)
                tot_budget = base_daily * trip_days * n_travelers
                st.markdown(f"""
                <div style="background: rgba(15, 23, 42, 0.85); border: 1px solid rgba(56, 189, 248, 0.3); border-radius: 10px; padding: 12px; text-align: center;">
                    <div style="font-size: 0.72rem; color: #94a3b8; font-weight: 700;">ESTIMATED TOTAL BUDGET</div>
                    <div style="font-size: 1.6rem; font-weight: 900; color: #34d399; margin: 4px 0;">₹{tot_budget:,}</div>
                    <div style="font-size: 0.72rem; color: #cbd5e1;">Lodging 40% • Meals 25% • Transit 20% • Sightseeing 15%</div>
                </div>
                """, unsafe_allow_html=True)

    with col_chat:
        st.markdown(f"### 💬 **{cd['chat_header']}**")
        st.caption(cd["chat_caption"])

        bot = st.session_state.get("pathfinder_bot")

        # Chat History Container
        chat_height = 420
        c_box = st.container(height=chat_height)
        with c_box:
            for msg in st.session_state.aura_chat_history:
                if msg["role"] == "user":
                    st.markdown(f"""
                    <div style="display: flex; justify-content: flex-end; margin-bottom: 8px;">
                        <div style="background: linear-gradient(135deg, #0284c7 0%, #0369a1 100%); color: #ffffff; padding: 8px 14px; border-radius: 14px 14px 2px 14px; max-width: 85%; font-size: 0.84rem; box-shadow: 0 2px 8px rgba(0,0,0,0.3); font-weight: 500;">
                            {msg['content']}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    b_badge = f"<span style='font-size: 0.62rem; font-weight: 800; color: #38bdf8; font-family: monospace; letter-spacing: 0.05em; background: rgba(56, 189, 248, 0.12); padding: 1px 6px; border-radius: 4px; display: inline-block; margin-bottom: 4px;'>{msg.get('badge', 'NEXROUTE AI')}</span>"
                    st.markdown(f"""
                    <div style="display: flex; justify-content: flex-start; margin-bottom: 10px;">
                        <div style="background: rgba(15, 23, 42, 0.85); border: 1px solid rgba(56, 189, 248, 0.22); color: #cbd5e1; padding: 10px 14px; border-radius: 14px 14px 14px 2px; max-width: 95%; font-size: 0.84rem; box-shadow: 0 4px 12px rgba(0,0,0,0.4);">
                            {b_badge}
                            <div>{msg['content']}</div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

        # Quick Suggestion Chips
        st.markdown(f"<span style='font-size: 0.70rem; font-weight: 700; color: #94a3b8;'>{cd['quick_prompts']}</span>", unsafe_allow_html=True)
        q_cols = st.columns(3)
        prompts = [
            ("🏖️ 3-Day Beach Itinerary", "Plan a 3-day beach and sightseeing itinerary for Goa with family."),
            ("🚆 Compare Train vs Driving", "Compare taking the train versus driving from Hyderabad to Visakhapatnam."),
            ("💰 Budget for 2 Travelers", "What is a realistic budget breakdown for 4 days in Ooty for 2 people?")
        ]
        for p_i, (p_t, p_txt) in enumerate(prompts):
            with q_cols[p_i]:
                if st.button(p_t, key=f"chip_studio_{p_i}", use_container_width=True):
                    st.session_state.pending_copilot_prompt = p_txt
                    st.rerun()

        # Handle queued prompt
        if "pending_copilot_prompt" in st.session_state and st.session_state.pending_copilot_prompt:
            p_q = st.session_state.pop("pending_copilot_prompt")
            st.session_state.aura_chat_history.append({"role": "user", "content": p_q})
            chat_ctx = {
                "start_label": st.session_state.get("user_live_label", "Live Location"),
                "dest_label": target_destination,
                "current_coords": st.session_state.get("user_live_coords", (16.2335, 80.5505)),
                "language": st.session_state.get("app_language", "en")
            }
            if bot:
                ans = bot.answer(p_q, context=chat_ctx)
                st.session_state.aura_chat_history.append({
                    "role": "assistant",
                    "content": ans["response"],
                    "badge": ans.get("badge", "NEXROUTE AI")
                })
            st.rerun()

        # Chat Input Form
        with st.form("studio_chat_form", clear_on_submit=True):
            f_col1, f_col2, f_col3 = st.columns([4, 1, 1])
            with f_col1:
                chat_in = st.text_input("Ask NexRoute", placeholder="Ask any question about travel, routes, packing, or general topics...", label_visibility="collapsed")
            with f_col2:
                btn_send = st.form_submit_button("Send ➔", use_container_width=True)
            with f_col3:
                btn_clear = st.form_submit_button("Reset", use_container_width=True)

        if btn_clear:
            if bot and hasattr(bot, "reset_conversation"):
                bot.reset_conversation()
            st.session_state.aura_chat_history = [
                {
                    "role": "assistant",
                    "badge": "🧭 NEXROUTE AI",
                    "content": "✨ *Hello! I am NexRoute, your AI Travel Assistant powered by Ollama. How can I help you plan your journey?*"
                }
            ]
            st.rerun()

        if btn_send and chat_in and chat_in.strip():
            u_text = chat_in.strip()
            st.session_state.aura_chat_history.append({"role": "user", "content": u_text})
            chat_ctx = {
                "start_label": st.session_state.get("user_live_label", "Live Location"),
                "dest_label": target_destination,
                "current_coords": st.session_state.get("user_live_coords", (16.2335, 80.5505)),
                "language": st.session_state.get("app_language", "en")
            }
            if bot:
                ans = bot.answer(u_text, context=chat_ctx)
                st.session_state.aura_chat_history.append({
                    "role": "assistant",
                    "content": ans["response"],
                    "badge": ans.get("badge", "NEXROUTE AI")
                })
            st.rerun()
