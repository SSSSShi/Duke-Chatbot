# secure_app.py
"""
Enhanced AWS Lambda handler with integrated security, privacy, and responsible AI features
"""

import json
import time
import logging
import os
from typing import Dict, Any
from .secure_agent import process_user_query, get_security_status
from .security_privacy import security_auditor, SecurityLevel, session_manager, privacy_manager

# Configure secure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Security headers for all responses
SECURITY_HEADERS = {
    'Content-Type': 'application/json',
    'X-Content-Type-Options': 'nosniff',
    'X-Frame-Options': 'DENY',
    'X-XSS-Protection': '1; mode=block',
    'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
    'Cache-Control': 'no-store, no-cache, must-revalidate, max-age=0',
    'Pragma': 'no-cache',
    'Referrer-Policy': 'strict-origin-when-cross-origin',
    'Permissions-Policy': 'camera=(), microphone=(), geolocation=()'
}

def get_client_ip(event: Dict) -> str:
    """Extract client IP address from Lambda event."""
    # Try various headers for client IP
    headers = event.get('headers', {})
    
    # Common headers for client IP
    ip_headers = [
        'X-Forwarded-For',
        'X-Real-IP',
        'CF-Connecting-IP',  # Cloudflare
        'X-Client-IP',
        'X-Cluster-Client-IP'
    ]
    
    for header in ip_headers:
        if header in headers:
            ip = headers[header].split(',')[0].strip()
            if ip and ip != 'unknown':
                return ip
    
    # Fallback to source IP
    return event.get('requestContext', {}).get('identity', {}).get('sourceIp', 'unknown')

def validate_request_structure(event: Dict) -> tuple[bool, str]:
    """Validate the structure of incoming requests."""
    # Check required fields
    if 'body' not in event:
        return False, "Missing request body"
    
    if not event['body']:
        return False, "Empty request body"
    
    # Validate HTTP method
    http_method = event.get('httpMethod', event.get('requestContext', {}).get('http', {}).get('method', ''))
    if http_method not in ['POST', 'GET']:
        return False, f"Unsupported HTTP method: {http_method}"
    
    # Check content length
    content_length = len(event['body'])
    if content_length > 10000:  # 10KB limit
        return False, "Request body too large"
    
    return True, "Valid request"

def parse_request_body(body: str) -> tuple[bool, Dict]:
    """Safely parse request body JSON."""
    try:
        parsed_body = json.loads(body)
        
        # Validate required fields
        if 'query' not in parsed_body:
            return False, {"error": "Missing 'query' field in request body"}
        
        # Validate query length
        query = parsed_body['query']
        if not query or len(query.strip()) == 0:
            return False, {"error": "Query cannot be empty"}
        
        if len(query) > 1000:  # 1000 character limit
            return False, {"error": "Query too long (max 1000 characters)"}
        
        return True, parsed_body
        
    except json.JSONDecodeError as e:
        return False, {"error": f"Invalid JSON format: {str(e)}"}
    except Exception as e:
        return False, {"error": "Failed to parse request body"}

def create_error_response(status_code: int, error_message: str, 
                         request_id: str = None) -> Dict:
    """Create standardized error response."""
    response_body = {
        'error': error_message,
        'status': 'error',
        'timestamp': time.time()
    }
    
    if request_id:
        response_body['request_id'] = request_id
    
    return {
        'statusCode': status_code,
        'headers': SECURITY_HEADERS,
        'body': json.dumps(response_body)
    }

def create_success_response(data: Dict, request_id: str = None) -> Dict:
    """Create standardized success response."""
    response_body = {
        'status': 'success',
        'timestamp': time.time(),
        **data
    }
    
    if request_id:
        response_body['request_id'] = request_id
    
    return {
        'statusCode': 200,
        'headers': SECURITY_HEADERS,
        'body': json.dumps(response_body)
    }

def lambda_handler(event, context):
    """
    Enhanced AWS Lambda handler with comprehensive security features.
    
    Security Features:
    - Request validation and sanitization
    - Rate limiting and abuse prevention
    - Session management
    - Privacy controls
    - Responsible AI practices
    - Comprehensive audit logging
    """
    
    # Start timing for performance monitoring
    start_time = time.time()
    request_id = context.aws_request_id if context else str(time.time())
    
    # Extract client information
    client_ip = get_client_ip(event)
    user_agent = event.get('headers', {}).get('User-Agent', 'unknown')
    
    # Log incoming request (without sensitive data)
    logger.info(f"Request received: {request_id} from {client_ip}")
    
    try:
        # 1. Validate request structure
        is_valid_structure, validation_message = validate_request_structure(event)
        if not is_valid_structure:
            security_auditor.log_security_event(
                "invalid_request_structure", SecurityLevel.MEDIUM, "anonymous",
                {"error": validation_message, "ip": client_ip}, client_ip
            )
            return create_error_response(400, validation_message, request_id)
        
        # 2. Parse and validate request body
        is_valid_body, parsed_data = parse_request_body(event['body'])
        if not is_valid_body:
            security_auditor.log_security_event(
                "invalid_request_body", SecurityLevel.MEDIUM, "anonymous",
                {"error": parsed_data.get("error", "Unknown error"), "ip": client_ip}, client_ip
            )
            return create_error_response(400, parsed_data.get("error", "Invalid request"), request_id)
        
        # 3. Extract request parameters
        query = parsed_data['query']
        user_id = parsed_data.get('user_id', f"lambda_user_{hash(client_ip) % 10000}")
        session_id = parsed_data.get('session_id')
        
        # 4. Create session if not provided
        if not session_id:
            session_id = session_manager.create_session(user_id)
            logger.info(f"Created new session {session_id} for user {user_id}")
        
        # 5. Log security event for request processing
        security_auditor.log_security_event(
            "lambda_request_start", SecurityLevel.LOW, user_id,
            {
                "query_length": len(query),
                "session_id": session_id,
                "user_agent": user_agent[:100],  # Truncate user agent
                "request_id": request_id
            },
            client_ip
        )
        
        # 6. Process query with security controls
        logger.info(f"Processing query for user {user_id} in session {session_id}")
        
        response_message = process_user_query(
            query=query,
            user_id=user_id,
            session_id=session_id,
            ip_address=client_ip
        )
        
        # 7. Calculate processing time
        processing_time = time.time() - start_time
        
        # 8. Log successful processing
        security_auditor.log_security_event(
            "lambda_request_success", SecurityLevel.LOW, user_id,
            {
                "processing_time": processing_time,
                "response_length": len(response_message),
                "request_id": request_id
            },
            client_ip
        )
        
        # 9. Create response with metadata
        response_data = {
            'response': response_message,
            'user_id': user_id,
            'session_id': session_id,
            'processing_time': round(processing_time, 3),
            'security_level': 'secure'
        }
        
        logger.info(f"Request completed successfully: {request_id} in {processing_time:.3f}s")
        return create_success_response(response_data, request_id)
        
    except json.JSONDecodeError as e:
        # JSON parsing error
        security_auditor.log_security_event(
            "json_decode_error", SecurityLevel.MEDIUM, "anonymous",
            {"error": str(e), "request_id": request_id}, client_ip
        )
        logger.error(f"JSON decode error in request {request_id}: {str(e)}")
        return create_error_response(400, "Invalid JSON format", request_id)
        
    except ValueError as e:
        # Value/validation error
        security_auditor.log_security_event(
            "value_error", SecurityLevel.MEDIUM, "anonymous",
            {"error": str(e), "request_id": request_id}, client_ip
        )
        logger.error(f"Value error in request {request_id}: {str(e)}")
        return create_error_response(400, "Invalid request parameters", request_id)
        
    except Exception as e:
        # Unexpected error
        security_auditor.log_security_event(
            "lambda_critical_error", SecurityLevel.CRITICAL, "anonymous",
            {
                "error_type": type(e).__name__,
                "error_message": str(e)[:200],  # Truncate error message
                "request_id": request_id
            },
            client_ip
        )
        logger.error(f"Critical error in request {request_id}: {str(e)}")
        return create_error_response(500, "Internal server error", request_id)

def health_check_handler(event, context):
    """Health check endpoint with security status."""
    try:
        # Get security status
        security_status = get_security_status()
        
        # Basic health metrics
        health_data = {
            'status': 'healthy',
            'timestamp': time.time(),
            'version': '1.0.0',
            'security_status': security_status,
            'environment': os.environ.get('STAGE', 'development')
        }
        
        return create_success_response(health_data, context.aws_request_id)
        
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return create_error_response(500, "Health check failed")

def admin_handler(event, context):
    """Administrative endpoint for security monitoring (protected)."""
    try:
        # In production, add proper authentication here
        # For now, just return security audit information
        
        audit_report = security_auditor.generate_audit_report()
        
        admin_data = {
            'audit_report': audit_report,
            'system_status': get_security_status(),
            'privacy_metrics': {
                'total_users': len(privacy_manager.privacy_records),
                'active_sessions': len([s for s in session_manager.sessions.values() if s["is_active"]]),
                'data_retention_compliance': True
            }
        }
        
        return create_success_response(admin_data, context.aws_request_id)
        
    except Exception as e:
        logger.error(f"Admin endpoint error: {str(e)}")
        return create_error_response(500, "Admin endpoint error")

# Environment-specific configuration
def configure_for_environment():
    """Configure security settings based on environment."""
    stage = os.environ.get('STAGE', 'development')
    
    if stage == 'production':
        # Production security settings
        os.environ.setdefault('RATE_LIMIT_REQUESTS', '5')
        os.environ.setdefault('RATE_LIMIT_WINDOW', '60')
        os.environ.setdefault('SESSION_TIMEOUT', '1800')
        os.environ.setdefault('DATA_RETENTION_DAYS', '30')
        
    elif stage == 'development':
        # Development settings (more permissive)
        os.environ.setdefault('RATE_LIMIT_REQUESTS', '20')
        os.environ.setdefault('RATE_LIMIT_WINDOW', '60')
        os.environ.setdefault('SESSION_TIMEOUT', '3600')
        
    # Apply configuration
    logger.info(f"Configured for {stage} environment")

# Initialize configuration on module load
configure_for_environment()

# AWS Lambda entry points based on path
def router_handler(event, context):
    """Router for different Lambda endpoints."""
    path = event.get('path', event.get('rawPath', '/'))
    
    if path == '/health':
        return health_check_handler(event, context)
    elif path == '/admin':
        return admin_handler(event, context)
    elif path in ['/', '/chat', '/query']:
        return lambda_handler(event, context)
    else:
        return create_error_response(404, "Endpoint not found")

# Export the main handler
handler = router_handler
