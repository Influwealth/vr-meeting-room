"""
VR Meeting Room — FastAPI Server
Port: 7791
SAP Node ID: vr-meeting-room

HTTP API for room management, AI assistant, and VR streaming.
Also serves the static A-Frame WebVR client.
"""
from __future__ import annotations

import os
import uuid
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from room_manager import RoomManager, ROOM_THEMES
from nim_assistant import NIMAssistant
from cloudxr_bridge import CloudXRBridge

app = FastAPI(title="VR Meeting Room", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

rooms = RoomManager()
assistant = NIMAssistant()
cloudxr = CloudXRBridge()

PORT = int(os.getenv("VR_ROOM_PORT", "7791"))
SAP_NODE_ID = "vr-meeting-room"


def sap_headers(trace_id: str) -> dict[str, str]:
    return {"x-sap-node-id": SAP_NODE_ID, "x-sap-trace-id": trace_id, "x-sap-version": "1.0"}


# ---------------------------------------------------------------------------
# Request models
# ---------------------------------------------------------------------------

class CreateRoomRequest(BaseModel):
    name: str = ""
    host_name: str = "Host"
    theme: str = "boardroom"
    max_participants: int = 25
    ai_assistant: bool = True


class JoinRoomRequest(BaseModel):
    display_name: str = "Participant"


class MessageRequest(BaseModel):
    participant_id: str
    text: str


class QuestionRequest(BaseModel):
    question: str
    participant_id: str = ""


class VRSessionRequest(BaseModel):
    participant_id: str
    headset_type: str = "unknown"
    stream_quality: str = "auto"


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.get("/health")
async def health() -> dict[str, Any]:
    return {
        "status": "ok",
        "node": SAP_NODE_ID,
        "port": PORT,
        "active_rooms": len(rooms.list_active_rooms()),
        "nim_available": bool(os.getenv("NVIDIA_API_KEY")),
        "cloudxr": cloudxr.status(),
    }


@app.get("/themes")
async def list_themes() -> dict[str, Any]:
    return {"themes": ROOM_THEMES}


@app.post("/rooms")
async def create_room(req: CreateRoomRequest, request: Request) -> dict[str, Any]:
    trace_id = request.headers.get("x-sap-trace-id", str(uuid.uuid4()))
    room, host = rooms.create_room(req.name, req.host_name, req.theme, req.max_participants, req.ai_assistant)

    welcome = ""
    if req.ai_assistant:
        welcome = assistant.welcome_message(room.name, room.theme, req.host_name)

    return {
        "room_id": room.room_id,
        "name": room.name,
        "theme": room.theme,
        "host_participant_id": host.participant_id,
        "join_url": f"http://localhost:{PORT}/room/{room.room_id}",
        "welcome_message": welcome,
        "trace_id": trace_id,
    }


@app.get("/rooms")
async def list_rooms() -> dict[str, Any]:
    return {"rooms": rooms.list_active_rooms()}


@app.post("/rooms/{room_id}/join")
async def join_room(room_id: str, req: JoinRoomRequest, request: Request) -> dict[str, Any]:
    trace_id = request.headers.get("x-sap-trace-id", str(uuid.uuid4()))
    result = rooms.join_room(room_id, req.display_name)
    if not result:
        raise HTTPException(status_code=404, detail="Room not found or full")
    room, participant = result
    return {
        "room_id": room.room_id,
        "participant_id": participant.participant_id,
        "display_name": participant.display_name,
        "role": participant.role,
        "avatar_color": participant.avatar_color,
        "room_state": rooms.get_room_state(room_id),
        "trace_id": trace_id,
    }


@app.post("/rooms/{room_id}/leave")
async def leave_room(room_id: str, participant_id: str) -> dict[str, Any]:
    success = rooms.leave_room(room_id, participant_id)
    return {"success": success}


@app.get("/rooms/{room_id}")
async def get_room(room_id: str) -> dict[str, Any]:
    state = rooms.get_room_state(room_id)
    if not state:
        raise HTTPException(status_code=404, detail="Room not found")
    return state


@app.post("/rooms/{room_id}/message")
async def send_message(room_id: str, req: MessageRequest) -> dict[str, Any]:
    msg = rooms.add_message(room_id, req.participant_id, req.text)
    if not msg:
        raise HTTPException(status_code=404, detail="Room not found")
    return {"message": msg}


@app.post("/rooms/{room_id}/ask")
async def ask_assistant(room_id: str, req: QuestionRequest) -> dict[str, Any]:
    room_state = rooms.get_room_state(room_id)
    if not room_state:
        raise HTTPException(status_code=404, detail="Room not found")
    if not room_state.get("ai_assistant_enabled"):
        raise HTTPException(status_code=400, detail="AI assistant not enabled for this room")
    context = f"Meeting: {room_state['name']}, Participants: {room_state['participant_count']}"
    answer = assistant.answer_question(req.question, context, room_state["theme"])
    return {"question": req.question, "answer": answer, "room_id": room_id}


@app.post("/rooms/{room_id}/summary")
async def get_summary(room_id: str) -> dict[str, Any]:
    room = rooms.rooms.get(room_id)
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    import time
    duration = (time.time() - (room.started_at or room.created_at)) / 60
    summary = assistant.summarize_meeting(room.name, room.messages, duration)
    action_items = assistant.generate_action_items(room.messages)
    return {"room_id": room_id, "summary": summary, "action_items": action_items, "duration_minutes": duration}


@app.post("/rooms/{room_id}/vr-session")
async def create_vr_session(room_id: str, req: VRSessionRequest) -> dict[str, Any]:
    session = cloudxr.create_session(room_id, req.participant_id, req.headset_type, req.stream_quality)
    return {"session_id": session.session_id, "connection": cloudxr.get_connection_info(session.session_id)}


@app.get("/room/{room_id}", response_class=HTMLResponse)
async def room_client(room_id: str) -> HTMLResponse:
    """Serve the A-Frame WebVR client for a specific room."""
    room_state = rooms.get_room_state(room_id)
    theme = room_state["theme"] if room_state else "boardroom"
    theme_data = ROOM_THEMES.get(theme, ROOM_THEMES["boardroom"])
    return HTMLResponse(content=_build_room_html(room_id, theme_data, room_state))


@app.get("/", response_class=HTMLResponse)
async def lobby() -> HTMLResponse:
    """Serve the meeting lobby page."""
    active = rooms.list_active_rooms()
    return HTMLResponse(content=_build_lobby_html(active))


def _build_room_html(room_id: str, theme: dict, state: dict | None) -> str:
    name = state["name"] if state else "Meeting Room"
    sky = theme.get("sky_color", "#1a1a2e")
    accent = theme.get("accent_color", "#00d4ff")
    participants = state["participants"] if state else []
    participant_spheres = ""
    for i, p in enumerate(participants):
        x = (i % 5) * 2 - 4
        z = -3 - (i // 5) * 2
        participant_spheres += f'<a-sphere position="{x} 1.6 {z}" radius="0.3" color="{p["avatar_color"]}" roughness="0.3"><a-text value="{p["name"][:12]}" position="0 0.5 0" align="center" color="white" scale="1.5 1.5 1.5"></a-text></a-sphere>\n'

    return f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>{name} — VR Meeting Room</title>
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <script src="https://aframe.io/releases/1.5.0/aframe.min.js"></script>
  <style>
    body {{ margin: 0; font-family: 'Arial', sans-serif; background: {sky}; }}
    #ui-overlay {{ position: fixed; bottom: 20px; left: 50%; transform: translateX(-50%);
      background: rgba(0,0,0,0.8); border: 1px solid {accent}; border-radius: 12px;
      padding: 16px 24px; color: white; z-index: 999; text-align: center; min-width: 400px; }}
    #room-title {{ position: fixed; top: 20px; left: 50%; transform: translateX(-50%);
      background: rgba(0,0,0,0.7); border: 1px solid {accent}; border-radius: 8px;
      padding: 8px 20px; color: {accent}; font-size: 18px; z-index: 999; }}
    #chat-box {{ position: fixed; right: 20px; top: 80px; width: 280px;
      background: rgba(0,0,0,0.85); border: 1px solid {accent}; border-radius: 12px;
      padding: 12px; color: white; z-index: 999; max-height: 400px; overflow-y: auto; }}
    input, button {{ background: rgba(255,255,255,0.1); border: 1px solid {accent};
      color: white; padding: 8px 12px; border-radius: 6px; margin: 4px; }}
    button {{ cursor: pointer; background: {accent}20; }}
    button:hover {{ background: {accent}40; }}
    #ask-box {{ position: fixed; left: 20px; top: 80px; width: 280px;
      background: rgba(0,0,0,0.85); border: 1px solid #00ff88; border-radius: 12px;
      padding: 12px; color: white; z-index: 999; }}
  </style>
</head>
<body>
  <div id="room-title">{name} | Room {room_id}</div>

  <div id="ask-box">
    <div style="color:#00ff88;font-weight:bold;margin-bottom:8px">AI Assistant</div>
    <input id="ai-question" type="text" placeholder="Ask anything..." style="width:100%;box-sizing:border-box">
    <button onclick="askAI()" style="width:100%;margin-top:6px">Ask</button>
    <div id="ai-answer" style="margin-top:8px;font-size:12px;color:#ccc;line-height:1.4"></div>
  </div>

  <div id="chat-box">
    <div style="color:{accent};font-weight:bold;margin-bottom:8px">Chat</div>
    <div id="messages" style="min-height:100px;font-size:12px"></div>
    <div style="margin-top:8px">
      <input id="msg-input" type="text" placeholder="Message..." style="width:100%;box-sizing:border-box">
      <button onclick="sendMsg()" style="width:100%;margin-top:4px">Send</button>
    </div>
  </div>

  <div id="ui-overlay">
    <span id="participant-count">{len(participants)} participants</span>
    &nbsp;|&nbsp;
    <button onclick="toggleVR()">Enter VR</button>
    <button onclick="getSummary()">Summary</button>
    <button onclick="leaveRoom()">Leave</button>
  </div>

  <a-scene background="color: {sky}" vr-mode-ui="enabled: true">
    <!-- Room floor -->
    <a-plane position="0 0 0" rotation="-90 0 0" width="20" height="20"
      color="#1a1a1a" roughness="0.8" metalness="0.1"></a-plane>

    <!-- Ambient lighting -->
    <a-light type="ambient" color="#404040" intensity="0.5"></a-light>
    <a-light type="directional" position="5 10 5" color="white" intensity="0.8"></a-light>
    <a-light type="point" position="0 3 0" color="{accent}" intensity="0.4" distance="15"></a-light>

    <!-- Conference table -->
    <a-box position="0 0.75 -3" width="6" height="0.1" depth="2.5"
      color="#2a2a3e" roughness="0.3" metalness="0.6"></a-box>

    <!-- Table legs -->
    <a-box position="-2.5 0.35 -3" width="0.1" height="0.7" depth="0.1" color="#1a1a2e"></a-box>
    <a-box position="2.5 0.35 -3" width="0.1" height="0.7" depth="0.1" color="#1a1a2e"></a-box>

    <!-- Screen wall -->
    <a-plane position="0 2.5 -7" width="8" height="4.5" color="#0a0a1a"
      roughness="0.1" metalness="0.9"></a-plane>
    <a-text value="INFLUWEALTH\\nVIRTUAL MEETING ROOM\\n{name}"
      position="0 2.5 -6.9" align="center" color="{accent}"
      scale="1.2 1.2 1.2" line-height="40"></a-text>

    <!-- Participant avatars -->
    {participant_spheres}

    <!-- Camera rig -->
    <a-entity id="rig" position="0 0 2">
      <a-camera look-controls wasd-controls>
        <a-cursor color="{accent}" fuse="false"></a-cursor>
      </a-camera>
    </a-entity>

    <!-- Sky -->
    <a-sky color="{sky}"></a-sky>
  </a-scene>

  <script>
    const ROOM_ID = '{room_id}';
    const API = 'http://localhost:7791';
    let participantId = sessionStorage.getItem('participant_id_' + ROOM_ID);
    let displayName = sessionStorage.getItem('display_name') || 'Participant';

    async function joinIfNeeded() {{
      if (!participantId) {{
        const name = prompt('Your name:', displayName) || 'Participant';
        displayName = name;
        sessionStorage.setItem('display_name', name);
        const res = await fetch(`${{API}}/rooms/${{ROOM_ID}}/join`, {{
          method: 'POST', headers: {{'Content-Type': 'application/json'}},
          body: JSON.stringify({{display_name: name}})
        }});
        const data = await res.json();
        participantId = data.participant_id;
        sessionStorage.setItem('participant_id_' + ROOM_ID, participantId);
        loadMessages(data.room_state?.messages || []);
      }}
    }}

    async function sendMsg() {{
      const input = document.getElementById('msg-input');
      if (!input.value.trim() || !participantId) return;
      await fetch(`${{API}}/rooms/${{ROOM_ID}}/message`, {{
        method: 'POST', headers: {{'Content-Type': 'application/json'}},
        body: JSON.stringify({{participant_id: participantId, text: input.value}})
      }});
      input.value = '';
    }}

    async function askAI() {{
      const q = document.getElementById('ai-question').value;
      if (!q.trim()) return;
      document.getElementById('ai-answer').textContent = 'Thinking...';
      const res = await fetch(`${{API}}/rooms/${{ROOM_ID}}/ask`, {{
        method: 'POST', headers: {{'Content-Type': 'application/json'}},
        body: JSON.stringify({{question: q}})
      }});
      const data = await res.json();
      document.getElementById('ai-answer').textContent = data.answer || 'No response';
    }}

    async function getSummary() {{
      const res = await fetch(`${{API}}/rooms/${{ROOM_ID}}/summary`, {{method: 'POST'}});
      const data = await res.json();
      alert('Meeting Summary:\\n\\n' + data.summary + '\\n\\nAction Items:\\n' + data.action_items.join('\\n'));
    }}

    function toggleVR() {{
      const scene = document.querySelector('a-scene');
      if (scene.is('vr-mode')) scene.exitVR(); else scene.enterVR();
    }}

    async function leaveRoom() {{
      if (participantId) {{
        await fetch(`${{API}}/rooms/${{ROOM_ID}}/leave?participant_id=${{participantId}}`, {{method: 'POST'}});
        sessionStorage.removeItem('participant_id_' + ROOM_ID);
      }}
      window.location.href = '/';
    }}

    function loadMessages(messages) {{
      const box = document.getElementById('messages');
      box.innerHTML = messages.map(m => `<div><b style="color:#ccc">${{m.display_name}}</b>: ${{m.text}}</div>`).join('');
    }}

    document.getElementById('msg-input').addEventListener('keydown', e => {{
      if (e.key === 'Enter') sendMsg();
    }});
    document.getElementById('ai-question').addEventListener('keydown', e => {{
      if (e.key === 'Enter') askAI();
    }});

    joinIfNeeded();
    setInterval(async () => {{
      const res = await fetch(`${{API}}/rooms/${{ROOM_ID}}`);
      const state = await res.json();
      document.getElementById('participant-count').textContent = state.participant_count + ' participants';
      loadMessages(state.messages || []);
    }}, 5000);
  </script>
</body>
</html>"""


def _build_lobby_html(active_rooms: list[dict]) -> str:
    room_cards = ""
    for r in active_rooms:
        room_cards += f"""
        <div style="background:rgba(255,255,255,0.05);border:1px solid #00d4ff33;border-radius:12px;padding:16px;margin:8px">
          <div style="color:#00d4ff;font-weight:bold">{r['name']}</div>
          <div style="color:#888;font-size:12px">{r['theme']} · {r['participant_count']} participants</div>
          <a href="/room/{r['room_id']}" style="color:#00d4ff;text-decoration:none">Join &rarr;</a>
        </div>"""
    if not room_cards:
        room_cards = '<div style="color:#666;text-align:center;padding:20px">No active rooms. Create one below.</div>'

    return f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>VR Meeting Room — Lobby</title>
  <style>
    body {{ background:#0d0d1f;color:white;font-family:Arial,sans-serif;margin:0;padding:20px; }}
    .container {{ max-width:600px;margin:0 auto; }}
    h1 {{ color:#00d4ff;text-align:center; }}
    input, select, button {{ background:rgba(255,255,255,0.1);border:1px solid #00d4ff44;
      color:white;padding:10px 16px;border-radius:8px;margin:6px 0;width:100%;box-sizing:border-box; }}
    button {{ background:#00d4ff20;cursor:pointer;font-weight:bold; }}
    button:hover {{ background:#00d4ff40; }}
    .theme-grid {{ display:grid;grid-template-columns:1fr 1fr;gap:8px;margin:12px 0; }}
    .theme-card {{ padding:10px;border:1px solid #ffffff22;border-radius:8px;cursor:pointer;font-size:12px; }}
    .theme-card.selected {{ border-color:#00d4ff;background:#00d4ff15; }}
  </style>
</head>
<body>
  <div class="container">
    <h1>VR Meeting Room</h1>
    <p style="text-align:center;color:#888">Powered by NVIDIA &middot; Influwealth Sovereign Platform</p>

    <div style="background:rgba(0,0,0,0.4);border:1px solid #ffffff22;border-radius:16px;padding:20px;margin:20px 0">
      <h3 style="color:#00d4ff;margin-top:0">Create a Room</h3>
      <input id="room-name" type="text" placeholder="Meeting name (optional)">
      <input id="host-name" type="text" placeholder="Your name">
      <div class="theme-grid" id="themes">
        <div class="theme-card selected" data-theme="boardroom">Boardroom</div>
        <div class="theme-card" data-theme="silk-road">Silk Road Bazaar</div>
        <div class="theme-card" data-theme="harlem-jazz">Harlem Jazz Club</div>
        <div class="theme-card" data-theme="brooklyn-90s">Brooklyn 90s</div>
        <div class="theme-card" data-theme="space-station">Space Station</div>
        <div class="theme-card" data-theme="community-center">EFB Community Center</div>
      </div>
      <button onclick="createRoom()">Create Room</button>
    </div>

    <div style="background:rgba(0,0,0,0.4);border:1px solid #ffffff22;border-radius:16px;padding:20px">
      <h3 style="color:#00d4ff;margin-top:0">Active Rooms</h3>
      {room_cards}
    </div>
  </div>
  <script>
    let selectedTheme = 'boardroom';
    document.querySelectorAll('.theme-card').forEach(card => {{
      card.addEventListener('click', () => {{
        document.querySelectorAll('.theme-card').forEach(c => c.classList.remove('selected'));
        card.classList.add('selected');
        selectedTheme = card.dataset.theme;
      }});
    }});
    async function createRoom() {{
      const name = document.getElementById('room-name').value;
      const host = document.getElementById('host-name').value || 'Host';
      sessionStorage.setItem('display_name', host);
      const res = await fetch('/rooms', {{
        method: 'POST', headers: {{'Content-Type': 'application/json'}},
        body: JSON.stringify({{name, host_name: host, theme: selectedTheme}})
      }});
      const data = await res.json();
      sessionStorage.setItem('participant_id_' + data.room_id, data.host_participant_id);
      window.location.href = '/room/' + data.room_id;
    }}
  </script>
</body>
</html>"""


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=PORT)
