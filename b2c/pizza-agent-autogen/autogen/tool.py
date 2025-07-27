"""
 Copyright (c) 2025, WSO2 LLC. (http://www.wso2.com). All Rights Reserved.

  This software is the property of WSO2 LLC. and its suppliers, if any.
  Dissemination of any information or reproduction of any material contained
  herein is strictly forbidden, unless permitted by WSO2 in accordance with
  the WSO2 Commercial License available at http://wso2.com/licenses.
  For specific language governing the permissions and limitations under
  this license, please see the license as well as any agreement you’ve
  entered into with WSO2 governing the purchase of this software and any
"""
import functools
import inspect
import logging
from collections import OrderedDict
from typing import Any, Callable, Sequence, Optional, get_origin, get_args, Union

from autogen_core import CancellationToken
from autogen_core.code_executor import Import
from autogen_core.tools import FunctionTool
from pydantic import BaseModel

from sdk.auth import OAuthToken, AuthorizationRequiredException, AuthSchema

logger = logging.getLogger(__name__)

TOKEN_FIELD = "token"


class SecureFunctionTool(FunctionTool):
    """Extension of FunctionTool that enforces permissions before execution"""

    def __init__(
            self,
            func: Callable[..., Any],
            description: str,
            name: Optional[str] = None,
            auth: Optional[AuthSchema] = None,
            global_imports: Sequence[Import] = [],
            strict: bool = False,
    ):
        # Store the auth context
        self.auth = auth

        # Get the original signature
        signature = inspect.signature(func)
        params = OrderedDict(signature.parameters)

        # Remove 'token' parameter from the function signature
        token_field = params.pop(TOKEN_FIELD, None)
        
        # Check if token parameter exists and has correct type
        valid_token_type = False
        if token_field is not None:
            annotation = token_field.annotation
            # Check for direct OAuthToken type
            if annotation is OAuthToken:
                valid_token_type = True
            # Check for Optional[OAuthToken] type (Union[OAuthToken, None])
            elif get_origin(annotation) is Union and OAuthToken in get_args(annotation):
                valid_token_type = True
        
        if token_field is None or not valid_token_type:
            available = ", ".join(f"{p.name}: {p.annotation}" for p in params.values())
            raise Exception(
                f"Expected a parameter named '{TOKEN_FIELD}' with type 'OAuthToken' or 'Optional[OAuthToken]' in tool arguments, "
                f"but got: {available or 'no parameters'}.\n"
                f"Ensure your function signature includes '{TOKEN_FIELD}: OAuthToken' or '{TOKEN_FIELD}: Optional[OAuthToken]'."
            )

        new_signature = signature.replace(parameters=params.values())

        # Create a new function with the modified signature
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            # Dummy function to replace the original
            pass

        wrapper.__signature__ = new_signature

        # Initialize the parent FunctionTool
        super().__init__(wrapper, description, name, global_imports, strict)

        # Store the original function
        self._signature = inspect.signature(func)
        self._func = func

    async def run(self, args: BaseModel, cancellation_token: CancellationToken) -> Any:
        # Skip auth if no auth context
        if not self.auth:
            args = args.model_copy(update={TOKEN_FIELD: ""})  # Set a empty token if no auth context
            return await super().run(args, cancellation_token)

        try:
            token = await self.auth.manager.get_oauth_token(self.auth.config)
            if not token:
                # No token was received
                raise Exception(f"No OAuth token found for {self.auth.config}")

            # Modify args with the token
            args = args.model_copy(update={TOKEN_FIELD: token})

            # Execute the tool
            return await super().run(args, cancellation_token)
            
        except AuthorizationRequiredException as e:
            # User authorization is required - return auth URL in a format the tool can handle
            logger.info(f"Authorization required for tool {self.name}: {e.auth_url}")
            return {
                "error": "Authentication required to place orders", 
                "requires_auth": True,
                "auth_url": e.auth_url
            }
        except Exception as e:
            # Handle any other auth-related errors by generating auth URL directly
            if "authentication" in str(e).lower() or "authorization" in str(e).lower() or "oauth" in str(e).lower():
                logger.info(f"Auth error in tool {self.name}, generating auth URL: {e}")
                
                # Generate PKCE parameters for IETF compliance
                import base64
                import hashlib
                import secrets
                import os
                code_verifier = base64.urlsafe_b64encode(secrets.token_bytes(32)).decode('utf-8').rstrip('=')
                code_challenge = base64.urlsafe_b64encode(hashlib.sha256(code_verifier.encode()).digest()).decode('utf-8').rstrip('=')
                
                # Generate IETF compliant auth URL
                client_id = os.getenv('ASGARDEO_CLIENT_ID')
                redirect_uri = os.getenv('ASGARDEO_REDIRECT_URI', 'http://localhost:8001/callback')
                idp_base_url = os.getenv('ASGARDEO_TENANT_DOMAIN', 'https://dev.api.asgardeo.io/t/wso2conasia')
                agent_id = os.getenv('AGENT_ID', '18eab4f7-58f8-4d0f-8c36-5da2c4f925ee')
                
                # Use the same scopes as configured in the auth config
                scope = " ".join(self.auth.config.scopes) if self.auth and self.auth.config else "order:write openid profile"
                state = f"tool-auth-{secrets.token_urlsafe(16)}"
                
                auth_url = f"{idp_base_url}/oauth2/authorize?response_type=code&client_id={client_id}&redirect_uri={redirect_uri}&scope={scope}&state={state}&code_challenge={code_challenge}&code_challenge_method=S256&requested_actor={agent_id}"
                
                return {
                    "error": "Authentication required to place orders", 
                    "requires_auth": True,
                    "auth_url": auth_url
                }
            else:
                # Re-raise non-auth errors
                raise e
