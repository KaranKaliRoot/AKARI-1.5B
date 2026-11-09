"""Conversation session management for AKARI.

Manages multiple independent conversation sessions with:
- Persistent storage in data/conversations/
- Context window management (sliding window with preserved recent history)
- JSON serialization of messages
"""
import json
import os
import time
import uuid
from pathlib import Path
from typing import Optional

from .config import CONVERSATIONS_DIR, MAX_HISTORY_TOKENS
from .persona import build_system_prompt, estimate_tokens


class ConversationSession:
    """A single independent conversation session."""

    def __init__(self, session_id: Optional[str] = None, mode: str = "default"):
        self.session_id = session_id or uuid.uuid4().hex[:12]
        self.mode = mode
        self.created_at = time.time()
        self.updated_at = time.time()
        self.messages: list[dict] = []  # [{"role": "user"/"assistant", "content": "..."}]
        self.system_prompt = build_system_prompt(mode)
        self._load()

    def _path(self) -> Path:
        return CONVERSATIONS_DIR / f"{self.session_id}.json"

    def _load(self) -> None:
        """Load existing messages from disk if present."""
        path = self._path()
        if path.exists():
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                self.session_id = data.get("session_id", self.session_id)
                self.mode = data.get("mode", self.mode)
                self.created_at = data.get("created_at", self.created_at)
                self.messages = data.get("messages", [])
                self.system_prompt = build_system_prompt(self.mode)
            except (json.JSONDecodeError, OSError):
                self.messages = []

    def save(self) -> None:
        """Persist conversation to disk."""
        CONVERSATIONS_DIR.mkdir(parents=True, exist_ok=True)
        data = {
            "session_id": self.session_id,
            "mode": self.mode,
            "created_at": self.created_at,
            "updated_at": time.time(),
            "messages": self.messages,
        }
        with open(self._path(), "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        self.updated_at = data["updated_at"]

    def add_message(self, role: str, content: str) -> None:
        """Append a message to the conversation."""
        self.messages.append({"role": role, "content": content})
        self.save()

    def add_user_message(self, content: str) -> None:
        self.add_message("user", content)

    def add_assistant_message(self, content: str) -> None:
        self.add_message("assistant", content)

    def get_messages_for_llm(self) -> list[dict]:
        """Build the message list to send to llama-server with context management.

        Strategy:
        1. Always include the system prompt.
        2. Include all messages if under the token budget.
        3. If over budget, keep the most recent messages and drop older ones,
           but never drop the very first exchange (it establishes context).
        """
        if not self.messages:
            return [{"role": "system", "content": self.system_prompt}]

        # Estimate total tokens of all messages
        total_tokens = estimate_tokens(self.system_prompt)
        for m in self.messages:
            total_tokens += estimate_tokens(m["content"])

        if total_tokens <= MAX_HISTORY_TOKENS:
            return [{"role": "system", "content": self.system_prompt}] + self.messages

        # Sliding window: keep recent messages, preserve first exchange
        result = [{"role": "system", "content": self.system_prompt}]
        running_tokens = estimate_tokens(self.system_prompt)

        # Always keep the first user message (context anchor)
        first_msg = self.messages[0]
        result.append(first_msg)
        running_tokens += estimate_tokens(first_msg["content"])

        # Add recent messages from the end
        recent = []
        recent_tokens = 0
        for m in reversed(self.messages[1:]):
            m_tokens = estimate_tokens(m["content"])
            if running_tokens + recent_tokens + m_tokens > MAX_HISTORY_TOKENS:
                break
            recent.append(m)
            recent_tokens += m_tokens

        result.extend(reversed(recent))
        return result

    def clear(self) -> None:
        """Remove all messages."""
        self.messages = []
        path = self._path()
        if path.exists():
            path.unlink()

    def to_dict(self) -> dict:
        return {
            "session_id": self.session_id,
            "mode": self.mode,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "message_count": len(self.messages),
        }


class ConversationManager:
    """Manages multiple ConversationSession instances."""

    def __init__(self):
        CONVERSATIONS_DIR.mkdir(parents=True, exist_ok=True)
        self._sessions: dict[str, ConversationSession] = {}
        self._load_all()

    def _load_all(self) -> None:
        """Load all existing sessions from disk."""
        for path in CONVERSATIONS_DIR.glob("*.json"):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                sid = data.get("session_id", path.stem)
                session = ConversationSession(session_id=sid, mode=data.get("mode", "default"))
                self._sessions[sid] = session
            except (json.JSONDecodeError, OSError):
                continue

    def get_or_create(self, session_id: Optional[str] = None, mode: str = "default") -> ConversationSession:
        """Get an existing session or create a new one."""
        if session_id and session_id in self._sessions:
            session = self._sessions[session_id]
            if mode != session.mode:
                session.mode = mode
                session.system_prompt = build_system_prompt(mode)
            return session
        session = ConversationSession(session_id=session_id, mode=mode)
        self._sessions[session.session_id] = session
        return session

    def list_sessions(self) -> list[dict]:
        """List all sessions sorted by most recent."""
        sessions = list(self._sessions.values())
        sessions.sort(key=lambda s: s.updated_at, reverse=True)
        return [s.to_dict() for s in sessions]

    def delete_session(self, session_id: str) -> bool:
        """Delete a session and its data file."""
        if session_id in self._sessions:
            del self._sessions[session_id]
            path = CONVERSATIONS_DIR / f"{session_id}.json"
            if path.exists():
                path.unlink()
            return True
        return False

    def get_session(self, session_id: str) -> Optional[ConversationSession]:
        return self._sessions.get(session_id)