"""
FastAPI dependency injection for authentication and database sessions
"""
import jwt
import logging
from fastapi import Depends, HTTPException, status, Security, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials, SecurityScopes
from sqlalchemy.orm import Session
from typing import Optional
from .database import SessionLocal
from .schemas import TokenInfo, TokenData, Actor

logger = logging.getLogger(__name__)
security = HTTPBearer()


def get_db():
    """Database session dependency"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class TokenHandler:
    """
    JWT token handler that only decodes tokens to extract user identity.
    No validation is performed - that's handled by Choreo.
    """
    
    @staticmethod
    def decode_token(token: str) -> TokenInfo:
        """
        Decode JWT token to extract user identity information.
        No signature verification or validation - only decoding for user context.
        
        Args:
            token: JWT token string
            
        Returns:
            TokenInfo with extracted user/agent identity
            
        Raises:
            ValueError: If token cannot be decoded or lacks required claims
        """
        try:
            # Log raw token (truncated for security)
            token_preview = f"{token[:20]}...{token[-10:]}" if len(token) > 30 else token
            logger.info(f"🔑 [PIZZA-API] Received JWT token: {token_preview}")
            
            # Decode without verification - only for extracting claims
            payload = jwt.decode(token, options={"verify_signature": False})
            
            # Log decoded payload (filtered for sensitive data)
            filtered_payload = {k: v for k, v in payload.items() 
                              if k not in ['signature', 'key', 'secret']}
            logger.info(f"📋 [PIZZA-API] Decoded JWT payload: {filtered_payload}")
            
            # Default values
            token_type = "user"
            user_id = payload.get("sub")
            agent_id = None
            
            # Check for OBO token pattern (act claim present)
            if "act" in payload:
                token_type = "obo"
                user_id = payload.get("sub")  # Original user
                agent_id = payload.get("act", {}).get("sub")  # Acting agent
                logger.info(f"🤖 [PIZZA-API] Detected OBO token - Agent: {agent_id} acting for User: {user_id}")
            else:
                logger.info(f"👤 [PIZZA-API] Detected User token - User: {user_id}")
                
            # Fallback user ID extraction from various possible claims
            if not user_id:
                user_id = (
                    payload.get("username") or 
                    payload.get("preferred_username") or
                    payload.get("email") or
                    payload.get("upn")
                )
            
            if not user_id:
                logger.error(f"❌ [PIZZA-API] Unable to extract user ID from token payload: {filtered_payload}")
                raise ValueError("Unable to extract user ID from token")
                
            logger.info(f"✅ [PIZZA-API] Token processed successfully: type={token_type}, user_id={user_id}, agent_id={agent_id}")
            
            # Extract scopes from token
            token_scopes = []
            scope_claim = payload.get("scope", "")
            if isinstance(scope_claim, str):
                token_scopes = scope_claim.split() if scope_claim else []
            elif isinstance(scope_claim, list):
                token_scopes = scope_claim
            
            return TokenInfo(
                token_type=token_type,
                user_id=user_id,
                agent_id=agent_id,
                raw_token=token,
                scopes=token_scopes
            )
            
        except jwt.DecodeError as e:
            logger.error(f"❌ [PIZZA-API] Token decode error: {e}")
            raise ValueError(f"Invalid token format: {e}")
        except Exception as e:
            logger.error(f"❌ [PIZZA-API] Token processing error: {e}")
            raise ValueError(f"Token processing failed: {e}")


def get_token_info(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    request: Request = None
) -> TokenInfo:
    """
    Extract token information from Authorization header.
    No validation performed - only decoding for user context.
    """
    # Log all relevant headers for debugging
    if request:
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


def validate_token(
    security_scopes: SecurityScopes,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    request: Request = Depends()
) -> TokenData:
    """
    Validate token and check scopes similar to hotel API pattern.
    Decodes token (no signature verification) and validates required scopes.
    """
    token_info = get_token_info(credentials, request)
    
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
    credentials: HTTPAuthorizationCredentials = Depends(security),
    request: Request = Depends()
) -> TokenInfo:
    """
    Simple token validation without scope checking for backward compatibility.
    """
    return get_token_info(credentials, request)