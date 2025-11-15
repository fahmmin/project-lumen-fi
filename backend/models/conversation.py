"""
Conversation Models - Pydantic models for chatbot conversations
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class MessageRole(str, Enum):
    """Message role in conversation"""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class ConversationMessage(BaseModel):
    """Single message in a conversation"""
    role: MessageRole
    content: str
    timestamp: datetime = Field(default_factory=datetime.now)
    metadata: Optional[Dict[str, Any]] = None


class ConversationSession(BaseModel):
    """Conversation session state"""
    session_id: str
    user_id: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    messages: List[ConversationMessage] = []
    context: Dict[str, Any] = {}  # Persistent context (extracted params, pending actions, etc.)
    status: str = "active"  # active, waiting_for_input, completed


class ChatRequest(BaseModel):
    """Chat request from user"""
    message: str = Field(..., min_length=1, description="User's message")
    user_id: Optional[str] = Field(None, description="User ID for context")
    session_id: Optional[str] = Field(None, description="Session ID for multi-turn conversation")
    email: Optional[str] = Field(None, description="User's email address")


class ActionTaken(BaseModel):
    """Details of action taken by chatbot"""
    endpoint: str
    method: str
    parameters: Dict[str, Any]
    success: bool
    response_data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class ChatResponse(BaseModel):
    """Chat response to user"""
    response: str = Field(..., description="Natural language response")
    session_id: str = Field(..., description="Session ID")
    action_taken: Optional[ActionTaken] = None
    follow_up_needed: bool = Field(False, description="Whether chatbot needs more info")
    follow_up_question: Optional[str] = None
    suggestions: List[str] = Field(default_factory=list, description="Suggested next actions")
    metadata: Optional[Dict[str, Any]] = None


class CapabilitiesResponse(BaseModel):
    """Response listing chatbot capabilities"""
    categories: List[Dict[str, Any]]
    total_endpoints: int
    examples: List[str]
