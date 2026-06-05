"""
VR Meeting Room — NVIDIA CloudXR Bridge
Enables full VR headset streaming for meeting rooms.

NVIDIA CloudXR streams the full Omniverse/3D scene to VR headsets
(Meta Quest, HTC Vive, Valve Index) with minimal latency.

Requirements:
- NVIDIA CloudXR Server installed on GPU host
- VR headset with CloudXR client app
- See: https://developer.nvidia.com/cloudxr-sdk
"""
from __future__ import annotations

import os
import uuid
from dataclasses import dataclass, field
from typing import Any

import requests


CLOUDXR_SERVER_URL = os.getenv("CLOUDXR_SERVER_URL", "")


@dataclass
class XRSession:
    session_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    room_id: str = ""
    participant_id: str = ""
    headset_type: str = "unknown"  # "quest3", "index", "vive", "pico4"
    server_url: str = ""
    stream_quality: str = "auto"  # "auto", "4k", "2k", "1080p"
    active: bool = False
    latency_ms: float = 0.0


class CloudXRBridge:
    """
    Bridge to NVIDIA CloudXR for VR headset streaming.
    Mocked when CLOUDXR_SERVER_URL is not set.
    """

    def __init__(self) -> None:
        self.server_url = CLOUDXR_SERVER_URL
        self.sessions: dict[str, XRSession] = {}
        self.mock = not bool(self.server_url)

    def create_session(
        self,
        room_id: str,
        participant_id: str,
        headset_type: str = "unknown",
        stream_quality: str = "auto",
    ) -> XRSession:
        """Create a CloudXR streaming session for a VR participant."""
        session = XRSession(
            room_id=room_id,
            participant_id=participant_id,
            headset_type=headset_type,
            server_url=self.server_url or "mock://cloudxr",
            stream_quality=stream_quality,
        )

        if not self.mock:
            result = self._create_remote_session(session)
            session.active = result.get("status") == "active"
        else:
            session.active = True
            session.latency_ms = 12.5  # mocked latency

        self.sessions[session.session_id] = session
        return session

    def _create_remote_session(self, session: XRSession) -> dict[str, Any]:
        """Call NVIDIA CloudXR server to create a streaming session."""
        try:
            resp = requests.post(
                f"{self.server_url}/api/v1/sessions",
                json={
                    "room_id": session.room_id,
                    "participant_id": session.participant_id,
                    "headset_type": session.headset_type,
                    "quality": session.stream_quality,
                },
                timeout=10,
            )
            return resp.json()
        except Exception as exc:
            return {"status": "error", "error": str(exc)}

    def end_session(self, session_id: str) -> bool:
        session = self.sessions.get(session_id)
        if not session:
            return False
        session.active = False
        return True

    def get_connection_info(self, session_id: str) -> dict[str, Any]:
        """Get connection info for the VR client to connect to the stream."""
        session = self.sessions.get(session_id)
        if not session:
            return {"error": "session not found"}
        return {
            "session_id": session.session_id,
            "server_url": session.server_url,
            "stream_url": f"{session.server_url}/stream/{session.session_id}",
            "quality": session.stream_quality,
            "active": session.active,
            "latency_ms": session.latency_ms,
            "setup_guide": "Install NVIDIA CloudXR client on your headset, then connect to the stream URL",
            "mock": session.mock if hasattr(session, 'mock') else self.mock,
        }

    def list_active_sessions(self) -> list[dict[str, Any]]:
        return [
            {"session_id": s.session_id, "room_id": s.room_id, "headset": s.headset_type, "latency_ms": s.latency_ms}
            for s in self.sessions.values()
            if s.active
        ]

    def status(self) -> dict[str, Any]:
        return {
            "cloudxr_available": not self.mock,
            "server_url": self.server_url or "not configured",
            "active_sessions": len([s for s in self.sessions.values() if s.active]),
            "setup": "Set CLOUDXR_SERVER_URL env var to enable VR streaming" if self.mock else "Connected",
        }
