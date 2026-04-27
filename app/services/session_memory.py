import time
from dataclasses import dataclass, field

@dataclass
class SessionState:
    updated_at: float
    turns: list[tuple[str, str]] = field(default_factory=list)

class SessionMemory:
    def __init__(self, max_turns: int = 4, ttl_seconds: int = 900) -> None:
        self.max_turns = max_turns
        self.ttl_seconds = ttl_seconds
        self._sessions: dict[str, SessionState] = {}

    def get_history(self, session_id: str | None) -> str | None:
        if not session_id:
            return None
        self._delete_expired()
        state = self._sessions.get(session_id)
        if state is None:
            return None
        lines: list[str] = []
        for user_message, assistant_answer in state.turns[-self.max_turns :]:
            lines.append(f"Usuario: {user_message}")
            lines.append(f"Assistente: {assistant_answer}")
        return "\n".join(lines) if lines else None

    def append(self, session_id: str | None, message: str, answer: str) -> None:
        if not session_id:
            return
        self._delete_expired()
        state = self._sessions.setdefault(
            session_id,
            SessionState(updated_at=time.time()),
        )
        state.updated_at = time.time()
        state.turns.append((message, answer))
        state.turns = state.turns[-self.max_turns :]

        
    def _delete_expired(self) -> None:
        now = time.time()
        expired = [
            session_id
            for session_id, state in self._sessions.items()
            if now - state.updated_at > self.ttl_seconds
        ]
        for session_id in expired:
            del self._sessions[session_id]