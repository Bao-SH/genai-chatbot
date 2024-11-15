import time
import uuid
from typing import Dict, List
import logging

class ChatSession:
    def __init__(self):
        self.messages: List[Dict] = [
            {"role": "system", "content": "You are a helpful assistant."}
        ]
        self.created_at = time.time()
        self.last_access = time.time()

class ChatSessionManager:
    def __init__(self):
        self.sessions: Dict[str, ChatSession] = {}
        self.session_timeout = 1800  # 30 minutes
        self.logger = logging.getLogger(__name__)

    def create_session(self) -> str:
        self._cleanup_old_sessions()
        session_id = str(uuid.uuid4())
        self.sessions[session_id] = ChatSession()
        self.logger.info(f"Created new session with ID: {session_id}")
        return session_id

    def get_session(self, session_id: str) -> ChatSession:
        if session_id not in self.sessions:
            self.logger.warning(f"Session not found: {session_id}")
            raise ValueError("Invalid session ID or session expired")
        session = self.sessions[session_id]
        session.last_access = time.time()
        self.logger.info(f"Retrieved session: {session_id}")
        return session

    def _cleanup_old_sessions(self):
        current_time = time.time()
        expired_sessions = [
            sid for sid, session in self.sessions.items()
            if current_time - session.last_access > self.session_timeout
        ]
        for sid in expired_sessions:
            del self.sessions[sid]