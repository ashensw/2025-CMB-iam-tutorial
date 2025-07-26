"""
Copyright (c) 2025, WSO2 LLC. (http://www.wso2.com). All Rights Reserved.

 This software is the property of WSO2 LLC. and its suppliers, if any.
 Dissemination of any information or reproduction of any material contained
 herein is strictly forbidden, unless permitted by WSO2 in accordance with
 the WSO2 Commercial License available at http://wso2.com/licenses.
 For specific language governing the permissions and limitations under
 this license, please see the license as well as any agreement you've
 entered into with WSO2 governing the purchase of this software and any
"""
import asyncio
import base64
import hashlib
import inspect
import logging
import secrets
import time
import uuid
import urllib3
import warnings
from enum import Enum
from typing import List, Dict, Callable, Awaitable, Literal, get_type_hints, Tuple
from typing import Optional

from authlib.integrations.httpx_client import AsyncOAuth2Client
from cachetools import TTLCache
from pydantic import BaseModel, Field
import requests
import os

from .token_logger import token_logger

logger = logging.getLogger(__name__)

# Disable only unverified HTTPS request warnings when using verify=False
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Configure requests session with proper SSL handling
def create_secure_session():
    """Create a requests session with proper SSL configuration"""
    session = requests.Session()
    # In development, we might need to disable SSL verification for self-signed certs
    # In production, always use proper SSL verification
    if os.getenv("DISABLE_SSL_VERIFICATION", "false").lower() == "true":
        session.verify = False
        logger.warning("⚠️ SSL verification is disabled - only use in development!")
    else:
        session.verify = True
    return session

# Global secure session
secure_session = create_secure_session()

# Enhanced HTTP logging utility for detailed request/response tracing
class HTTPLogger:
    """Utility class for logging HTTP requests and responses at INFO level"""
    
    @staticmethod
    def log_http_request(method: str, url: str, headers: Dict = None, data: Dict = None, correlation_id: str = None):
        """Log outgoing HTTP request details at INFO level"""
        logger.info("🌐" * 5 + " HTTP REQUEST " + "🌐" * 5)
        logger.info(f"📝 METHOD: {method.upper()}")
        logger.info(f"🎯 URL: {url}")
        if correlation_id:
            logger.info(f"🔗 CORRELATION_ID: {correlation_id}")
        logger.info(f"⏰ TIMESTAMP: {time.time()}")
        
        # Log headers (sanitized)
        if headers:
            sanitized_headers = HTTPLogger._sanitize_headers(headers)
            logger.info("📋 HEADERS:")
            for key, value in sanitized_headers.items():
                logger.info(f"   └─ {key}: {value}")
        
        # Log request data (sanitized)
        if data:
            sanitized_data = HTTPLogger._sanitize_data(data)
            logger.info("📦 REQUEST DATA:")
            for key, value in sanitized_data.items():
                logger.info(f"   └─ {key}: {value}")
    
    @staticmethod
    def log_http_response(status_code: int, response_data: Dict = None, correlation_id: str = None, duration_ms: float = None):
        """Log HTTP response details at INFO level"""
        logger.info("📨" * 5 + " HTTP RESPONSE " + "📨" * 5)
        logger.info(f"📊 STATUS_CODE: {status_code}")
        if correlation_id:
            logger.info(f"🔗 CORRELATION_ID: {correlation_id}")
        if duration_ms is not None:
            logger.info(f"⏱️ DURATION: {duration_ms:.2f}ms")
        logger.info(f"⏰ TIMESTAMP: {time.time()}")
        
        # Log response data (sanitized)
        if response_data:
            sanitized_data = HTTPLogger._sanitize_data(response_data)
            logger.info("📦 RESPONSE DATA:")
            for key, value in sanitized_data.items():
                if key in ['access_token', 'id_token', 'refresh_token'] and isinstance(value, str):
                    # Log raw token first, then preview
                    logger.info(f"   └─ {key} (RAW): {value}")
                    preview = f"{value[:20]}...{value[-10:]}" if len(value) > 30 else value
                    logger.info(f"   └─ {key} (PREVIEW): {preview}")
                else:
                    logger.info(f"   └─ {key}: {value}")
    
    @staticmethod
    def _sanitize_headers(headers: Dict) -> Dict:
        """Sanitize headers to hide sensitive information"""
        sensitive_headers = {'authorization', 'cookie', 'x-api-key'}
        sanitized = {}
        for key, value in headers.items():
            if key.lower() in sensitive_headers:
                if isinstance(value, str) and len(value) > 10:
                    sanitized[key] = f"{value[:8]}...{value[-4:]}"
                else:
                    sanitized[key] = "***HIDDEN***"
            else:
                sanitized[key] = value
        return sanitized
    
    @staticmethod
    def _sanitize_data(data: Dict) -> Dict:
        """Sanitize data to hide sensitive information while preserving structure"""
        sensitive_keys = {
            'password', 'client_secret', 'code_verifier', 
            'actor_token', 'refresh_token'
        }
        
        sanitized = {}
        for key, value in data.items():
            if any(sensitive_key in key.lower() for sensitive_key in sensitive_keys):
                if isinstance(value, str) and len(value) > 10:
                    sanitized[key] = f"{value[:4]}...{value[-4:]}"
                else:
                    sanitized[key] = "***HIDDEN***"
            elif key.lower() == 'code' and isinstance(value, str) and len(value) > 20:
                # Special handling for authorization codes
                sanitized[key] = f"{value[:8]}...{value[-4:]}"
            else:
                sanitized[key] = value
        
        return sanitized

http_logger = HTTPLogger()

DEFAULT_TOKEN_STORE_MAX_SIZE = 1000
DEFAULT_TOKEN_STORE_TTL = 3600
DEFAULT_AUTHORIZATION_TIMEOUT = 300  # 5 minute timeout


class OAuthTokenType(str, Enum):
    """OAuth token types supported by the tools"""
    CLIENT_TOKEN = "client_credentials"
    OBO_TOKEN = "authorization_code"
    AGENT_TOKEN = "agent_token"


class OAuthToken(BaseModel):
    """OAuth token information"""
    access_token: str
    token_type: str = "Bearer"
    expires_in: Optional[int] = None
    refresh_token: Optional[str] = None
    scope: Optional[str] = None
    id_token: Optional[str] = None
    expires_at: Optional[float] = None

    def is_expired(self) -> bool:
        if not self.expires_at:
            return True
        return time.time() >= self.expires_at - 60  # Refresh slightly early


class AuthConfig(BaseModel):
    """Context information for tool authorization"""
    scopes: List[str] = Field(default_factory=list)
    token_type: OAuthTokenType = OAuthTokenType.CLIENT_TOKEN
    resource: Optional[str] = None

    class Config:
        frozen = True


class AgentConfig(BaseModel):
    """Configuration for AI agent identity and credentials"""
    agent_name: str
    agent_id: str
    agent_secret: str


class AuthRequestMessage(BaseModel):
    type: Literal["auth_request"] = "auth_request"
    auth_url: str
    state: str
    scopes: List[str]


class TokenManager:
    def __init__(self, maxsize=1000, ttl=3600):
        self.token_store = TTLCache(maxsize=maxsize, ttl=ttl)  # TTL in seconds

    def add_token(self, config: AuthConfig, token: OAuthToken):
        key = (frozenset(config.scopes), config.token_type, config.resource)
        self.token_store[key] = token

    def get_token(self, config: AuthConfig) -> Optional[OAuthToken]:
        key = (frozenset(config.scopes), config.token_type, config.resource)
        token = self.token_store.get(key)

        # clean the expired tokens
        if token and token.is_expired():
            _ = self.token_store.pop(key)

        return token


# Global store for pending authorizations to handle reconnections
_pending_auths: Dict[str, Tuple[List[str], asyncio.Future, str]] = {}


class PizzaAuthManager:
    """Enhanced authentication manager for Pizza Agent aligned with IETF OAuth 2.0 AI Agent draft"""
    
    def __init__(
            self,
            idp_base_url: str,
            client_id: str,
            client_secret: str,
            redirect_uri: Optional[str] = None,
            message_handler: Optional[Callable[[AuthRequestMessage], Awaitable[None]]] = None,
            scopes: Optional[List[str]] = None,
            agent_config: Optional[AgentConfig] = None,
            *,
            token_store_maxsize: int = DEFAULT_TOKEN_STORE_MAX_SIZE,
            token_store_ttl: int = DEFAULT_TOKEN_STORE_TTL,
            authorization_timeout: int = DEFAULT_AUTHORIZATION_TIMEOUT
    ):
        # Basic OAuth config
        if not idp_base_url.endswith("/"):
            idp_base_url = idp_base_url.rstrip("/")
        self.token_endpoint = f"{idp_base_url}/oauth2/token"
        self.authorize_endpoint = f"{idp_base_url}/oauth2/authorize"
        self.authn_url = f"{idp_base_url}/oauth2/authn"
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.scopes = scopes or []
        self.authorization_timeout = authorization_timeout
        
        # Agent configuration for IETF draft compliance
        self.agent_config = agent_config
        
        # Initialize agent token if agent config provided
        self.agent_token = None
        if self.agent_config:
            try:
                self.agent_token = self.authenticate_agent_with_basic_auth()
                logger.info("Pizza Agent authentication successful")
            except Exception as e:
                logger.warning(f"Pizza Agent authentication failed: {e}")
                # Continue without agent token - it will be attempted later if needed
        
        # Pending authorization requests with resource support
        self._pending_auths: Dict[str, Tuple[List[str], str, asyncio.Future]] = {}

        # Optional message handler for WebSocket communication
        self._message_handler = message_handler

        # Token manager with configurable eviction
        self._token_manager: TokenManager = TokenManager(
            maxsize=token_store_maxsize,
            ttl=token_store_ttl
        )

        self._validate()

    def _validate(self):
        self._validate_message_handler()

    def _validate_message_handler(self):
        message_handler = self._message_handler
        if not message_handler:
            return
        if not callable(message_handler):
            raise TypeError("message_handler must be callable")
        if not inspect.iscoroutinefunction(message_handler):
            raise TypeError("message_handler must be an async function")

        signature = inspect.signature(message_handler)
        params = list(signature.parameters.values())

        if len(params) != 1:
            raise TypeError("message_handler must accept exactly one parameter")

        param_type = get_type_hints(message_handler).get(params[0].name)
        if param_type != AuthRequestMessage:
            raise TypeError(f"message_handler parameter must be of type AuthRequestMessage, not {param_type}")

    @staticmethod
    def _create_state() -> str:
        return secrets.token_urlsafe(16)
    
    @staticmethod
    def _generate_pkce_pair() -> Tuple[str, str]:
        """Generate PKCE code verifier and challenge according to RFC 7636"""
        # Generate code verifier (43-128 characters, URL-safe without padding)
        code_verifier = base64.urlsafe_b64encode(secrets.token_bytes(32)).decode('utf-8').rstrip('=')
        
        # Generate code challenge using SHA256
        code_challenge = base64.urlsafe_b64encode(
            hashlib.sha256(code_verifier.encode('utf-8')).digest()
        ).decode('utf-8').rstrip('=')
        
        return code_verifier, code_challenge

    def get_message_handler(self) -> Callable[[AuthRequestMessage], Awaitable[None]]:
        return self._message_handler

    async def _refresh_oauth_token(self, refresh_token: str, scopes: List[str]) -> Optional[OAuthToken]:
        """Refresh OAuth token"""
        if not refresh_token:
            return None

        client = AsyncOAuth2Client(
            client_id=self.client_id,
            client_secret=self.client_secret,
            redirect_uri=self.redirect_uri,
            scope=scopes,
        )

        try:
            token = await client.refresh_token(self.token_endpoint, refresh_token)
        except Exception as e:
            logger.error(f"Failed to refresh token: {e}")
            raise

        return OAuthToken(**token)

    async def _fetch_oauth_token(self, config: AuthConfig, code: Optional[str] = None) -> OAuthToken:
        """Fetch OAuth token based on the token type (Client or OBO)"""
        fetch_start_time = time.time()
        correlation_id = str(uuid.uuid4())[:8]
        
        client = AsyncOAuth2Client(
            client_id=self.client_id,
            client_secret=self.client_secret,
            redirect_uri=self.redirect_uri,
            scope=config.scopes,
        )

        try:
            if config.token_type == OAuthTokenType.OBO_TOKEN:
                if not code:
                    token_logger.log_token_error(
                        "MISSING_AUTHORIZATION_CODE",
                        "'code' is required for OBO token",
                        {"token_type": config.token_type.value, "scopes": config.scopes}
                    )
                    raise ValueError("'code' is required for OBO token")
                
                # Include actor_token for IETF draft compliance
                token_params = {
                    "url": self.token_endpoint,
                    "code": code,
                    "grant_type": OAuthTokenType.OBO_TOKEN
                }
                
                # Add actor_token if agent is configured (IETF draft requirement)
                if self.agent_token:
                    token_params["actor_token"] = self.agent_token["access_token"]
                
                # Log detailed HTTP request
                http_logger.log_http_request(
                    method="POST",
                    url=self.token_endpoint,
                    data=token_params,
                    correlation_id=correlation_id
                )
                
                # Log request
                token_logger.log_token_request(
                    token_type="OBO_TOKEN_DIRECT",
                    endpoint=self.token_endpoint,
                    request_data=token_params,
                    scopes=config.scopes,
                    resource=config.resource,
                    agent_info={
                        "agent_delegation": self.agent_token is not None,
                        "agent_id": self.agent_config.agent_id if self.agent_config else None
                    }
                )
                
                request_start = time.time()
                token = await client.fetch_token(**token_params)
                request_duration = (time.time() - request_start) * 1000
                
                # Log detailed HTTP response
                http_logger.log_http_response(
                    status_code=200,  # authlib handles errors, so if we get here, it's 200
                    response_data=token,
                    correlation_id=correlation_id,
                    duration_ms=request_duration
                )
                
                # Log response
                token_logger.log_token_response(
                    token_type="OBO_TOKEN_DIRECT",
                    token_response=token,
                    decode_token=True
                )
                
            elif config.token_type == OAuthTokenType.CLIENT_TOKEN:
                request_data = {"grant_type": "client_credentials", "scope": " ".join(config.scopes)}
                
                # Log detailed HTTP request
                http_logger.log_http_request(
                    method="POST",
                    url=self.token_endpoint,
                    data=request_data,
                    correlation_id=correlation_id
                )
                
                # Log request
                token_logger.log_token_request(
                    token_type="CLIENT_CREDENTIALS",
                    endpoint=self.token_endpoint,
                    request_data=request_data,
                    scopes=config.scopes,
                    resource=config.resource
                )
                
                request_start = time.time()
                token = await client.fetch_token(url=self.token_endpoint)
                request_duration = (time.time() - request_start) * 1000
                
                # Log detailed HTTP response
                http_logger.log_http_response(
                    status_code=200,  # authlib handles errors, so if we get here, it's 200
                    response_data=token,
                    correlation_id=correlation_id,
                    duration_ms=request_duration
                )
                
                # Log response
                token_logger.log_token_response(
                    token_type="CLIENT_CREDENTIALS",
                    token_response=token,
                    decode_token=True
                )
                
            elif config.token_type == OAuthTokenType.AGENT_TOKEN:
                # Agent token is handled by authenticate_agent_with_basic_auth
                token = self.authenticate_agent_with_basic_auth(config)
                if not token:
                    token_logger.log_token_error(
                        "AGENT_TOKEN_FAILED",
                        "Failed to obtain agent token",
                        {"token_type": config.token_type.value, "scopes": config.scopes}
                    )
                    raise ValueError("Failed to obtain agent token")
            else:
                token_logger.log_token_error(
                    "UNSUPPORTED_TOKEN_TYPE",
                    f"Unsupported token type: {config.token_type}",
                    {"token_type": config.token_type.value}
                )
                raise ValueError(f"Unsupported token type: {config.token_type}")
                
        except ValueError:
            # Re-raise ValueError as it's already handled above
            raise
        except Exception as e:
            token_logger.log_token_error(
                "TOKEN_FETCH_ERROR",
                f"Failed to fetch {config.token_type} token: {str(e)}",
                {
                    "token_type": config.token_type.value,
                    "scopes": config.scopes,
                    "resource": config.resource,
                    "error_type": type(e).__name__,
                    "correlation_id": correlation_id
                }
            )
            raise

        # Log successful completion summary
        fetch_duration = time.time() - fetch_start_time
        token_logger.log_flow_summary(
            flow_type=f"{config.token_type.value}_TOKEN_FETCH",
            success=True,
            total_steps=1,
            duration_seconds=fetch_duration
        )

        return OAuthToken(**token)

    async def _fetch_obo_token(self, config: AuthConfig) -> Optional["OAuthToken"]:
        """
        Fetches the OBO token for the given scopes.
        Requests user authorization and waits for a token asynchronously.
        """
        if not self._message_handler:
            logger.error(f"[Authorization Error] No message handler registered.")
            return None

        state = self._create_state()
        code_verifier, code_challenge = self._generate_pkce_pair()

        # Create a future to await authorization completion
        future = asyncio.Future()
        _pending_auths[state] = config.scopes, config.resource, future, code_verifier

        logger.info(f"🔐 AUTHORIZATION REQUEST: User consent required")
        logger.info(f"   └─ State: {state}")
        logger.info(f"   └─ Scopes: {config.scopes}")
        logger.info(f"   └─ Resource: {config.resource}")
        logger.info(f"   └─ Agent delegation: {self.agent_config.agent_id if self.agent_config else 'None'}")

        # Construct authorization URL with IETF draft parameters
        scope = " ".join(config.scopes)
        params = [
            f"client_id={self.client_id}",
            "response_type=code",
            f"scope={scope}",
            f"redirect_uri={self.redirect_uri}",
            f"state={state}",
            f"code_challenge={code_challenge}",
            f"code_challenge_method=S256"
        ]
        
        # Add requested_actor parameter if agent is configured (IETF draft requirement)
        if self.agent_config:
            params.append(f"requested_actor={self.agent_config.agent_id}")
            
        # Add resource parameter if specified
        if config.resource:
            params.append(f"resource={config.resource}")
            
        auth_url = f"{self.authorize_endpoint}?" + "&".join(params)
        logger.info(f"   └─ Authorization URL generated and sent to client")

        # Notify client via handler (WebSocket message)
        await self._message_handler(
            AuthRequestMessage(
                auth_url=auth_url,
                state=state,
                scopes=config.scopes)
        )

        # Wait for authorization to complete (with timeout)
        try:
            token = await asyncio.wait_for(future, timeout=self.authorization_timeout)
            logger.info(f"✅ AUTHORIZATION RESPONSE: User consent completed for state {state}")
            return token
        except asyncio.TimeoutError:
            logger.warning(f"⏰ AUTHORIZATION TIMEOUT: User consent timed out for state {state}")
            if state in _pending_auths:
                _, future, _ = _pending_auths.pop(state)
                if not future.done():
                    future.cancel()
            return None

    async def get_oauth_token(self, config: AuthConfig) -> OAuthToken:
        """
        Fetches the OAuth token based on the token type (Client or OBO) and the scope
        """
        # Check if a valid token exists already
        token = self._token_manager.get_token(config)

        # If a token exists, check if it is expired
        if token and token.is_expired():
            logger.debug("Token expired. Attempting to refresh %s for the scopes %s", 
                        config.token_type.name, config.scopes)
            token = await self._refresh_oauth_token(token.refresh_token, config.scopes)

        # If token is available then return
        if token:
            return token

        logger.debug("Attempting to fetch %s for the scopes %s", config.token_type.name, config.scopes)
        if config.token_type == OAuthTokenType.OBO_TOKEN:
            token = await self._fetch_obo_token(config)
        elif config.token_type == OAuthTokenType.CLIENT_TOKEN:
            token = await self._fetch_oauth_token(config)
        else:
            raise ValueError(f"Unsupported token type: {config.token_type}")

        # Cache the token in token manager
        if token:
            self._token_manager.add_token(config, token)
        return token

    async def process_callback(self, state: str, code: str) -> OAuthToken:
        """Process OAuth callback with authorization code, PKCE, and agent delegation"""
        callback_start_time = time.time()
        correlation_id = str(uuid.uuid4())[:8]
        
        if state not in _pending_auths:
            token_logger.log_token_error(
                "CALLBACK_STATE_ERROR",
                f"No pending authorization for state: {state}",
                {"state": state, "pending_states": list(_pending_auths.keys())}
            )
            raise ValueError(f"Invalid state or no pending authorization.")

        scopes, resource, future, code_verifier = _pending_auths.pop(state)

        if future.done():
            token_logger.log_token_error(
                "CALLBACK_ALREADY_COMPLETED",
                f"Authorization already completed for state: {state}",
                {"state": state}
            )
            raise ValueError(f"Authorization already completed.")

        # Log OBO flow initiation
        agent_token_preview = None
        if self.agent_token:
            access_token = self.agent_token.get("access_token", "")
            agent_token_preview = f"{access_token[:20]}...{access_token[-10:]}" if len(access_token) > 30 else access_token

        token_logger.log_obo_flow(
            user_token_preview=f"{code[:8]}...{code[-4:]}",
            agent_token_preview=agent_token_preview,
            obo_token=None,
            step="CALLBACK_PROCESSING_START"
        )

        try:
            # Use authlib client with PKCE support
            client = AsyncOAuth2Client(
                client_id=self.client_id,
                client_secret=self.client_secret,
                redirect_uri=self.redirect_uri,
                scope=scopes,
                code_challenge_method="S256"
            )

            token_params = {
                "url": self.token_endpoint,
                "code": code,
                "code_verifier": code_verifier,
                "grant_type": "authorization_code"
            }
            
            # Add actor_token for IETF draft compliance
            if self.agent_token:
                token_params["actor_token"] = self.agent_token["access_token"]
            
            # Log detailed HTTP request
            http_logger.log_http_request(
                method="POST",
                url=self.token_endpoint,
                data=token_params,
                correlation_id=correlation_id
            )
            
            # Log the token exchange request
            token_logger.log_token_request(
                token_type="OBO_TOKEN",
                endpoint=self.token_endpoint,
                request_data=token_params,
                scopes=scopes,
                resource=resource,
                agent_info={
                    "agent_delegation": self.agent_token is not None,
                    "agent_id": self.agent_config.agent_id if self.agent_config else None
                }
            )
            
            request_start = time.time()
            token = await client.fetch_token(**token_params)
            request_duration = (time.time() - request_start) * 1000
            oauth_token = OAuthToken(**token)
            
            # Log detailed HTTP response
            http_logger.log_http_response(
                status_code=200,  # authlib handles errors, so if we get here, it's 200
                response_data=token,
                correlation_id=correlation_id,
                duration_ms=request_duration
            )
            
            # Log comprehensive OBO token response
            token_logger.log_token_response(
                token_type="OBO_TOKEN",
                token_response=token,
                decode_token=True
            )
            
            # Log detailed OBO flow completion
            token_logger.log_obo_flow(
                user_token_preview=f"{code[:8]}...{code[-4:]}",
                agent_token_preview=agent_token_preview,
                obo_token=token,
                step="TOKEN_EXCHANGE_SUCCESS"
            )
            
            # Extract user and agent info for flow summary
            user_id = None
            agent_id = None
            try:
                import jwt
                access_token = oauth_token.access_token
                payload = jwt.decode(access_token, options={"verify_signature": False})
                user_id = payload.get("sub")
                if "act" in payload:
                    agent_id = payload.get("act", {}).get("sub")
            except:
                pass  # Continue without decoded info
            
            # Log flow summary
            callback_duration = time.time() - callback_start_time
            token_logger.log_flow_summary(
                flow_type="OBO_TOKEN_EXCHANGE",
                user_id=user_id,
                agent_id=agent_id,
                success=True,
                total_steps=1,  # Just the token exchange step
                duration_seconds=callback_duration
            )
            
            future.set_result(oauth_token)
            return oauth_token
            
        except Exception as e:
            # Log comprehensive error details
            token_logger.log_token_error(
                "OBO_TOKEN_EXCHANGE_ERROR",
                f"Failed to exchange code for OBO token: {str(e)}",
                {
                    "state": state,
                    "scopes": scopes,
                    "resource": resource,
                    "agent_delegation": self.agent_token is not None,
                    "error_type": type(e).__name__,
                    "correlation_id": correlation_id
                }
            )
            
            token_logger.log_obo_flow(
                user_token_preview=f"{code[:8]}...{code[-4:]}",
                agent_token_preview=agent_token_preview,
                obo_token=None,
                step="TOKEN_EXCHANGE_FAILED",
                success=False
            )
            
            future.set_exception(e)
            raise

    def authenticate_agent_with_basic_auth(
        self,
        auth_config: Optional[AuthConfig] = None
    ):
        """
        Perform OAuth2 authentication flow for Pizza Agent using basic auth.
        Aligned with IETF draft requirements for agent identity.

        Args:
            auth_config (Optional[AuthConfig]): Auth configuration for scopes

        Returns:
            Optional[dict]: The agent token response if successful, otherwise None.
        """
        flow_start_time = time.time()
        
        if not self.agent_config:
            token_logger.log_token_error(
                "CONFIGURATION_ERROR",
                "Agent configuration required for agent authentication",
                {"agent_config": "Missing"}
            )
            return None
        
        scopes = "openid profile pizza:agent"
        if auth_config is not None:
            scopes = " ".join(auth_config.scopes)

        # Use the actual client ID from environment or fallback to your org's client ID
        AGENT_DEFAULT_APP_CLIENT_ID = os.getenv("AGENT_APP_CLIENT_ID", self.client_id)

        # Log initial request
        token_logger.log_token_request(
            token_type="AGENT_TOKEN",
            endpoint=self.authorize_endpoint,
            request_data={
                "client_id": AGENT_DEFAULT_APP_CLIENT_ID,
                "response_type": "code",
                "redirect_uri": self.redirect_uri,
                "scope": scopes,
                "response_mode": "direct",
                "resource": "pizza_api"
            },
            scopes=scopes.split(),
            resource="pizza_api",
            agent_info={
                "agent_name": self.agent_config.agent_name,
                "agent_id": self.agent_config.agent_id
            }
        )

        code_verifier = self.generate_code_verifier()
        code_challenge = self.generate_code_challenge(code_verifier)

        try:
            correlation_id = str(uuid.uuid4())[:8]
            
            # Step 1: Initialize Authorization
            authorize_data = {
                "client_id": AGENT_DEFAULT_APP_CLIENT_ID,
                "response_type": "code",
                "redirect_uri": self.redirect_uri,
                "state": "pizza_agent_auth",
                "scope": scopes,
                "response_mode": "direct",
                "code_challenge": code_challenge,
                "code_challenge_method": "S256",
                "resource": "pizza_api"
            }
            
            # Log detailed HTTP request for Step 1
            http_logger.log_http_request(
                method="POST",
                url=self.authorize_endpoint,
                data=authorize_data,
                correlation_id=f"{correlation_id}-S1"
            )
            
            token_logger.log_agent_authentication_flow(
                agent_name=self.agent_config.agent_name,
                agent_id=self.agent_config.agent_id,
                flow_step="STEP_1_AUTHORIZE",
                flow_data=authorize_data
            )
            
            step1_start = time.time()
            resp = secure_session.post(self.authorize_endpoint, data=authorize_data)
            step1_duration = (time.time() - step1_start) * 1000
            resp.raise_for_status()
            resp_json = resp.json()
            
            # Log detailed HTTP response for Step 1
            http_logger.log_http_response(
                status_code=resp.status_code,
                response_data=resp_json,
                correlation_id=f"{correlation_id}-S1",
                duration_ms=step1_duration
            )
            
            flow_id = resp_json.get("flowId")
            idf_authenticator_id = resp_json.get("nextStep", {}).get("authenticators", [{}])[0].get("authenticatorId")
            
            if not flow_id:
                token_logger.log_token_error(
                    "AUTHORIZATION_ERROR",
                    "Failed to get flow ID from authorization endpoint",
                    {"response": resp_json, "correlation_id": f"{correlation_id}-S1"}
                )
                return None

            # Step 2: Authenticate with identifier
            idf_body = {
                "flowId": flow_id,
                "selectedAuthenticator": {
                    "authenticatorId": idf_authenticator_id,
                    "params": {
                        "username": self.agent_config.agent_name
                    }
                }
            }
            
            # Log detailed HTTP request for Step 2
            http_logger.log_http_request(
                method="POST",
                url=self.authn_url,
                data=idf_body,
                correlation_id=f"{correlation_id}-S2"
            )
            
            token_logger.log_agent_authentication_flow(
                agent_name=self.agent_config.agent_name,
                agent_id=self.agent_config.agent_id,
                flow_step="STEP_2_IDENTIFIER",
                flow_data={"flow_id": flow_id, "username": self.agent_config.agent_name}
            )
            
            step2_start = time.time()
            resp = secure_session.post(self.authn_url, json=idf_body)
            step2_duration = (time.time() - step2_start) * 1000
            resp.raise_for_status()
            resp_json = resp.json()

            # Log detailed HTTP response for Step 2
            http_logger.log_http_response(
                status_code=resp.status_code,
                response_data=resp_json,
                correlation_id=f"{correlation_id}-S2",
                duration_ms=step2_duration
            )

            password_authenticator_id = resp_json.get("nextStep", {}).get("authenticators", [{}])[0].get("authenticatorId")

            # Step 3: Authenticate with password (basic auth)
            password_body = {
                "flowId": flow_id,
                "selectedAuthenticator": {
                    "authenticatorId": password_authenticator_id,
                    "params": {
                        "password": self.agent_config.agent_secret
                    }
                }
            }
            
            # Log detailed HTTP request for Step 3
            http_logger.log_http_request(
                method="POST",
                url=self.authn_url,
                data=password_body,
                correlation_id=f"{correlation_id}-S3"
            )
            
            token_logger.log_agent_authentication_flow(
                agent_name=self.agent_config.agent_name,
                agent_id=self.agent_config.agent_id,
                flow_step="STEP_3_PASSWORD",
                flow_data={"flow_id": flow_id, "password": "***HIDDEN***"}
            )
            
            step3_start = time.time()
            resp = secure_session.post(self.authn_url, json=password_body)
            step3_duration = (time.time() - step3_start) * 1000
            resp.raise_for_status()
            resp_json = resp.json()

            # Log detailed HTTP response for Step 3
            http_logger.log_http_response(
                status_code=resp.status_code,
                response_data=resp_json,
                correlation_id=f"{correlation_id}-S3",
                duration_ms=step3_duration
            )

            code = resp_json.get("authData", {}).get("code")
            if not code:
                token_logger.log_token_error(
                    "AUTHENTICATION_ERROR",
                    "Failed to get authorization code from authentication",
                    {"response": resp_json, "correlation_id": f"{correlation_id}-S3"}
                )
                return None

            # Step 4: Exchange code for token
            token_data = {
                "grant_type": "authorization_code",
                "client_id": AGENT_DEFAULT_APP_CLIENT_ID,
                "code": code,
                "code_verifier": code_verifier,
                "redirect_uri": self.redirect_uri,
                "scope": scopes,
                "resource": "pizza_api"
            }
            
            # Log detailed HTTP request for Step 4
            http_logger.log_http_request(
                method="POST",
                url=self.token_endpoint,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                data=token_data,
                correlation_id=f"{correlation_id}-S4"
            )
            
            token_logger.log_agent_authentication_flow(
                agent_name=self.agent_config.agent_name,
                agent_id=self.agent_config.agent_id,
                flow_step="STEP_4_TOKEN_EXCHANGE",
                flow_data={"code": f"{code[:8]}...{code[-4:]}", "resource": "pizza_api"}
            )
            
            headers = {"Content-Type": "application/x-www-form-urlencoded"}
            step4_start = time.time()
            resp = secure_session.post(self.token_endpoint, data=token_data, headers=headers)
            step4_duration = (time.time() - step4_start) * 1000
            resp.raise_for_status()
            resp_json = resp.json()
            
            # Log detailed HTTP response for Step 4
            http_logger.log_http_response(
                status_code=resp.status_code,
                response_data=resp_json,
                correlation_id=f"{correlation_id}-S4",
                duration_ms=step4_duration
            )
            
            # Log comprehensive token response
            token_logger.log_token_response(
                token_type="AGENT_TOKEN",
                token_response=resp_json,
                decode_token=True
            )
            
            # Log flow summary
            flow_duration = time.time() - flow_start_time
            token_logger.log_flow_summary(
                flow_type="AGENT_AUTHENTICATION",
                agent_id=self.agent_config.agent_id,
                success=True,
                total_steps=4,
                duration_seconds=flow_duration
            )
            
            return resp_json
            
        except requests.RequestException as e:
            token_logger.log_token_error(
                "HTTP_REQUEST_ERROR",
                f"HTTP request failed during agent authentication: {str(e)}",
                {"agent_name": self.agent_config.agent_name, "error_type": type(e).__name__}
            )
            return None
        except Exception as e:
            token_logger.log_token_error(
                "AGENT_AUTHENTICATION_ERROR",
                f"Unexpected error during agent authentication: {str(e)}",
                {"agent_name": self.agent_config.agent_name, "error_type": type(e).__name__}
            )
            return None

    def generate_code_verifier(self, length: int = 64) -> str:
        """Generate PKCE code verifier"""
        return secrets.token_urlsafe(length)[:length]

    def generate_code_challenge(self, code_verifier: str) -> str:
        """Generate PKCE code challenge using SHA256"""
        sha256_digest = hashlib.sha256(code_verifier.encode('utf-8')).digest()
        code_challenge = base64.urlsafe_b64encode(sha256_digest).rstrip(b'=').decode('utf-8')
        return code_challenge


class AuthSchema:
    """Authentication schema for validating auth configurations"""
    
    def __init__(self, manager: PizzaAuthManager, config: AuthConfig):
        self.manager = manager
        self.config = config
        self._validate_manager()

    def _validate_manager(self):
        if self.config.token_type is OAuthTokenType.OBO_TOKEN:
            if not self.manager.redirect_uri:
                raise ValueError(
                    "Redirect URI is required for authorization code grant type."
                )
            if not self.manager.get_message_handler():
                raise ValueError(
                    "Message handler is required for authorization code grant type."
                )


class SecureFunctionTool:
    """Enhanced secure function tool for Pizza Agent following Hotel Agent patterns"""
    
    def __init__(self, tool_instance, auth_manager: PizzaAuthManager, auth_config: AuthConfig):
        self.tool = tool_instance
        self.auth_manager = auth_manager
        self.auth_config = auth_config
        self.auth_schema = AuthSchema(auth_manager, auth_config)
        
    async def execute(self, *args, **kwargs):
        """Execute tool with automatic authentication handling"""
        try:
            # Get the required token
            token = await self.auth_manager.get_oauth_token(self.auth_config)
            if not token:
                raise Exception("Failed to obtain required authentication token")
            
            # Execute the tool with the token
            return await self._execute_with_token(token, *args, **kwargs)
            
        except Exception as e:
            logger.error(f"SecureFunctionTool execution failed: {e}")
            raise
    
    async def _execute_with_token(self, token: OAuthToken, *args, **kwargs):
        """Execute the underlying tool with the obtained token"""
        # Add token to kwargs if the tool expects it
        kwargs['token'] = token.access_token
        
        # Execute the tool (handle both sync and async tools)
        if hasattr(self.tool, '_run'):
            if asyncio.iscoroutinefunction(self.tool._run):
                return await self.tool._run(*args, **kwargs)
            else:
                return self.tool._run(*args, **kwargs)
        elif hasattr(self.tool, 'run'):
            if asyncio.iscoroutinefunction(self.tool.run):
                return await self.tool.run(*args, **kwargs)
            else:
                return self.tool.run(*args, **kwargs)
        else:
            raise Exception("Tool does not have a recognized execution method")
    
    def __getattr__(self, name):
        """Delegate attribute access to wrapped tool"""
        return getattr(self.tool, name)