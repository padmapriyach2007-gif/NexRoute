# Pathfinder: Privacy, Location Governance & Security Architecture

---

## 1. Core Privacy Principles

Pathfinder is engineered around strict privacy preservation, data minimization, and transparent location governance. Location data is considered sensitive personal information and is protected through architectural isolation.

### Principles:
1. **Separation of Concerns:** Live in-transit navigation is completely decoupled from anonymous traffic contribution. A user can navigate without consenting to share telemetry.
2. **$k$-Anonymity Aggregation Thresholds:** Individual user telemetry is never displayed as a standalone road condition. Pathfinder requires at least $k = 3$ distinct consenting contributors on a road segment before publishing crowd-observed speeds. If fewer than 3 contributors exist, the system blends partial observations with historical baseline profiles.
3. **Pseudonymous Contribution Identifiers:** Anonymous traffic contributions use client-rotated cryptographic tokens (`session_pseudonym`). No user IDs, emails, IMEI numbers, or hardware IDs are linked to traffic points.
4. **Pedestrian Noise & Drift Filtering:** Speeds below 4.0 km/h are classified as pedestrian/stationary movement and automatically excluded from motor vehicle traffic speed aggregation.
5. **Zero Secret Background Tracking:** Pathfinder never collects coordinates in the background without explicit disclosure, persistent system notifications, and active user consent.

---

## 2. Location Sharing Governance

Pathfinder provides an explicit, user-initiated location sharing subsystem:

- **Time-Limited Sessions:** Every sharing session has a mandatory lifespan (e.g., 15 to 1440 minutes) and automatically expires.
- **Cryptographic Sharing Tokens:** Recipients view location through high-entropy random URL tokens (256-bit entropy via `secrets.token_urlsafe(32)`).
- **No Public Searchability:** Shared locations cannot be indexed, scraped, or queried without the specific token.
- **Instant Revocation:** The sharer can revoke access at any second via `DELETE /api/location-sharing/sessions/{session_id}`, which terminates the token immediately.
- **Auditing:** Active sharing sessions are visible on the user's dashboard with remaining time indicators.

---

## 3. Platform Permission Architecture

### Web Platform (Browser Geolocation API)
- **Permission Action:** Requested exclusively upon explicit user interaction (e.g., clicking "📍 My Location" or starting navigation).
- **Permission Denial Handling:** If the user denies browser permission, Pathfinder gracefully falls back to IP/network coarse regional localization or manual starting point search without degrading other features.
- **Visual Tracking Status:** A glowing green pulse (`.origin-gps-dot`) clearly indicates when satellite/browser GPS is actively queried.

### Android Native Platform (Fused Location Provider)
When deploying the companion Android app (`/android`):
- **Foreground Service with Persistent Notification:** Continuous turn-by-turn navigation runs under an Android Foreground Service with a visible, non-dismissible notification (`Pathfinder is actively navigating`).
- **Permissions:**
  - `ACCESS_FINE_LOCATION`: Required for GPS turn-by-turn accuracy.
  - `ACCESS_COARSE_LOCATION`: Used for general regional search when high precision is unneeded.
  - `FOREGROUND_SERVICE_LOCATION`: Disclosed foreground service type.
  - `ACCESS_BACKGROUND_LOCATION`: Never requested by default; only prompted if the user explicitly turns on geofence arrival alerts.
- **Battery Optimization:** Utilizes passive location listeners when stationary and adjusts polling frequency based on vehicle velocity.

---

## 4. Security & Data Protection Controls

- **Transport Security:** All client-server communication requires HTTPS/TLS 1.3 in production.
- **Authentication:** JWT tokens signed with HMAC-SHA256 (`HS256`) or asymmetric `RS256` keys.
- **SQL Injection Defense:** Strict SQLAlchemy ORM parameterized queries across all database operations.
- **Input Validation:** Strict Pydantic models with type enforcement, coordinate boundary constraints ($-90 \le \text{lat} \le 90$, $-180 \le \text{lon} \le 180$), and sanitize filters.
- **Prompt Injection Defense:** A.U.R.A. AI assistant filters prompt injection attempts, system prompt exfiltration, and maintains strict medical/legal safety boundaries.
