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

import json
import logging
import base64
import time
from datetime import datetime, timezone
from typing import Dict, Any, Optional, Union
import jwt

logger = logging.getLogger(__name__)

class TokenLogger:
    """Enhanced token logging utility for comprehensive token analysis and debugging"""
    
    def __init__(self, log_level: int = logging.INFO):
        self.logger = logging.getLogger(f"{__name__}.TokenLogger")
        self.logger.setLevel(log_level)
        
        # Configure formatter if not already configured
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
    
    def log_token_request(
        self, 
        token_type: str, 
        endpoint: str, 
        request_data: Dict[str, Any],
        scopes: Optional[list] = None,
        resource: Optional[str] = None,
        agent_info: Optional[Dict[str, str]] = None
    ):
        """Log comprehensive token request details"""
        self.logger.info("🔐" * 5 + " TOKEN REQUEST START " + "🔐" * 5)
        self.logger.info(f"📝 REQUEST TYPE: {token_type}")
        self.logger.info(f"🌐 ENDPOINT: {endpoint}")
        self.logger.info(f"⏰ TIMESTAMP: {datetime.now(timezone.utc).isoformat()}")
        
        if scopes:
            self.logger.info(f"🔑 SCOPES: {scopes}")
        if resource:
            self.logger.info(f"🎯 RESOURCE: {resource}")
        if agent_info:
            self.logger.info(f"🤖 AGENT INFO: {agent_info}")
        
        # Log request parameters (excluding sensitive data)
        sanitized_data = self._sanitize_request_data(request_data)
        self.logger.info(f"📋 REQUEST PARAMS:")
        for key, value in sanitized_data.items():
            self.logger.info(f"   └─ {key}: {value}")
    
    def log_token_response(
        self, 
        token_type: str, 
        token_response: Dict[str, Any],
        decode_token: bool = True
    ):
        """Log comprehensive token response with decoding"""
        self.logger.info("✅" * 5 + " TOKEN RESPONSE START " + "✅" * 5)
        self.logger.info(f"📝 RESPONSE TYPE: {token_type}")
        self.logger.info(f"⏰ TIMESTAMP: {datetime.now(timezone.utc).isoformat()}")
        
        # Log basic token info
        token_info = {
            'token_type': token_response.get('token_type', 'Bearer'),
            'expires_in': token_response.get('expires_in', 'Not specified'),
            'scope': token_response.get('scope', 'Not specified'),
        }
        
        self.logger.info("📋 TOKEN METADATA:")
        for key, value in token_info.items():
            self.logger.info(f"   └─ {key}: {value}")
        
        # Decode and log access token if present
        if 'access_token' in token_response and decode_token:
            self._log_decoded_token(
                token_response['access_token'], 
                "ACCESS TOKEN",
                token_type
            )
        
        # Decode and log ID token if present
        if 'id_token' in token_response and decode_token:
            self._log_decoded_token(
                token_response['id_token'], 
                "ID TOKEN",
                token_type
            )
        
        # Log refresh token info (without decoding for security)
        if 'refresh_token' in token_response:
            refresh_token = token_response['refresh_token']
            preview = f"{refresh_token[:15]}...{refresh_token[-10:]}" if len(refresh_token) > 25 else refresh_token
            self.logger.info(f"🔄 REFRESH TOKEN: {preview}")
        
        self.logger.info("✅" * 5 + " TOKEN RESPONSE END " + "✅" * 5)
    
    def log_agent_authentication_flow(
        self,
        agent_name: str,
        agent_id: str,
        flow_step: str,
        flow_data: Dict[str, Any],
        success: bool = True
    ):
        """Log Agent Authentication flow steps in detail"""
        status_icon = "✅" if success else "❌"
        self.logger.info(f"🤖 {status_icon} AGENT AUTH FLOW - {flow_step}")
        self.logger.info(f"   └─ Agent Name: {agent_name}")
        self.logger.info(f"   └─ Agent ID: {agent_id}")
        self.logger.info(f"   └─ Timestamp: {datetime.now(timezone.utc).isoformat()}")
        
        if flow_data:
            sanitized_data = self._sanitize_request_data(flow_data)
            self.logger.info("   └─ Flow Data:")
            for key, value in sanitized_data.items():
                self.logger.info(f"      ├─ {key}: {value}")
    
    def log_obo_flow(
        self,
        user_token_preview: Optional[str],
        agent_token_preview: Optional[str], 
        obo_token: Optional[Dict[str, Any]],
        step: str,
        success: bool = True
    ):
        """Log On-Behalf-Of (OBO) token exchange flow"""
        status_icon = "✅" if success else "❌"
        self.logger.info(f"🔄 {status_icon} OBO FLOW - {step}")
        self.logger.info(f"   └─ Timestamp: {datetime.now(timezone.utc).isoformat()}")
        
        if user_token_preview:
            self.logger.info(f"   └─ User Token: {user_token_preview}")
        if agent_token_preview:
            self.logger.info(f"   └─ Agent Token: {agent_token_preview}")
        
        if obo_token:
            self._log_decoded_token(obo_token.get('access_token'), "OBO ACCESS TOKEN", "OBO")
    
    def log_token_error(
        self,
        error_type: str,
        error_message: str,
        error_details: Optional[Dict[str, Any]] = None,
        fallback_attempted: bool = False,
        fallback_success: bool = False
    ):
        """Log token-related errors and fallback attempts"""
        self.logger.error("❌" * 5 + " TOKEN ERROR " + "❌" * 5)
        self.logger.error(f"🚫 ERROR TYPE: {error_type}")
        self.logger.error(f"💬 ERROR MESSAGE: {error_message}")
        self.logger.error(f"⏰ TIMESTAMP: {datetime.now(timezone.utc).isoformat()}")
        
        if error_details:
            self.logger.error("📋 ERROR DETAILS:")
            for key, value in error_details.items():
                self.logger.error(f"   └─ {key}: {value}")
        
        if fallback_attempted:
            fallback_icon = "✅" if fallback_success else "❌"
            self.logger.error(f"🔄 FALLBACK ATTEMPTED: {fallback_icon} {'Success' if fallback_success else 'Failed'}")
    
    def _log_decoded_token(self, token: str, token_label: str, token_type: str):
        """Decode and log JWT token contents"""
        if not token:
            return
        
        try:
            # Create token preview
            token_preview = f"{token[:20]}...{token[-10:]}" if len(token) > 30 else token
            
            # Decode without verification to inspect claims
            decoded = jwt.decode(token, options={"verify_signature": False})
            
            self.logger.info(f"🔍 {token_label} ({token_type}):")
            self.logger.info(f"   └─ Token Preview: {token_preview}")
            self.logger.info(f"   └─ Token Length: {len(token)} characters")
            
            # Log standard JWT claims
            standard_claims = {
                'iss': 'Issuer',
                'sub': 'Subject (User/Agent ID)', 
                'aud': 'Audience',
                'exp': 'Expires At',
                'iat': 'Issued At',
                'nbf': 'Not Before',
                'jti': 'JWT ID',
                'scope': 'Scopes',
                'client_id': 'Client ID',
                'username': 'Username'
            }
            
            self.logger.info("   └─ STANDARD CLAIMS:")
            for claim, description in standard_claims.items():
                if claim in decoded:
                    value = decoded[claim]
                    if claim in ['exp', 'iat', 'nbf'] and isinstance(value, (int, float)):
                        # Convert Unix timestamp to readable format
                        readable_time = datetime.fromtimestamp(value, tz=timezone.utc).isoformat()
                        self.logger.info(f"      ├─ {claim} ({description}): {value} ({readable_time})")
                    else:
                        self.logger.info(f"      ├─ {claim} ({description}): {value}")
            
            # Check for OBO token pattern (act claim)
            if 'act' in decoded:
                self.logger.info("   └─ 🎯 ON-BEHALF-OF (OBO) PATTERN DETECTED:")
                act_claim = decoded['act']
                user_id = decoded.get('sub')
                agent_id = act_claim.get('sub') if isinstance(act_claim, dict) else str(act_claim)
                
                self.logger.info(f"      ├─ User ID: {user_id}")
                self.logger.info(f"      ├─ Acting Agent ID: {agent_id}")
                self.logger.info(f"      └─ Full Act Claim: {act_claim}")
            
            # Check for agent-specific claims
            agent_claims = ['agent_id', 'agent_name', 'actor_token', 'requested_actor']
            agent_claim_found = False
            for claim in agent_claims:
                if claim in decoded:
                    if not agent_claim_found:
                        self.logger.info("   └─ 🤖 AGENT-SPECIFIC CLAIMS:")
                        agent_claim_found = True
                    self.logger.info(f"      ├─ {claim}: {decoded[claim]}")
            
            # Log custom/additional claims
            excluded_claims = set(standard_claims.keys()) | {'act'} | set(agent_claims)
            custom_claims = {k: v for k, v in decoded.items() if k not in excluded_claims}
            
            if custom_claims:
                self.logger.info("   └─ CUSTOM/ADDITIONAL CLAIMS:")
                for claim, value in custom_claims.items():
                    # Truncate very long values
                    if isinstance(value, str) and len(value) > 100:
                        display_value = f"{value[:50]}...{value[-20:]}"
                    else:
                        display_value = value
                    self.logger.info(f"      ├─ {claim}: {display_value}")
            
            # Log token validation status
            current_time = time.time()
            if 'exp' in decoded:
                exp_time = decoded['exp']
                is_expired = current_time >= exp_time
                time_to_expiry = exp_time - current_time
                
                if is_expired:
                    self.logger.warning(f"   └─ ⚠️ TOKEN STATUS: EXPIRED ({abs(time_to_expiry):.0f} seconds ago)")
                else:
                    self.logger.info(f"   └─ ✅ TOKEN STATUS: VALID (expires in {time_to_expiry:.0f} seconds)")
            
        except jwt.DecodeError as e:
            self.logger.warning(f"   └─ ⚠️ Failed to decode {token_label}: Invalid JWT format - {e}")
        except Exception as e:
            self.logger.warning(f"   └─ ⚠️ Failed to decode {token_label}: {e}")
    
    def _sanitize_request_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitize request data by masking sensitive information"""
        sensitive_keys = {
            'password', 'client_secret', 'authorization', 'access_token', 
            'refresh_token', 'code_verifier', 'actor_token'
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
    
    def log_flow_summary(
        self, 
        flow_type: str,
        user_id: Optional[str] = None,
        agent_id: Optional[str] = None,
        success: bool = True,
        total_steps: int = 0,
        duration_seconds: Optional[float] = None
    ):
        """Log a summary of the entire authentication flow"""
        status_icon = "✅" if success else "❌"
        self.logger.info("=" * 60)
        self.logger.info(f"📊 {status_icon} AUTHENTICATION FLOW SUMMARY")
        self.logger.info(f"   └─ Flow Type: {flow_type}")
        if user_id:
            self.logger.info(f"   └─ User ID: {user_id}")
        if agent_id:
            self.logger.info(f"   └─ Agent ID: {agent_id}")
        self.logger.info(f"   └─ Status: {'SUCCESS' if success else 'FAILED'}")
        if total_steps > 0:
            self.logger.info(f"   └─ Steps Completed: {total_steps}")
        if duration_seconds is not None:
            self.logger.info(f"   └─ Duration: {duration_seconds:.2f} seconds")
        self.logger.info(f"   └─ Timestamp: {datetime.now(timezone.utc).isoformat()}")
        self.logger.info("=" * 60)


# Convenience instance for easy import
token_logger = TokenLogger()