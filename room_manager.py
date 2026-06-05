"""
VR Meeting Room — Room Manager
Manages room state, participants, and sessions.
"""
from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class RoomStatus(str, Enum):
    WAITING = "waiting"
    ACTIVE = "active"
    ENDED = "ended"


class ParticipantRole(str, Enum):
    HOST = "host"
    PARTICIPANT = "participant"
    OBSERVER = "observer"


ROOM_THEMES = {
    "boardroom": {
        "name": "Executive Boardroom",
        "description": "Modern corporate meeting space",
        "environment": "modern-office",
        "sky_color": "#1a1a2e",
        "floor_texture": "marble",
        "accent_color": "#00d4ff",
    },
    "silk-road": {
        "name": "Silk Road Bazaar",
        "description": "Ancient trading post on the Silk Road",
        "environment": "desert-night",
        "sky_color": "#0d0d2b",
        "floor_texture": "sand",
        "accent_color": "#f4a017",
    },
    "harlem-jazz": {
        "name": "Harlem Jazz Club",
        "description": "1920s jazz club in Harlem, NY",
        "environment": "city-night",
        "sky_color": "#1a0a0a",
        "floor_texture": "hardwood",
        "accent_color": "#c9a84c",
    },
    "brooklyn-90s": {
        "name": "Brooklyn Community Center",
        "description": "1990s Brooklyn community gathering space",
        "environment": "urban",
        "sky_color": "#2c3e50",
        "floor_texture": "concrete",
        "accent_color": "#e74c3c",
    },
    "space-station": {
        "name": "Space Station",
        "description": "Zero-gravity orbital meeting room",
        "environment": "space",
        "sky_color": "#000011",
        "floor_texture": "metal-grating",
        "accent_color": "#00ff88",
    },
    "community-center": {
        "name": "East Flatbush Community Center",
        "description": "Warm community gathering space",
        "environment": "park",
        "sky_color": "#87ceeb",
        "floor_texture": "carpet",
        "accent_color": "#27ae60",
    },
}


@dataclass
class Participant:
    participant_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    display_name: str = "Anonymous"
    role: ParticipantRole = ParticipantRole.PARTICIPANT
    joined_at: float = field(default_factory=time.time)
    avatar_color: str = "#00d4ff"
    position: dict[str, float] = field(default_factory=lambda: {"x": 0, "y": 1.6, "z": -3})
    is_speaking: bool = False
    is_muted: bool = False
    is_video_on: bool = True
    using_vr: bool = False


@dataclass
class MeetingRoom:
    room_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8].upper())
    name: str = ""
    theme: str = "boardroom"
    status: RoomStatus = RoomStatus.WAITING
    host_id: str = ""
    participants: dict[str, Participant] = field(default_factory=dict)
    created_at: float = field(default_factory=time.time)
    started_at: float | None = None
    ended_at: float | None = None
    max_participants: int = 25
    recording_enabled: bool = False
    ai_assistant_enabled: bool = True
    messages: list[dict[str, Any]] = field(default_factory=list)
    ai_notes: list[str] = field(default_factory=list)


class RoomManager:
    def __init__(self) -> None:
        self.rooms: dict[str, MeetingRoom] = {}

    def create_room(
        self,
        name: str,
        host_name: str,
        theme: str = "boardroom",
        max_participants: int = 25,
        ai_assistant: bool = True,
    ) -> tuple[MeetingRoom, Participant]:
        room = MeetingRoom(
            name=name or f"Meeting {time.strftime('%H:%M')}",
            theme=theme if theme in ROOM_THEMES else "boardroom",
            max_participants=max_participants,
            ai_assistant_enabled=ai_assistant,
        )
        host = Participant(
            display_name=host_name,
            role=ParticipantRole.HOST,
            avatar_color="#f4a017",
        )
        room.host_id = host.participant_id
        room.participants[host.participant_id] = host
        self.rooms[room.room_id] = room
        return room, host

    def join_room(self, room_id: str, display_name: str) -> tuple[MeetingRoom, Participant] | None:
        room = self.rooms.get(room_id)
        if not room or room.status == RoomStatus.ENDED:
            return None
        if len(room.participants) >= room.max_participants:
            return None

        # Assign avatar color based on participant number
        colors = ["#00d4ff", "#ff6b6b", "#51cf66", "#ffd43b", "#cc5de8", "#74c0fc"]
        color = colors[len(room.participants) % len(colors)]

        participant = Participant(display_name=display_name, avatar_color=color)
        room.participants[participant.participant_id] = participant

        if room.status == RoomStatus.WAITING:
            room.status = RoomStatus.ACTIVE
            room.started_at = time.time()

        return room, participant

    def leave_room(self, room_id: str, participant_id: str) -> bool:
        room = self.rooms.get(room_id)
        if not room:
            return False
        room.participants.pop(participant_id, None)
        if len(room.participants) == 0:
            room.status = RoomStatus.ENDED
            room.ended_at = time.time()
        return True

    def add_message(self, room_id: str, participant_id: str, text: str) -> dict[str, Any] | None:
        room = self.rooms.get(room_id)
        if not room:
            return None
        participant = room.participants.get(participant_id)
        msg = {
            "id": str(uuid.uuid4()),
            "participant_id": participant_id,
            "display_name": participant.display_name if participant else "Unknown",
            "text": text,
            "timestamp": time.time(),
        }
        room.messages.append(msg)
        return msg

    def get_room_state(self, room_id: str) -> dict[str, Any] | None:
        room = self.rooms.get(room_id)
        if not room:
            return None
        theme_data = ROOM_THEMES.get(room.theme, ROOM_THEMES["boardroom"])
        return {
            "room_id": room.room_id,
            "name": room.name,
            "theme": room.theme,
            "theme_data": theme_data,
            "status": room.status,
            "participant_count": len(room.participants),
            "participants": [
                {
                    "id": p.participant_id,
                    "name": p.display_name,
                    "role": p.role,
                    "avatar_color": p.avatar_color,
                    "position": p.position,
                    "is_speaking": p.is_speaking,
                    "is_muted": p.is_muted,
                    "using_vr": p.using_vr,
                }
                for p in room.participants.values()
            ],
            "ai_assistant_enabled": room.ai_assistant_enabled,
            "messages": room.messages[-50:],  # last 50 messages
        }

    def list_active_rooms(self) -> list[dict[str, Any]]:
        return [
            {
                "room_id": r.room_id,
                "name": r.name,
                "theme": r.theme,
                "participant_count": len(r.participants),
                "status": r.status,
            }
            for r in self.rooms.values()
            if r.status != RoomStatus.ENDED
        ]
