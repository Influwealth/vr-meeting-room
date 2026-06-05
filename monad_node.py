"""
vr-meeting-room — MONAD NODE_EPSILON: Digital Twin & VR Interface

NODE_EPSILON is the operator-facing VR layer of the MONAD mesh:
  - VR Cockpit Primary  — operator control surface
  - VR Cockpit Secondary — observer / backup
  - Digital twin rendering for East Flatbush and Greenville worlds
  - CloudXR streaming for Quest 3, Index, Vive, Pico 4
  - A-Frame WebVR fallback for browser access

Port: 7791 (FastAPI)
MONAD VR port range: 3000–3099
"""

from __future__ import annotations

import logging
import os
import time
import uuid
from dataclasses import dataclass, field
from typing import Any

log = logging.getLogger(__name__)

MONAD_VERSION = "3.7"
NODE_ID = "NODE_EPSILON"
API_PORT = 7791
VR_PORT_RANGE = (3000, 3099)

AGENTS = ["VR Cockpit Primary", "VR Cockpit Secondary"]

HEADSETS = ["quest3", "index", "vive", "pico4"]

THEMES = [
    "boardroom",
    "silk-road",
    "harlem-jazz",
    "brooklyn-90s",
    "space-station",
    "community-center",
    "east-flatbush-origins",
    "greenville-sovereign",
]


@dataclass
class NODE_EPSILON_Registration:
    service_id: str = "vr-meeting-room"
    node_id: str = NODE_ID
    api_port: int = API_PORT
    vr_port_range: tuple[int, int] = field(default_factory=lambda: VR_PORT_RANGE)
    capabilities: list[str] = field(default_factory=lambda: [
        "vr_cockpit",
        "cloudxr_streaming",
        "aframe_webvr",
        "digital_twin_render",
        "meeting_rooms",
        "nim_assistant",
        "community_events",
    ])
    agents: list[str] = field(default_factory=lambda: AGENTS)
    headsets_supported: list[str] = field(default_factory=lambda: HEADSETS)
    themes: list[str] = field(default_factory=lambda: THEMES)
    cloudxr_available: bool = field(default_factory=lambda: bool(os.environ.get("CLOUDXR_SERVER_URL")))
    nim_available: bool = field(default_factory=lambda: bool(os.environ.get("NVIDIA_API_KEY")))
    monad_version: str = MONAD_VERSION
    registered_at: float = field(default_factory=time.time)
    trace_id: str = field(default_factory=lambda: str(uuid.uuid4()))

    def as_sap_headers(self) -> dict[str, str]:
        return {
            "x-sap-node-id": self.node_id,
            "x-sap-trace-id": self.trace_id,
            "x-sap-version": self.monad_version,
            "x-sap-capsule": f"epsilon-{self.registered_at:.0f}",
        }

    def to_dict(self) -> dict[str, Any]:
        return {
            "service_id": self.service_id,
            "node_id": self.node_id,
            "api_port": self.api_port,
            "vr_port_range": list(self.vr_port_range),
            "capabilities": self.capabilities,
            "agents": self.agents,
            "headsets_supported": self.headsets_supported,
            "themes": self.themes,
            "cloudxr_available": self.cloudxr_available,
            "nim_available": self.nim_available,
            "monad_version": self.monad_version,
            "registered_at": self.registered_at,
            "trace_id": self.trace_id,
        }


class NODE_EPSILON_Handler:
    """NODE_EPSILON registration and cockpit status for vr-meeting-room."""

    def __init__(self):
        self.registration = NODE_EPSILON_Registration()
        self._cockpit_primary_active = False
        self._cockpit_secondary_active = False

    def activate_cockpit(self, role: str = "primary") -> dict[str, Any]:
        """Activate VR Cockpit Primary or Secondary."""
        if role == "primary":
            self._cockpit_primary_active = True
            log.info("[NODE_EPSILON] VR Cockpit Primary activated")
        else:
            self._cockpit_secondary_active = True
            log.info("[NODE_EPSILON] VR Cockpit Secondary activated (observer mode)")
        return {"role": role, "active": True, "node_id": NODE_ID}

    def status(self) -> dict[str, Any]:
        return {
            "service_id": "vr-meeting-room",
            "node_id": NODE_ID,
            "monad_version": MONAD_VERSION,
            "api_port": API_PORT,
            "vr_port_range": list(VR_PORT_RANGE),
            "agents": AGENTS,
            "cockpit_primary_active": self._cockpit_primary_active,
            "cockpit_secondary_active": self._cockpit_secondary_active,
            "cloudxr_available": self.registration.cloudxr_available,
            "nim_available": self.registration.nim_available,
            "themes": THEMES,
            "headsets_supported": HEADSETS,
        }


_handler = NODE_EPSILON_Handler()


def get_handler() -> NODE_EPSILON_Handler:
    return _handler
