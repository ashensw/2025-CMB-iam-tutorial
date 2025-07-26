"""
FastAPI dependency injection for authentication and database sessions
"""
import jwt
import logging
import os
import requests
from fastapi import Depends, HTTPException, status, Security, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials, SecurityScopes
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any
from dotenv import load_dotenv
from jwt import PyJWKClient
from .database import SessionLocal
from .schemas import TokenInfo, TokenData, Actor

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)
security = HTTPBearer(auto_error=False)

# Configuration from environment variables
ENABLE_BACKEND_TOKEN_VALIDATION = os.getenv('ENABLE_BACKEND_TOKEN_VALIDATION', 'true').lower() == 'true'
AUTH_HEADER_NAME = os.getenv('AUTH_HEADER_NAME', 'Authorization')
ENABLE_TOKEN_LOGGING = os.getenv('ENABLE_TOKEN_LOGGING', 'true').lower() == 'true'

# JWT Configuration
JWKS_URL = os.getenv('JWKS_URL')
JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')
JWT_ALGORITHM = os.getenv('JWT_ALGORITHM', 'RS256')
JWT_ISSUER = os.getenv('JWT_ISSUER')
JWT_AUDIENCE = os.getenv('JWT_AUDIENCE')

# Initialize JWKS client if JWKS URL is provided
JWKS_CLIENT = None
if JWKS_URL and ENABLE_BACKEND_TOKEN_VALIDATION:
    try:
        JWKS_CLIENT = PyJWKClient(JWKS_URL)
        if ENABLE_TOKEN_LOGGING:
            logger.info(f"✅ [AUTH DEBUG] JWKS client initialized with URL: {JWKS_URL}")
    except Exception as e:
        logger.error(f"❌ [AUTH DEBUG] Failed to initialize JWKS client: {e}")
        JWKS_CLIENT = None

# Scope mapping based on OpenAPI specification
ENDPOINT_SCOPE_MAPPING = {
    # Orders endpoints
    ("POST", "/api/orders"): ["order:write"],
    ("GET", "/api/orders"): ["order:read"],
    ("GET", "/api/orders/{order_id}"): ["order:read"],
    
    # System endpoints (no specific scopes required, just valid token)
    ("GET", "/api/system/status"): [],
    ("GET", "/api/token-info"): [],
    
    # Public endpoints (no authentication)
    ("GET", "/"): None,
    ("GET", "/health"): None,
    ("GET", "/api/menu"): None,
}


def get_required_scopes_for_endpoint(method: str, path: str) -> list:
    """
    Get required scopes for a specific endpoint based on OpenAPI specification.
    
    Args:
        method: HTTP method (GET, POST, etc.)
        path: API path
        
    Returns:
        List of required scopes, empty list if no scopes required, None if public endpoint
    """
    # Normalize path for comparison (handle path parameters)
    normalized_path = path
    if "/orders/" in path and path != "/api/orders":
        normalized_path = "/api/orders/{order_id}"
    
    return ENDPOINT_SCOPE_MAPPING.get((method.upper(), normalized_path), [])


def get_db():
    """Database session dependency"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def extract_token_from_request(request: Request) -> Optional[str]:
    """
    Extract JWT token from configurable header.
    
    Args:
        request: FastAPI request object
        
    Returns:
        JWT token string or None if not found
    """
    # Try to get token from configured header
    header_value = request.headers.get(AUTH_HEADER_NAME)
    
    if header_value:
        # Handle Bearer format
        if header_value.startswith("Bearer "):
            token = header_value.replace("Bearer ", "")
            if ENABLE_TOKEN_LOGGING:
                logger.info(f"🔑 [AUTH DEBUG] Token extracted from {AUTH_HEADER_NAME} header")
            return token
        # For custom headers like X-Access-Token, assume direct token value
        elif AUTH_HEADER_NAME != "Authorization":
            if ENABLE_TOKEN_LOGGING:
                logger.info(f"🔑 [AUTH DEBUG] Token extracted from custom header {AUTH_HEADER_NAME}")
            return header_value
    
    # Fallback: Try standard Authorization header if using custom header
    if AUTH_HEADER_NAME != "Authorization":
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.replace("Bearer ", "")
            if ENABLE_TOKEN_LOGGING:
                logger.info(f"🔑 [AUTH DEBUG] Token extracted from fallback Authorization header")
            return token
    
    # Try X-JWT-Assertion (common in Choreo/API Gateway)
    jwt_assertion = request.headers.get("X-JWT-Assertion")
    if jwt_assertion:
        if ENABLE_TOKEN_LOGGING:
            logger.info(f"🔑 [AUTH DEBUG] Token extracted from X-JWT-Assertion header")
        return jwt_assertion
    
    if ENABLE_TOKEN_LOGGING:
        logger.warning(f"⚠️ [AUTH DEBUG] No token found in any header")
    return None


def log_all_request_headers(request: Request):
    """Log all request headers for debugging purposes"""
    if not ENABLE_TOKEN_LOGGING:
        return
        
    logger.info(f"🌐 [AUTH DEBUG] All Request Headers:")
    for header_name, header_value in request.headers.items():
        # Truncate long values and mask sensitive headers
        if "token" in header_name.lower() or "authorization" in header_name.lower():
            if len(header_value) > 30:
                display_value = f"{header_value[:15]}...{header_value[-10:]}"
            else:
                display_value = header_value
        else:
            display_value = header_value[:100] + "..." if len(header_value) > 100 else header_value
        logger.info(f"  ├─ {header_name}: {display_value}")
    logger.info(f"  └─ Client IP: {request.client.host if request.client else 'N/A'}")


class TokenHandler:
    """
    JWT token handler that supports both JWKS validation and decode-only modes.
    """
    
    @staticmethod
    def validate_and_decode_token(token: str) -> TokenInfo:
        """
        Validate JWT token using JWKS and decode for user context.
        Used when ENABLE_BACKEND_TOKEN_VALIDATION=true.
        
        Args:
            token: JWT token string
            
        Returns:
            TokenInfo with extracted and validated user/agent identity
            
        Raises:
            ValueError: If token cannot be validated or decoded
        """
        try:
            if ENABLE_TOKEN_LOGGING:
                token_preview = f"{token[:20]}...{token[-10:]}" if len(token) > 30 else token
                logger.info(f"🔑 [AUTH DEBUG] Validating JWT token with JWKS: {token_preview}")
            
            # Get signing key from JWKS
            if JWKS_CLIENT:
                try:
                    signing_key = JWKS_CLIENT.get_signing_key_from_jwt(token)
                    key = signing_key.key
                    if ENABLE_TOKEN_LOGGING:
                        logger.info(f"✅ [AUTH DEBUG] Retrieved signing key from JWKS")
                except Exception as e:
                    if ENABLE_TOKEN_LOGGING:
                        logger.error(f"❌ [AUTH DEBUG] Failed to get signing key from JWKS: {e}")
                    # Fallback to static key if available
                    if JWT_SECRET_KEY:
                        key = JWT_SECRET_KEY
                        if ENABLE_TOKEN_LOGGING:
                            logger.info(f"🔄 [AUTH DEBUG] Falling back to static JWT secret key")
                    else:
                        raise ValueError("Unable to get JWT signing key")
            elif JWT_SECRET_KEY:
                key = JWT_SECRET_KEY
                if ENABLE_TOKEN_LOGGING:
                    logger.info(f"🔑 [AUTH DEBUG] Using static JWT secret key")
            else:
                raise ValueError("No JWT validation method configured (JWKS_URL or JWT_SECRET_KEY required)")
            
            # Validate JWT with signature verification
            decode_options = {
                "verify_signature": True,
                "verify_exp": True,
                "verify_iat": True,
                "verify_aud": bool(JWT_AUDIENCE),
                "verify_iss": bool(JWT_ISSUER),
            }
            
            payload = jwt.decode(
                token,
                key=key,
                algorithms=[JWT_ALGORITHM],
                audience=JWT_AUDIENCE,
                issuer=JWT_ISSUER,
                options=decode_options
            )
            
            if ENABLE_TOKEN_LOGGING:
                logger.info(f"✅ [AUTH DEBUG] JWT signature validation successful")
                
        except jwt.ExpiredSignatureError:
            logger.error(f"❌ [AUTH DEBUG] JWT token has expired")
            raise ValueError("Token has expired")
        except jwt.InvalidTokenError as e:
            logger.error(f"❌ [AUTH DEBUG] JWT validation failed: {e}")
            raise ValueError(f"Invalid token: {e}")
        except Exception as e:
            logger.error(f"❌ [AUTH DEBUG] JWT validation error: {e}")
            raise ValueError(f"Token validation failed: {e}")
        
        # Process the validated payload
        return TokenHandler._process_jwt_payload(payload, token)
    
    @staticmethod
    def decode_token(token: str) -> TokenInfo:
        """
        Decode JWT token without signature verification for user context only.
        Used when ENABLE_BACKEND_TOKEN_VALIDATION=false (gateway handles validation).
        
        Args:
            token: JWT token string
            
        Returns:
            TokenInfo with extracted user/agent identity
            
        Raises:
            ValueError: If token cannot be decoded or lacks required claims
        """
        try:
            if ENABLE_TOKEN_LOGGING:
                token_preview = f"{token[:20]}...{token[-10:]}" if len(token) > 30 else token
                logger.info(f"🔑 [AUTH DEBUG] Decoding JWT token (no validation): {token_preview}")
            
            # Decode without verification - only for extracting claims
            payload = jwt.decode(token, options={"verify_signature": False})
            
            if ENABLE_TOKEN_LOGGING:
                logger.info(f"✅ [AUTH DEBUG] JWT decoded successfully (no validation)")
                
        except jwt.DecodeError as e:
            logger.error(f"❌ [AUTH DEBUG] Token decode error: {e}")
            raise ValueError(f"Invalid token format: {e}")
        except Exception as e:
            logger.error(f"❌ [AUTH DEBUG] Token processing error: {e}")
            raise ValueError(f"Token processing failed: {e}")
        
        # Process the decoded payload
        return TokenHandler._process_jwt_payload(payload, token)
    
    @staticmethod
    def _process_jwt_payload(payload: Dict[str, Any], token: str) -> TokenInfo:
        """
        Process JWT payload to extract user/agent information.
        
        Args:
            payload: Decoded JWT payload
            token: Original JWT token string
            
        Returns:
            TokenInfo with extracted user/agent identity
        """
        if ENABLE_TOKEN_LOGGING:
            # Log decoded payload (filtered for sensitive data)
            filtered_payload = {k: v for k, v in payload.items() 
                              if k not in ['signature', 'key', 'secret']}
            logger.info(f"📋 [AUTH DEBUG] JWT payload: {filtered_payload}")
            
            # Log specific claims for debugging
            logger.info(f"📊 [AUTH DEBUG] JWT Claims Analysis:")
            logger.info(f"  ├─ sub (Subject): {payload.get('sub', 'N/A')}")
            logger.info(f"  ├─ aud (Audience): {payload.get('aud', 'N/A')}")  
            logger.info(f"  ├─ iss (Issuer): {payload.get('iss', 'N/A')}")
            logger.info(f"  ├─ exp (Expires): {payload.get('exp', 'N/A')}")
            logger.info(f"  ├─ iat (Issued At): {payload.get('iat', 'N/A')}")
            logger.info(f"  ├─ scope: {payload.get('scope', 'N/A')}")
            logger.info(f"  └─ act (Actor): {payload.get('act', 'N/A')}")
        
        # Default values
        token_type = "user"
        user_id = payload.get("sub")
        agent_id = None
        
        # Check for OBO token pattern (act claim present)
        if "act" in payload:
            token_type = "obo"
            user_id = payload.get("sub")  # Original user
            agent_id = payload.get("act", {}).get("sub")  # Acting agent
            if ENABLE_TOKEN_LOGGING:
                logger.info(f"🤖 [AUTH DEBUG] Detected OBO token - Agent: {agent_id} acting for User: {user_id}")
        else:
            # Check if this might be an agent token (common patterns)
            sub = payload.get("sub", "")
            if any(indicator in sub.lower() for indicator in ["agent", "bot", "service", "system"]):
                token_type = "agent"
                if ENABLE_TOKEN_LOGGING:
                    logger.info(f"🤖 [AUTH DEBUG] Detected Agent token - Agent: {user_id}")
            else:
                if ENABLE_TOKEN_LOGGING:
                    logger.info(f"👤 [AUTH DEBUG] Detected User token - User: {user_id}")
            
        # Fallback user ID extraction from various possible claims
        if not user_id:
            user_id = (
                payload.get("username") or 
                payload.get("preferred_username") or
                payload.get("email") or
                payload.get("upn")
            )
        
        if not user_id:
            logger.error(f"❌ [AUTH DEBUG] Unable to extract user ID from token payload")
            raise ValueError("Unable to extract user ID from token")
            
        if ENABLE_TOKEN_LOGGING:
            logger.info(f"✅ [AUTH DEBUG] Token processed successfully: type={token_type}, user_id={user_id}, agent_id={agent_id}")
        
        # Extract scopes from token
        token_scopes = []
        scope_claim = payload.get("scope", "")
        if isinstance(scope_claim, str):
            token_scopes = scope_claim.split() if scope_claim else []
        elif isinstance(scope_claim, list):
            token_scopes = scope_claim
        
        if ENABLE_TOKEN_LOGGING:
            logger.info(f"🔒 [AUTH DEBUG] Extracted scopes: {token_scopes}")
        
        return TokenInfo(
            token_type=token_type,
            user_id=user_id,
            agent_id=agent_id,
            raw_token=token,
            scopes=token_scopes
        )


def get_token_info_flexible(request: Request) -> Optional[TokenInfo]:
    """
    Extract token information from configurable header.
    Supports both backend validation and gateway-only modes.
    
    Args:
        request: FastAPI request object
        
    Returns:
        TokenInfo if token found and processed, None if no token found
    """
    if ENABLE_TOKEN_LOGGING:
        log_all_request_headers(request)
    
    # Extract token from configured header (even if validation is disabled)
    token = extract_token_from_request(request)
    if not token:
        if ENABLE_TOKEN_LOGGING:
            logger.info(f"⚠️ [AUTH DEBUG] No token found in any header")
        return None
    
    # If backend validation is disabled, still decode for business context
    if not ENABLE_BACKEND_TOKEN_VALIDATION:
        if ENABLE_TOKEN_LOGGING:
            logger.info(f"🚫 [AUTH DEBUG] Backend token validation disabled - decoding JWT for business context only")
        try:
            return TokenHandler.decode_token(token)
        except ValueError as e:
            if ENABLE_TOKEN_LOGGING:
                logger.error(f"❌ [AUTH DEBUG] Token decode error (validation disabled): {e}")
            return None
    
    # Backend validation enabled - full validation with JWKS
    try:
        return TokenHandler.validate_and_decode_token(token)
    except ValueError as e:
        if ENABLE_TOKEN_LOGGING:
            logger.error(f"❌ [AUTH DEBUG] Token validation error: {e}")
        return None


def get_token_info(credentials: HTTPAuthorizationCredentials = Depends(security)) -> TokenInfo:
    """
    Extract token information from Authorization header (legacy method).
    Kept for backward compatibility with existing endpoints.
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token = credentials.credentials
    
    try:
        return TokenHandler.decode_token(token)
    except ValueError as e:
        logger.error(f"Token decode error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unable to process token",
            headers={"WWW-Authenticate": "Bearer"},
        )


def get_token_info_required(request: Request) -> TokenInfo:
    """
    Extract token information with flexible header support.
    Raises HTTPException if token validation is enabled but token is missing/invalid.
    
    Args:
        request: FastAPI request object
        
    Returns:
        TokenInfo object
        
    Raises:
        HTTPException: If validation enabled but token missing/invalid
    """
    if ENABLE_TOKEN_LOGGING:
        log_all_request_headers(request)
    
    # If backend validation is disabled, create a placeholder token info
    if not ENABLE_BACKEND_TOKEN_VALIDATION:
        if ENABLE_TOKEN_LOGGING:
            logger.info(f"🚫 [AUTH DEBUG] Backend validation disabled - creating placeholder token info")
        return TokenInfo(
            token_type="gateway",
            user_id="gateway-user",
            agent_id=None,
            raw_token="",
            scopes=[]  # Gateway handles scope validation
        )
    
    # Extract token from configured header
    token = extract_token_from_request(request)
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Token required in {AUTH_HEADER_NAME} header",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    try:
        return TokenHandler.decode_token(token)
    except ValueError as e:
        logger.error(f"❌ [AUTH DEBUG] Token processing failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unable to process token",
            headers={"WWW-Authenticate": "Bearer"},
        )


def log_request_headers(request: Request, credentials: HTTPAuthorizationCredentials):
    """
    Extract token information from Authorization header.
    No validation performed - only decoding for user context.
    """
    token = credentials.credentials
    
    try:
        return TokenHandler.decode_token(token)
    except ValueError as e:
        logger.error(f"Token decode error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unable to process token",
            headers={"WWW-Authenticate": "Bearer"},
        )


def log_request_headers(request: Request, credentials: HTTPAuthorizationCredentials):
    """Log request headers for debugging"""
    try:
        logger.info(f"🌐 [PIZZA-API] Request Headers Analysis:")
        logger.info(f"  ├─ Authorization: Bearer {credentials.credentials[:20]}...{credentials.credentials[-10:]}")
        
        # Log X-JWT-Assertion header if present (common in Choreo/API Gateway)
        jwt_assertion = request.headers.get("X-JWT-Assertion")
        if jwt_assertion:
            jwt_preview = f"{jwt_assertion[:20]}...{jwt_assertion[-10:]}" if len(jwt_assertion) > 30 else jwt_assertion
            logger.info(f"  ├─ X-JWT-Assertion: {jwt_preview}")
        else:
            logger.info(f"  ├─ X-JWT-Assertion: Not present")
        
        # Log other common auth headers
        for header_name in ["X-Forwarded-For", "X-Real-IP", "User-Agent", "X-Request-ID"]:
            header_value = request.headers.get(header_name)
            if header_value:
                # Truncate long header values
                display_value = header_value[:50] + "..." if len(header_value) > 50 else header_value
                logger.info(f"  ├─ {header_name}: {display_value}")
        
        logger.info(f"  └─ Client IP: {request.client.host if request.client else 'N/A'}")
    except Exception as e:
        logger.error(f"❌ [PIZZA-API] Error logging request headers: {e}")


def validate_token_flexible(
    request: Request,
    security_scopes: SecurityScopes
) -> TokenData:
    """
    Flexible token validation supporting both backend and gateway modes.
    
    In backend validation mode: Validates token and checks scopes
    In gateway mode: Decodes JWT for business context but skips scope validation
    
    Args:
        request: FastAPI request object
        security_scopes: Required scopes for this endpoint
        
    Returns:
        TokenData object
        
    Raises:
        HTTPException: If validation enabled but token missing/invalid/insufficient scopes
    """
    if ENABLE_TOKEN_LOGGING:
        logger.info(f"🔒 [AUTH DEBUG] Validating token for scopes: {security_scopes.scopes}")
        log_all_request_headers(request)
    
    # Extract token from configured header (regardless of validation mode)
    token = extract_token_from_request(request)
    
    # If backend validation is disabled
    if not ENABLE_BACKEND_TOKEN_VALIDATION:
        if token:
            # JWT is available - decode it for business context
            try:
                token_info = TokenHandler.decode_token(token)
                if ENABLE_TOKEN_LOGGING:
                    logger.info(f"🚫 [AUTH DEBUG] Backend validation disabled - using JWT for business context only")
                    logger.info(f"✅ [AUTH DEBUG] Gateway handles scope validation for: {security_scopes.scopes}")
                
                # Return TokenData with real user info but assume gateway validated scopes
                act = Actor(sub=token_info.agent_id)
                return TokenData(
                    sub=token_info.user_id,
                    act=act,
                    scopes=security_scopes.scopes  # Assume gateway validated required scopes
                )
            except ValueError as e:
                if ENABLE_TOKEN_LOGGING:
                    logger.error(f"❌ [AUTH DEBUG] Token decode error (validation disabled): {e}")
                # Fallback to placeholder if JWT decode fails
                pass
        
        # No JWT available or decode failed - create placeholder
        if ENABLE_TOKEN_LOGGING:
            logger.info(f"🚫 [AUTH DEBUG] No JWT available - using placeholder token data")
            logger.info(f"✅ [AUTH DEBUG] Gateway handles scope validation for: {security_scopes.scopes}")
            
        act = Actor(sub=None)
        return TokenData(
            sub="gateway-user",
            act=act,
            scopes=security_scopes.scopes  # Assume gateway validated required scopes
        )
    
    # Backend validation mode - full validation required
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Token required in {AUTH_HEADER_NAME} header",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    try:
        token_info = TokenHandler.validate_and_decode_token(token)
    except ValueError as e:
        logger.error(f"❌ [AUTH DEBUG] Token validation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unable to validate token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Check that the token has ALL the required scopes
    missing_scopes = []
    for scope in security_scopes.scopes:
        if scope not in token_info.scopes:
            missing_scopes.append(scope)
    
    if missing_scopes:
        error_msg = f"Insufficient permissions. Missing scopes: {missing_scopes}, Available: {token_info.scopes}"
        if ENABLE_TOKEN_LOGGING:
            logger.error(f"❌ [AUTH DEBUG] {error_msg}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=error_msg
        )
    
    if ENABLE_TOKEN_LOGGING:
        logger.info(f"✅ [AUTH DEBUG] Token validation successful - all required scopes present")
    
    # Convert to TokenData format
    act = Actor(sub=token_info.agent_id)
    
    return TokenData(
        sub=token_info.user_id,
        act=act,
        scopes=token_info.scopes
    )


def validate_token(
    security_scopes: SecurityScopes,
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> TokenData:
    """
    Legacy token validation using Authorization header only.
    Validates token and checks scopes (original implementation).
    
    For new flexible validation, use validate_token_flexible() instead.
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token_info = get_token_info(credentials)
    
    # Check that the token has ALL the required scopes
    for scope in security_scopes.scopes:
        if scope not in token_info.scopes:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Required scope: {scope}, Available scopes: {token_info.scopes}"
            )
    
    # Convert to TokenData format compatible with hotel API patterns
    act = Actor(sub=token_info.agent_id)
    
    return TokenData(
        sub=token_info.user_id,
        act=act,
        scopes=token_info.scopes
    )


# Backward compatibility function - keep the simple validate_token for endpoints that don't need scopes
def simple_validate_token(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> TokenInfo:
    """
    Simple token validation without scope checking for backward compatibility.
    Uses Authorization header only.
    """
    return get_token_info(credentials)


def simple_validate_token_flexible(request: Request) -> Optional[TokenInfo]:
    """
    Simple token validation with flexible header support.
    Returns None if backend validation is disabled or token not found.
    """
    return get_token_info_flexible(request)