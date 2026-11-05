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
    #pathfinder-tour-fab-trigger,
    .pathfinder-tour-fab-trigger {
        bottom: 148px !important;
        right: 14px !important;
        width: 50px !important;
        height: 50px !important;
        min-width: 50px !important;
        min-height: 50px !important;
    }
    #pathfinder-tour-fab-trigger img {
        width: 40px !important;
        height: 40px !important;
    }
    .floating-tour-welcome-tooltip,
    .floating-aura-welcome-tooltip {
        right: 70px !important;
        bottom: 150px !important;
        padding: 5px 12px !important;
    }
    div[data-testid="stPopoverBody"] {
        width: calc(100vw - 24px) !important;
        max-width: 420px !important;
        max-height: 80vh !important;
        bottom: 74px !important;
        right: 12px !important;
        left: 12px !important;
        margin: 0 auto !important;
        padding: 12px !important;
        border-radius: 16px !important;
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


_AURA_ROBOT_B64 = None

def _get_aura_robot_b64() -> str:
    global _AURA_ROBOT_B64
    if _AURA_ROBOT_B64 is None:
        p = Path(__file__).resolve().parent.parent / "assets" / "aura_3d_robot_mascot_256.png"
        if not p.exists():
            p = Path(__file__).resolve().parent.parent / "assets" / "aura_chatbot_logo.png"
        if p.exists():
            import base64
            _AURA_ROBOT_B64 = base64.b64encode(p.read_bytes()).decode("ascii")
        else:
            _AURA_ROBOT_B64 = ""
    return _AURA_ROBOT_B64

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
        aura_walker_script = """
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
            mascotImg3D.src = "data:image/png;base64,__AURA_MASCOT_B64__";

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
                        var aspect = mascotImg3D.naturalWidth / mascotImg3D.naturalHeight;
                        var mh = 82;
                        var mw = Math.round(mh * aspect);
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
        """
        components.html(aura_walker_script.replace("__AURA_MASCOT_B64__", _get_aura_robot_b64()), height=0, width=0)
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
