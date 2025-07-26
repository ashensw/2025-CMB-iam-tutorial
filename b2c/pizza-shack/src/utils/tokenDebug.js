/**
 * Token debugging utilities
 */

export function decodeToken(token) {
  try {
    if (!token) return null;
    
    const parts = token.split('.');
    if (parts.length !== 3) return null;
    
    const payload = JSON.parse(atob(parts[1]));
    return payload;
  } catch (error) {
    console.error('Failed to decode token:', error);
    return null;
  }
}

export function debugTokenScopes(token) {
  const payload = decodeToken(token);
  if (!payload) {
    console.log('❌ Could not decode token');
    return;
  }
  
  console.log('🔍 Token Debug Information:');
  console.log('├─ Subject (sub):', payload.sub);
  console.log('├─ Issuer (iss):', payload.iss);
  console.log('├─ Audience (aud):', payload.aud);
  console.log('├─ Expires (exp):', new Date(payload.exp * 1000));
  console.log('├─ Issued at (iat):', new Date(payload.iat * 1000));
  
  // Check different scope formats
  if (payload.scope) {
    const scopes = typeof payload.scope === 'string' ? payload.scope.split(' ') : payload.scope;
    console.log('├─ Scopes (scope field):', scopes);
  }
  
  if (payload.scp) {
    console.log('├─ Scopes (scp field):', payload.scp);
  }
  
  if (payload.scopes) {
    console.log('├─ Scopes (scopes field):', payload.scopes);
  }
  
  // Check for specific Pizza API scopes
  const allScopes = [
    ...(payload.scope ? (typeof payload.scope === 'string' ? payload.scope.split(' ') : payload.scope) : []),
    ...(payload.scp || []),
    ...(payload.scopes || [])
  ];
  
  const pizzaScopes = allScopes.filter(scope => 
    scope.includes('order') || scope.includes('pizza')
  );
  
  console.log('├─ Pizza-related scopes found:', pizzaScopes);
  console.log('├─ Has order:read?', allScopes.includes('order:read'));
  console.log('├─ Has order:write?', allScopes.includes('order:write'));
  console.log('└─ All available scopes:', allScopes);
  
  return {
    allScopes,
    pizzaScopes,
    hasOrderRead: allScopes.includes('order:read'),
    hasOrderWrite: allScopes.includes('order:write'),
    payload
  };
}

export function debugAsgardeoConfig() {
  console.log('🔧 Asgardeo Configuration Debug:');
  console.log('├─ Requested scopes: [\'openid\', \'profile\', \'order:read\', \'order:write\']');
  console.log('├─ Client ID: T54WRrMa4zZvS0_7PhjQF0u077Ua');
  console.log('├─ Base URL: https://api.asgardeo.io/t/wso2conasia');
  console.log('├─ Custom scopes need to be configured in Asgardeo Console');
  console.log('├─ Go to: Applications → Your App → API Authorization');
  console.log('├─ Create API Resource: pizza_api');
  console.log('├─ Add scopes: order:read, order:write');
  console.log('└─ Authorize app to use these scopes');
}