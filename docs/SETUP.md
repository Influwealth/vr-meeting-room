# VR Meeting Room — Setup Guide

## Quick Start (2 minutes)

```bash
git clone https://github.com/influwealth/vr-meeting-room
cd vr-meeting-room
pip install -r requirements.txt
cp .env.example .env
# Optional: add NVIDIA_API_KEY to .env for AI assistant
uvicorn server:app --port 7791 --reload
```

Open http://localhost:7791 in your browser.

## Features

### Without NVIDIA API Key
- Full room management (create/join/leave)
- WebRTC peer-to-peer video/audio (use browser's built-in)
- A-Frame 3D WebVR scenes
- All 6 room themes
- Chat messaging

### With NVIDIA API Key
All of the above, plus:
- **AI Meeting Assistant** — Ask questions in the room context
- **Meeting Summaries** — NIM-generated summaries with action items
- **Contextual Welcome** — Theme-appropriate welcome messages
- **Smart Notes** — AI-extracted action items

### With NVIDIA CloudXR
All of the above, plus:
- **Full VR streaming** — Headset-quality rendering on any device
- **NVIDIA RTX rendering** — Real-time ray-traced scenes
- **Multi-user VR presence** — See each other as avatars

## Room Themes

| Theme | Atmosphere | Best For |
|-------|------------|----------|
| `boardroom` | Modern corporate | Business meetings |
| `silk-road` | Ancient bazaar | Education, history |
| `harlem-jazz` | 1920s jazz club | Creative sessions |
| `brooklyn-90s` | Urban community | Community organizing |
| `space-station` | Orbital sci-fi | STEM, innovation |
| `community-center` | East Flatbush | Community meetings |

## API Reference

```
GET  /health                    — Server health
GET  /themes                    — List room themes
POST /rooms                     — Create a room
GET  /rooms                     — List active rooms
POST /rooms/{id}/join           — Join a room
POST /rooms/{id}/leave          — Leave a room
GET  /rooms/{id}                — Get room state
POST /rooms/{id}/message        — Send chat message
POST /rooms/{id}/ask            — Ask AI assistant
POST /rooms/{id}/summary        — Get meeting summary
POST /rooms/{id}/vr-session     — Start CloudXR VR session
GET  /room/{id}                 — WebVR client (browser)
GET  /                          — Meeting lobby
```

## Integration with NVIDIA Resource Suite

The VR Meeting Room can use the NVIDIA Resource Suite (port 7760) for:
- Advanced NIM models (Nemotron, multimodal)
- GPU-accelerated rendering via Omniverse
- World Interactive Origins themed rooms

Set `NVIDIA_RESOURCE_SUITE_URL=http://localhost:7760` to enable.

## Integration with World Interactive Origins

Meeting rooms can be hosted inside World Interactive Origins educational worlds:
- Teachers hold class sessions in the Silk Road Bazaar
- Community meetings in the East Flatbush Community Center
- Science sessions in the Space Station

The `theme` parameter maps directly to Omniverse world themes in `nvidia-resource-suite`.
