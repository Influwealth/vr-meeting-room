"""
VR Meeting Room — NIM AI Meeting Assistant
Powered by NVIDIA NIM LLMs for meeting summaries, notes, and Q&A.
"""
from __future__ import annotations

import os
import time
from typing import Any

import requests


NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY", "")
NIM_BASE_URL = os.getenv("NVIDIA_NIM_BASE_URL", "https://integrate.api.nvidia.com/v1")
DEFAULT_MODEL = "meta/llama-3.1-70b-instruct"


class NIMAssistant:
    """AI meeting assistant powered by NVIDIA NIM."""

    def __init__(self) -> None:
        self.api_key = NVIDIA_API_KEY
        self._session = requests.Session()
        if self.api_key:
            self._session.headers.update({"Authorization": f"Bearer {self.api_key}"})

    def _chat(self, system: str, user: str, max_tokens: int = 512) -> str:
        if not self.api_key:
            return "[AI Assistant unavailable — NVIDIA_API_KEY not configured]"
        payload = {
            "model": DEFAULT_MODEL,
            "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}],
            "temperature": 0.4,
            "max_tokens": max_tokens,
        }
        try:
            resp = self._session.post(f"{NIM_BASE_URL}/chat/completions", json=payload, timeout=30)
            resp.raise_for_status()
            return resp.json()["choices"][0]["message"]["content"]
        except Exception as exc:
            return f"[AI Assistant error: {exc}]"

    def summarize_meeting(self, room_name: str, messages: list[dict[str, Any]], duration_minutes: float) -> str:
        """Generate a meeting summary from chat messages."""
        transcript = "\n".join(f"{m['display_name']}: {m['text']}" for m in messages)
        system = "You are an AI meeting assistant. Generate concise, actionable meeting summaries."
        user = f"""Meeting: {room_name}
Duration: {duration_minutes:.0f} minutes
Participants: {len({m['display_name'] for m in messages})}

Transcript:
{transcript[:3000]}

Generate a meeting summary with:
1. Key discussion points (3-5 bullets)
2. Decisions made
3. Action items with owners
4. Next steps"""
        return self._chat(system, user, max_tokens=600)

    def answer_question(self, question: str, room_context: str, theme: str = "boardroom") -> str:
        """Answer a question in the context of the meeting room theme."""
        theme_contexts = {
            "silk-road": "You are in a virtual reconstruction of the ancient Silk Road. Historical expertise available.",
            "harlem-jazz": "You are in a virtual 1920s Harlem jazz club. Cultural and historical expertise available.",
            "brooklyn-90s": "You are in a 1990s Brooklyn community center. Local history and culture expertise available.",
            "space-station": "You are on a virtual space station. STEM and science expertise available.",
            "boardroom": "You are in a corporate boardroom. Business and strategy expertise available.",
            "community-center": "You are in the East Flatbush Community Center. Community organizing expertise available.",
        }
        theme_ctx = theme_contexts.get(theme, theme_contexts["boardroom"])
        system = f"You are an AI assistant in a virtual meeting room. {theme_ctx} Be concise and helpful."
        return self._chat(system, f"Context: {room_context}\n\nQuestion: {question}", max_tokens=300)

    def generate_action_items(self, messages: list[dict[str, Any]]) -> list[str]:
        """Extract action items from meeting messages."""
        transcript = "\n".join(f"{m['display_name']}: {m['text']}" for m in messages[-100:])
        system = "Extract action items from meeting transcripts. Return a numbered list only."
        result = self._chat(system, f"Extract action items:\n{transcript[:2000]}", max_tokens=300)
        lines = [line.strip() for line in result.split("\n") if line.strip() and not line.strip().startswith("#")]
        return lines[:10]

    def welcome_message(self, room_name: str, theme: str, host_name: str) -> str:
        """Generate a contextual welcome message for the meeting room."""
        theme_prompts = {
            "silk-road": f"Welcome participants to a meeting in the Silk Road Bazaar. Host: {host_name}. Be poetic and reference ancient trade.",
            "harlem-jazz": f"Welcome participants to a meeting in the Harlem Jazz Club. Host: {host_name}. Reference jazz, freedom, and creativity.",
            "brooklyn-90s": f"Welcome to the Brooklyn Community Center. Host: {host_name}. Keep it real and community-focused.",
            "space-station": f"Welcome to the Space Station meeting room. Host: {host_name}. Reference the cosmos and exploration.",
            "boardroom": f"Welcome to {room_name}. Host: {host_name}. Professional and efficient.",
            "community-center": f"Welcome to the East Flatbush Community Center. Host: {host_name}. Warm, inclusive, community-first.",
        }
        system = "You are a warm, welcoming AI assistant. Generate a 2-sentence welcome message."
        prompt = theme_prompts.get(theme, theme_prompts["boardroom"])
        return self._chat(system, prompt, max_tokens=100)
