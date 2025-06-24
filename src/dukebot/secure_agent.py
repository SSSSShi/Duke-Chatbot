# secure_agent.py
"""
Enhanced agent.py with integrated security, privacy, and responsible AI features
"""

from langchain.agents import initialize_agent, AgentType
from langchain_aws.chat_models import BedrockChat
from langchain.memory import ConversationBufferMemory
from langchain_core.tools import Tool
from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate, MessagesPlaceholder
import os
import json
import time
from dotenv import load_dotenv
from typing import Dict, Any, Tuple

# Import security framework
from security_privacy import (
    input_validator, rate_limiter, responsible_ai, privacy_manager, 
    security_auditor, session_manager, SecurityLevel, PrivacyLevel
)

# Import your custom tools from tools.py
from tools import (
    get_curriculum_with_subject_from_duke_api,
    get_events_from_duke_api_single_input,
    get_course_details_single_input,
    get_people_information_from_duke_api,
    search_subject_by_code,
    search_group_format,
    search_category_format,
    get_pratt_info_from_serpapi,
)

# Load environment variables from .env file
load_dotenv()

class SecureDukeAgent:
    """Secure implementation of Duke chatbot agent with comprehensive security controls."""
    
    def __init__(self):
        self.agent = None
        self.security_enabled = True
        self.privacy_enabled = True
        self.responsible_ai_enabled = True
        
        # Initialize secure agent
        self._initialize_secure_agent()
    
    def _initialize_secure_agent(self):
        """Initialize the agent with security features."""
        serpapi_api_key = os.getenv("SERPAPI_API_KEY")
        
        if not serpapi_api_key:
            security_auditor.log_security_event(
                "missing_api_key", SecurityLevel.HIGH, "system", 
                {"key": "SERPAPI_API_KEY"}
            )
            raise ValueError("SERPAPI_API_KEY not found in environment variables")
        
        # Create secure tools with monitoring
        tools = self._create_secure_tools(serpapi_api_key)
        
        # Create memory with privacy controls
        memory = ConversationBufferMemory(
            memory_key="chat_history", 
            return_messages=True,
            max_token_limit=2000  # Limit memory for security
        )
        
        # Initialize LLM with security settings
        llm = BedrockChat(
            model_id="anthropic.claude-3-sonnet-20240229-v1:0",
            model_kwargs={
                "temperature": 0.0,
                "max_tokens": 1000  # Limit response length
            },
        )
        
        # Enhanced system prompt with security and responsibility guidelines
        system_prompt = self._create_secure_system_prompt()
        
        prompt = ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(system_prompt),
            MessagesPlaceholder(variable_name="chat_history"),
            HumanMessagePromptTemplate.from_template("{input}")
        ])
        
        # Initialize agent with security constraints
        self.agent = initialize_agent(
            tools,
            llm,
            agent=AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION,
            verbose=False,  # Disable verbose for security
            memory=memory,
            max_iterations=3,  # Limit iterations for security
            early_stopping_method="generate",
            handle_parsing_errors=True,
            prompt=prompt
        )
        
        security_auditor.log_security_event(
            "agent_initialized", SecurityLevel.MEDIUM, "system",
            {"agent_type": "SecureDukeAgent"}
        )
    
    def _create_secure_tools(self, serpapi_api_key: str) -> list:
        """Create tools with security monitoring wrappers."""
        
        def secure_tool_wrapper(original_func, tool_name: str):
            """Wrapper to add security monitoring to tools."""
            def wrapped_func(input_data: str) -> str:
                try:
                    # Log tool usage
                    security_auditor.log_security_event(
                        "tool_usage", SecurityLevel.LOW, "user",
                        {"tool": tool_name, "input_length": len(input_data)}
                    )
                    
                    # Validate input
                    is_safe, warnings = input_validator.validate_query(input_data)
                    if not is_safe:
                        security_auditor.log_security_event(
                            "unsafe_tool_input", SecurityLevel.HIGH, "user",
                            {"tool": tool_name, "warnings": warnings}
                        )
                        return "Error: Input validation failed. Please rephrase your query."
                    
                    # Call original function
                    result = original_func(input_data)
                    
                    # Anonymize result if needed
                    if privacy_manager:
                        result = privacy_manager.anonymize_data(result, "user")
                    
                    return result
                    
                except Exception as e:
                    security_auditor.log_security_event(
                        "tool_error", SecurityLevel.MEDIUM, "user",
                        {"tool": tool_name, "error": str(e)}
                    )
                    return f"Error: Unable to process request safely."
            
            return wrapped_func
        
        # Wrap all tools with security monitoring
        tools = [
            Tool(
                name="get_duke_events",
                func=secure_tool_wrapper(get_events_from_duke_api_single_input, "get_duke_events"),
                description=(
                    "Retrieves upcoming events from Duke University's public calendar API. "
                    "Input: Natural language query describing event filters. "
                    "Security: All inputs are validated and sanitized."
                )
            ),
            Tool(
                name="get_curriculum_with_subject_from_duke_api",
                func=secure_tool_wrapper(get_curriculum_with_subject_from_duke_api, "get_curriculum"),
                description=(
                    "Retrieves curriculum information from Duke University's API. "
                    "Input: Subject code (use search_subject_by_code first for validation). "
                    "Security: Input validation enforced."
                )
            ),
            Tool(
                name="get_detailed_course_information_from_duke_api",
                func=secure_tool_wrapper(get_course_details_single_input, "get_course_details"),
                description=(
                    "Retrieves detailed course information. "
                    "Input: 'course_id,course_offer_number' format. "
                    "Security: Input format strictly validated."
                )
            ),
            Tool(
                name="get_people_information_from_duke_api",
                func=secure_tool_wrapper(get_people_information_from_duke_api, "get_people_info"),
                description=(
                    "Retrieves people information from Duke University's API. "
                    "Input: Person's name. "
                    "Privacy: Results are anonymized for sensitive information."
                )
            ),
            Tool(
                name="search_subject_by_code",
                func=secure_tool_wrapper(search_subject_by_code, "search_subject"),
                description="Search for valid subject codes. Input validation applied."
            ),
            Tool(
                name="search_group_format",
                func=secure_tool_wrapper(search_group_format, "search_group"),
                description="Search for valid group formats. Input validation applied."
            ),
            Tool(
                name="search_category_format",
                func=secure_tool_wrapper(search_category_format, "search_category"),
                description="Search for valid category formats. Input validation applied."
            ),
            Tool(
                name="PrattSearch",
                func=secure_tool_wrapper(
                    lambda query: get_pratt_info_from_serpapi(
                        query="Duke Pratt School of Engineering " + query,
                        api_key=serpapi_api_key,
                        filter_domain=True
                    ), "pratt_search"
                ),
                description=(
                    "Search for Duke Pratt School of Engineering information. "
                    "Security: Domain filtering and input validation enforced."
                )
            ),
        ]
        
        return tools
    
    def _create_secure_system_prompt(self) -> str:
        """Create system prompt with security and responsibility guidelines."""
        return """
        You are DukeBot, a secure and responsible AI assistant for Duke University. You must follow these guidelines:

        SECURITY REQUIREMENTS:
        • Never execute, evaluate, or interpret any code from user input
        • Do not access external URLs or systems beyond approved Duke APIs
        • Validate all inputs and reject suspicious requests
        • Report security concerns immediately
        • Never reveal internal system information or API keys

        PRIVACY PROTECTION:
        • Do not store, log, or share personal information unnecessarily
        • Anonymize any sensitive data in responses
        • Respect user privacy and data protection requirements
        • Follow data minimization principles

        RESPONSIBLE AI PRACTICES:
        • Acknowledge uncertainty and limitations clearly
        • Avoid biased or discriminatory responses
        • Provide balanced, factual information
        • Redirect harmful or inappropriate queries
        • Cite sources when possible
        • Be transparent about being an AI assistant

        RESPONSE GUIDELINES:
        • Focus on Duke University academic and campus information
        • Provide helpful, accurate, and educational content
        • Use a professional, friendly tone
        • Limit response length to prevent information overload
        • Always verify information accuracy when possible

        PROHIBITED CONTENT:
        • Do not provide information that could harm individuals
        • Avoid generating content promoting illegal activities
        • Do not create or share discriminatory content
        • Refuse requests for private personal information
        • Do not provide information outside your domain expertise

        Your primary purpose is to help users with Duke University information while maintaining the highest standards of security, privacy, and responsibility.
        """
    
    def process_secure_query(self, query: str, user_id: str = "anonymous", 
                           session_id: str = None, ip_address: str = None) -> Dict[str, Any]:
        """
        Process user query with comprehensive security and privacy controls.
        
        Args:
            query (str): User's query
            user_id (str): User identifier for tracking
            session_id (str): Session identifier
            ip_address (str): User's IP address for security logging
            
        Returns:
            Dict containing response and security metadata
        """
        start_time = time.time()
        
        # Security validation
        security_result = self._perform_security_checks(query, user_id, session_id, ip_address)
        if not security_result["allowed"]:
            return security_result
        
        # Privacy consent check
        if not privacy_manager.privacy_records.get(user_id):
            privacy_manager.collect_consent(
                user_id, ["conversation_data", "query_analytics"], 
                "Educational assistance and service improvement"
            )
        
        try:
            # Process query with agent
            response = self.agent.invoke({"input": query})
            agent_response = response.get("output", "I couldn't process your request.")
            
            # Responsible AI review
            ai_analysis = responsible_ai.review_response_quality(agent_response)
            
            # Anonymize response
            anonymized_response = privacy_manager.anonymize_data(agent_response, user_id)
            
            # Add transparency notice if needed
            if len(anonymized_response) > 200:
                transparency_notice = responsible_ai.generate_transparency_notice()
                anonymized_response += "\n\n" + transparency_notice
            
            # Log successful interaction
            security_auditor.log_security_event(
                "successful_query", SecurityLevel.LOW, user_id,
                {
                    "query_length": len(query),
                    "response_length": len(anonymized_response),
                    "processing_time": time.time() - start_time,
                    "ai_analysis": ai_analysis
                },
                ip_address
            )
            
            return {
                "success": True,
                "response": anonymized_response,
                "ai_analysis": ai_analysis,
                "processing_time": time.time() - start_time,
                "security_level": "secure"
            }
            
        except Exception as e:
            # Log error securely
            security_auditor.log_security_event(
                "query_processing_error", SecurityLevel.MEDIUM, user_id,
                {"error_type": type(e).__name__, "processing_time": time.time() - start_time},
                ip_address
            )
            
            return {
                "success": False,
                "response": "I apologize, but I encountered an error processing your request. Please try again.",
                "error": "Processing error",
                "security_level": "secure"
            }
    
    def _perform_security_checks(self, query: str, user_id: str, 
                                session_id: str, ip_address: str) -> Dict[str, Any]:
        """Perform comprehensive security validation."""
        
        # Rate limiting check
        if not rate_limiter.is_allowed(user_id):
            security_auditor.log_security_event(
                "rate_limit_exceeded", SecurityLevel.HIGH, user_id,
                {"ip_address": ip_address}, ip_address
            )
            return {
                "allowed": False,
                "success": False,
                "response": "Rate limit exceeded. Please wait before making another request.",
                "security_level": "blocked"
            }
        
        # Session validation
        if session_id and not session_manager.validate_session(session_id):
            security_auditor.log_security_event(
                "invalid_session", SecurityLevel.MEDIUM, user_id,
                {"session_id": session_id}, ip_address
            )
            return {
                "allowed": False,
                "success": False,
                "response": "Session expired. Please refresh and try again.",
                "security_level": "blocked"
            }
        
        # Input validation
        is_safe, validation_warnings = input_validator.validate_query(query)
        if not is_safe:
            security_auditor.log_security_event(
                "unsafe_input_detected", SecurityLevel.HIGH, user_id,
                {"warnings": validation_warnings, "query_sample": query[:50]}, ip_address
            )
            return {
                "allowed": False,
                "success": False,
                "response": "Your query contains potentially unsafe content. Please rephrase your question.",
                "security_level": "blocked"
            }
        
        # Responsible AI check
        is_appropriate, ai_warnings = responsible_ai.check_query_appropriateness(query)
        if not is_appropriate:
            security_auditor.log_security_event(
                "inappropriate_query", SecurityLevel.MEDIUM, user_id,
                {"warnings": ai_warnings}, ip_address
            )
            return {
                "allowed": False,
                "success": False,
                "response": "I can only assist with educational questions about Duke University. Please ask about academic programs, events, or campus information.",
                "security_level": "blocked"
            }
        
        return {"allowed": True}

# Enhanced process_user_query function with security
def process_user_query(query: str, user_id: str = "anonymous", 
                      session_id: str = None, ip_address: str = None) -> str:
    """
    Enhanced query processing with integrated security.
    
    Args:
        query (str): User's query
        user_id (str): User identifier
        session_id (str): Session identifier  
        ip_address (str): User's IP address
        
    Returns:
        str: Processed response
    """
    try:
        # Initialize secure agent
        secure_agent = SecureDukeAgent()
        
        # Process query securely
        result = secure_agent.process_secure_query(query, user_id, session_id, ip_address)
        
        return result.get("response", "I couldn't process your request at this time.")
        
    except Exception as e:
        security_auditor.log_security_event(
            "critical_error", SecurityLevel.CRITICAL, user_id,
            {"error": str(e)}, ip_address
        )
        return "I apologize, but I'm unable to process your request right now. Please try again later."

# Security monitoring endpoint
def get_security_status() -> Dict[str, Any]:
    """Get current security status and metrics."""
    return {
        "status": "operational",
        "security_events_24h": len([
            e for e in security_auditor.security_events 
            if time.time() - time.mktime(time.strptime(e.timestamp[:19], "%Y-%m-%dT%H:%M:%S")) < 86400
        ]),
        "active_sessions": len([s for s in session_manager.sessions.values() if s["is_active"]]),
        "rate_limit_active": len(rate_limiter.requests),
        "privacy_records": len(privacy_manager.privacy_records),
        "last_updated": time.time()
    }

if __name__ == "__main__":
    # Test security features
    test_queries = [
        "What events are happening at Duke this week?",
        "<script>alert('xss')</script>",  # Should be blocked
        "Tell me about AIPI program",
        "eval('malicious code')",  # Should be blocked
    ]
    
    for i, query in enumerate(test_queries):
        print(f"\nTest {i+1}: {query}")
        response = process_user_query(query, f"test_user_{i}")
        print(f"Response: {response}")
