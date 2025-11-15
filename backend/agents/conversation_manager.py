"""
Conversation Manager - Handles Multi-Turn Conversations and Session State
"""

from typing import Dict, Optional
import uuid
import json
from pathlib import Path

from backend.models.conversation import (
    ConversationSession,
    ConversationMessage,
    MessageRole
)
from backend.config import settings
from backend.utils.logger import logger


class ConversationManager:
    """
    Manages conversation sessions and context across multiple turns
    Stores session state for follow-up questions and multi-step interactions
    """

    def __init__(self):
        """Initialize conversation manager"""
        self.sessions: Dict[str, ConversationSession] = {}
        self.sessions_file = settings.DATA_DIR / "conversation_sessions.json"
        self._load_sessions()

    def create_session(
        self,
        user_id: Optional[str] = None,
        initial_context: Optional[Dict] = None
    ) -> ConversationSession:
        """
        Create a new conversation session

        Args:
            user_id: Optional user ID
            initial_context: Optional initial context

        Returns:
            New ConversationSession
        """
        session_id = str(uuid.uuid4())

        session = ConversationSession(
            session_id=session_id,
            user_id=user_id,
            context=initial_context or {}
        )

        self.sessions[session_id] = session
        self._save_sessions()

        logger.info(f"Created new conversation session: {session_id}")
        return session

    def get_session(self, session_id: str) -> Optional[ConversationSession]:
        """Get existing session by ID"""
        return self.sessions.get(session_id)

    def get_or_create_session(
        self,
        session_id: Optional[str] = None,
        user_id: Optional[str] = None
    ) -> ConversationSession:
        """Get existing session or create new one"""
        if session_id and session_id in self.sessions:
            return self.sessions[session_id]
        else:
            return self.create_session(user_id=user_id)

    def add_message(
        self,
        session_id: str,
        role: MessageRole,
        content: str,
        metadata: Optional[Dict] = None
    ) -> bool:
        """Add message to session"""
        session = self.get_session(session_id)
        if not session:
            logger.warning(f"Session not found: {session_id}")
            return False

        message = ConversationMessage(
            role=role,
            content=content,
            metadata=metadata
        )

        session.messages.append(message)
        self._save_sessions()

        return True

    def update_context(
        self,
        session_id: str,
        context_update: Dict
    ) -> bool:
        """Update session context"""
        session = self.get_session(session_id)
        if not session:
            return False

        session.context.update(context_update)
        self._save_sessions()

        return True

    def get_context(self, session_id: str) -> Dict:
        """Get session context"""
        session = self.get_session(session_id)
        return session.context if session else {}

    def get_conversation_history(
        self,
        session_id: str,
        last_n: Optional[int] = None
    ) -> list:
        """Get conversation history"""
        session = self.get_session(session_id)
        if not session:
            return []

        messages = session.messages
        if last_n:
            messages = messages[-last_n:]

        return [
            {
                "role": msg.role,
                "content": msg.content,
                "timestamp": msg.timestamp.isoformat()
            }
            for msg in messages
        ]

    def clear_session(self, session_id: str) -> bool:
        """Clear/delete a session"""
        if session_id in self.sessions:
            del self.sessions[session_id]
            self._save_sessions()
            logger.info(f"Cleared session: {session_id}")
            return True
        return False

    def _load_sessions(self):
        """Load sessions from file"""
        if not self.sessions_file.exists():
            return

        try:
            with open(self.sessions_file, 'r') as f:
                data = json.load(f)

            for session_id, session_data in data.items():
                self.sessions[session_id] = ConversationSession(**session_data)

            logger.info(f"Loaded {len(self.sessions)} conversation sessions")

        except Exception as e:
            logger.error(f"Error loading sessions: {e}")

    def _save_sessions(self):
        """Save sessions to file"""
        try:
            # Convert sessions to dict
            data = {
                session_id: session.dict()
                for session_id, session in self.sessions.items()
            }

            with open(self.sessions_file, 'w') as f:
                json.dump(data, f, indent=2, default=str)

        except Exception as e:
            logger.error(f"Error saving sessions: {e}")


# Global instance
_conversation_manager = None


def get_conversation_manager() -> ConversationManager:
    """Get global conversation manager instance"""
    global _conversation_manager
    if _conversation_manager is None:
        _conversation_manager = ConversationManager()
    return _conversation_manager
