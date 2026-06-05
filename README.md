# VR Meeting Room

Immersive virtual meeting room for the Influwealth Sovereign Automation System.
Supports 2D web, 3D WebVR (A-Frame), and full VR via NVIDIA CloudXR streaming.

## Features

- **Multi-room management** — Create, join, and manage meeting rooms
- **WebRTC video/audio** — Peer-to-peer real-time communication
- **3D WebVR** — A-Frame powered 3D meeting space in any browser
- **NVIDIA CloudXR** — Full VR headset streaming (requires NVIDIA GPU server)
- **AI Meeting Assistant** — NIM-powered note-taking, summaries, and Q&A
- **World Themes** — Rooms themed after World Interactive Origins worlds
- **SAP Integration** — Sovereign Agent Protocol for distributed tracing

## Architecture

```
Browser / VR Headset
    ↓ WebRTC / HTTPS
VR Meeting Server (port 7791)
    ├── Room Manager     — Room state, participants, sessions
    ├── NIM Assistant    — AI note-taking via NVIDIA NIM
    ├── CloudXR Bridge   — NVIDIA CloudXR VR streaming
    └── A-Frame Static   — WebVR client (served at /room/<id>)
```

## SAP Integration
- **SAP Node ID**: `vr-meeting-room`
- **Port**: 7791
- **Managed by**: DeepFlex Supervisor (port 8000)

## Quick Start

```bash
pip install -r requirements.txt
cp .env.example .env  # add NVIDIA_API_KEY
uvicorn server:app --port 7791 --reload
```

Open http://localhost:7791 to create a meeting room.

## Room Themes

| Theme | World | Best For |
|-------|-------|----------|
| `boardroom` | Modern | Business meetings |
| `silk-road` | Ancient Silk Road | History education |
| `harlem-jazz` | Harlem Renaissance | Arts education |
| `brooklyn-90s` | Brooklyn 1990s | Community sessions |
| `space-station` | Future | Science & STEM |
| `community-center` | East Flatbush | Local org meetings |

## Environment Variables

```bash
NVIDIA_API_KEY=nvapi-...        # For NIM AI assistant
CLOUDXR_SERVER_URL=...          # NVIDIA CloudXR server (optional)
VR_ROOM_PORT=7791               # HTTP server port
DEEPFLEX_BASE_URL=http://localhost:8000
```
