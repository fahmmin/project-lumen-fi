"""
AI Assistant Router - Universal Chatbot API
Maps natural language to API endpoints and executes them automatically
"""

from fastapi import APIRouter, HTTPException
from typing import Optional, Dict, Any

from backend.models.conversation import (
    ChatRequest,
    ChatResponse,
    ActionTaken,
    CapabilitiesResponse,
    MessageRole
)
from backend.agents.api_registry import get_api_registry
from backend.agents.intent_detection_agent import get_intent_detection_agent
from backend.agents.parameter_extraction_agent import get_parameter_extraction_agent
from backend.agents.api_orchestrator import get_api_orchestrator
from backend.agents.conversation_manager import get_conversation_manager
from backend.agents.response_generator import get_response_generator
from backend.utils.logger import logger

router = APIRouter(prefix="/assistant", tags=["AI Assistant"])


# ==================== ENDPOINTS ====================

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Universal AI Assistant - Natural Language to API Router

    This endpoint allows users to interact with ALL Project Lumen APIs using natural language.

    **Examples:**
    - "I spent $50 at Starbucks" → Creates receipt
    - "Create a goal to save $10000" → Creates financial goal
    - "Show my dashboard" → Returns financial dashboard
    - "Generate a weekly report" → Generates and emails report
    - "How much did I spend this month?" → Returns spending analysis

    **How it works:**
    1. Detects user intent using AI
    2. Maps to correct API endpoint
    3. Extracts required parameters
    4. Executes the API call
    5. Returns friendly natural language response

    **Multi-turn conversations:**
    - Provide session_id to continue a conversation
    - Chatbot will ask follow-up questions if needed
    - Context is maintained across messages
    """
    try:
        # Get manager instances
        registry = get_api_registry()
        intent_agent = get_intent_detection_agent()
        param_agent = get_parameter_extraction_agent()
        orchestrator = get_api_orchestrator()
        conv_manager = get_conversation_manager()
        response_gen = get_response_generator()

        # Get or create session
        session = conv_manager.get_or_create_session(
            session_id=request.session_id,
            user_id=request.user_id
        )

        # Add user message to history
        conv_manager.add_message(
            session_id=session.session_id,
            role=MessageRole.USER,
            content=request.message
        )

        # Build user context
        user_context = {
            "user_id": request.user_id,
            "email": request.email,
            **session.context
        }

        # Check if this is a follow-up response
        if session.context.get("waiting_for_parameter"):
            return await _handle_follow_up(
                request, session, user_context,
                param_agent, orchestrator, conv_manager, response_gen
            )

        # Step 0: Check if this is conversational (no API call needed)
        logger.info(f"Processing message: '{request.message[:100]}...'")

        if intent_agent.is_conversational(request.message):
            logger.info("Message is conversational - generating LLM response")

            # Generate conversational response
            conversational_response = intent_agent.generate_conversational_response(request.message)

            # Add to conversation history
            conv_manager.add_message(
                session_id=session.session_id,
                role=MessageRole.ASSISTANT,
                content=conversational_response
            )

            return ChatResponse(
                response=conversational_response,
                session_id=session.session_id,
                action_taken=None,  # No API call
                follow_up_needed=False,
                suggestions=[
                    "I spent $50 at Starbucks",
                    "Create a goal to save $10000",
                    "Show my dashboard"
                ]
            )

        # Step 1: Detect Intent (API endpoint)
        logger.info("Message requires action - detecting API endpoint")

        intent_result = intent_agent.detect_intent(
            user_message=request.message,
            user_context=user_context
        )

        if not intent_result.get("success", False):
            return ChatResponse(
                response="I'm not sure what you'd like me to do. Could you rephrase that?",
                session_id=session.session_id,
                follow_up_needed=False,
                suggestions=[
                    "Try 'show my dashboard'",
                    "Ask 'what can you do?'",
                    "Say 'I spent $50 at Starbucks'"
                ]
            )

        endpoint_dict = intent_result["endpoint"]
        from backend.agents.api_registry import EndpointSchema
        endpoint = EndpointSchema(**endpoint_dict)

        logger.info(f"Intent detected: {endpoint.method} {endpoint.path} (confidence: {intent_result['confidence']:.2f})")

        # Step 2: Extract Parameters
        param_result = param_agent.extract_parameters(
            user_message=request.message,
            endpoint=endpoint,
            user_context=user_context
        )

        # Step 3: Check if we need follow-up
        if not param_result["success"] and param_result["follow_up_question"]:
            # Store context for follow-up
            conv_manager.update_context(session.session_id, {
                "waiting_for_parameter": True,
                "pending_endpoint": endpoint.dict(),
                "pending_parameters": param_result["parameters"],
                "missing_parameter": param_result["missing_required"][0]
            })

            # Add assistant message
            conv_manager.add_message(
                session_id=session.session_id,
                role=MessageRole.ASSISTANT,
                content=param_result["follow_up_question"]
            )

            return ChatResponse(
                response=param_result["follow_up_question"],
                session_id=session.session_id,
                follow_up_needed=True,
                suggestions=[]
            )

        # Step 4: Execute API Call
        logger.info(f"Executing API call with parameters: {param_result['parameters']}")

        api_result = await orchestrator.execute_endpoint(
            endpoint=endpoint,
            parameters=param_result["parameters"]
        )

        # Step 5: Generate Natural Language Response
        nl_response = response_gen.generate_response(
            endpoint=endpoint,
            api_result=api_result,
            user_message=request.message
        )

        # Create action record
        action = ActionTaken(
            endpoint=endpoint.path,
            method=endpoint.method,
            parameters=param_result["parameters"],
            success=api_result.get("success", False),
            response_data=api_result.get("data"),
            error=api_result.get("error")
        )

        # Add assistant response to history
        conv_manager.add_message(
            session_id=session.session_id,
            role=MessageRole.ASSISTANT,
            content=nl_response["response"],
            metadata={"action": action.dict()}
        )

        return ChatResponse(
            response=nl_response["response"],
            session_id=session.session_id,
            action_taken=action,
            follow_up_needed=False,
            suggestions=nl_response.get("suggestions", [])
        )

    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Assistant error: {str(e)}")


async def _handle_follow_up(
    request: ChatRequest,
    session: Any,
    user_context: Dict,
    param_agent,
    orchestrator,
    conv_manager,
    response_gen
) -> ChatResponse:
    """Handle follow-up response for missing parameters"""
    try:
        # Get pending action from context
        from backend.agents.api_registry import EndpointSchema
        endpoint = EndpointSchema(**session.context["pending_endpoint"])
        previous_params = session.context["pending_parameters"]
        missing_param = session.context["missing_parameter"]

        # Merge with follow-up response
        merged_params = param_agent.merge_with_follow_up(
            previous_params=previous_params,
            follow_up_message=request.message,
            missing_param=missing_param
        )

        # Clear waiting state
        conv_manager.update_context(session.session_id, {
            "waiting_for_parameter": False,
            "pending_endpoint": None,
            "pending_parameters": None,
            "missing_parameter": None
        })

        # Execute API call
        api_result = await orchestrator.execute_endpoint(
            endpoint=endpoint,
            parameters=merged_params
        )

        # Generate response
        nl_response = response_gen.generate_response(
            endpoint=endpoint,
            api_result=api_result,
            user_message=request.message
        )

        # Create action
        action = ActionTaken(
            endpoint=endpoint.path,
            method=endpoint.method,
            parameters=merged_params,
            success=api_result.get("success", False),
            response_data=api_result.get("data"),
            error=api_result.get("error")
        )

        # Add to history
        conv_manager.add_message(
            session_id=session.session_id,
            role=MessageRole.ASSISTANT,
            content=nl_response["response"],
            metadata={"action": action.dict()}
        )

        return ChatResponse(
            response=nl_response["response"],
            session_id=session.session_id,
            action_taken=action,
            follow_up_needed=False,
            suggestions=nl_response.get("suggestions", [])
        )

    except Exception as e:
        logger.error(f"Error handling follow-up: {e}")
        raise


@router.get("/session/{session_id}/history")
async def get_conversation_history(session_id: str, last_n: Optional[int] = None):
    """
    Get conversation history for a session

    Args:
        session_id: Session ID
        last_n: Optional number of recent messages to return
    """
    try:
        conv_manager = get_conversation_manager()

        history = conv_manager.get_conversation_history(
            session_id=session_id,
            last_n=last_n
        )

        if not history:
            raise HTTPException(status_code=404, detail="Session not found")

        return {
            "success": True,
            "session_id": session_id,
            "messages": history,
            "total_messages": len(history)
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting conversation history: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/session/{session_id}")
async def clear_session(session_id: str):
    """
    Clear/delete a conversation session

    Args:
        session_id: Session ID to clear
    """
    try:
        conv_manager = get_conversation_manager()

        success = conv_manager.clear_session(session_id)

        if not success:
            raise HTTPException(status_code=404, detail="Session not found")

        return {
            "success": True,
            "message": f"Session {session_id} cleared successfully"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error clearing session: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/capabilities", response_model=CapabilitiesResponse)
async def get_capabilities():
    """
    Get chatbot capabilities - list of all actions it can perform

    Returns a comprehensive list of what the AI assistant can do,
    organized by category with example phrases.
    """
    try:
        registry = get_api_registry()

        categories_dict = {}

        for endpoint in registry.get_all_endpoints():
            category = endpoint.category

            if category not in categories_dict:
                categories_dict[category] = {
                    "category": category,
                    "name": category.replace("_", " ").title(),
                    "endpoints": [],
                    "examples": []
                }

            categories_dict[category]["endpoints"].append({
                "path": endpoint.path,
                "method": endpoint.method,
                "description": endpoint.summary
            })

            # Add unique examples
            for example in endpoint.examples:
                if example not in categories_dict[category]["examples"]:
                    categories_dict[category]["examples"].append(example)

        # Convert to list
        categories = list(categories_dict.values())

        # Overall examples
        overall_examples = [
            "I spent $50 at Starbucks",
            "Create a goal to save $10000",
            "Show my dashboard",
            "Generate a weekly report",
            "How much did I spend this month?",
            "What subscriptions am I paying for?",
            "Add a family member",
            "Show my financial health score",
            "What's my spending compared to others?",
            "Set my monthly salary to $5000"
        ]

        return CapabilitiesResponse(
            categories=categories,
            total_endpoints=len(registry.get_all_endpoints()),
            examples=overall_examples
        )

    except Exception as e:
        logger.error(f"Error getting capabilities: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status")
async def get_status():
    """
    Get assistant system status

    Returns status of all components
    """
    try:
        registry = get_api_registry()

        return {
            "success": True,
            "status": "operational",
            "components": {
                "api_registry": {
                    "status": "operational",
                    "endpoints_registered": len(registry.get_all_endpoints()),
                    "categories": len(registry.get_categories())
                },
                "intent_detection": {
                    "status": "operational",
                    "llm_provider": "ollama"
                },
                "conversation_manager": {
                    "status": "operational"
                }
            },
            "version": "1.0.0"
        }

    except Exception as e:
        logger.error(f"Error getting status: {e}")
        raise HTTPException(status_code=500, detail=str(e))
