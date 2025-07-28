import React from 'react';
import { useAuthContext } from "@asgardeo/auth-react";
import { useConfig } from "../ConfigContext";

export const DebugInfo: React.FC = () => {
    const { state } = useAuthContext();
    const config = useConfig();

    if (process.env.NODE_ENV !== 'development') {
        return null;
    }

    return (
        <div style={{
            position: 'fixed',
            bottom: '10px',
            right: '10px',
            background: 'rgba(0,0,0,0.8)',
            color: 'white',
            padding: '10px',
            borderRadius: '5px',
            fontSize: '12px',
            maxWidth: '300px',
            zIndex: 9999
        }}>
            <div><strong>Debug Info:</strong></div>
            <div>Authenticated: {state?.isAuthenticated ? 'Yes' : 'No'}</div>
            <div>Username: {state?.username || 'N/A'}</div>
            <div>Client ID: {config?.clientID || 'Missing'}</div>
            <div>Base URL: {config?.baseUrl || 'Missing'}</div>
            <div>IdV Provider: {config?.identityVerificationProviderId ? 'Present' : 'Missing'}</div>
            {state?.isAuthenticated && (
                <div>
                    <strong>User Claims:</strong>
                    <pre style={{ fontSize: '10px', marginTop: '5px' }}>
                        {JSON.stringify(state, null, 2)}
                    </pre>
                </div>
            )}
        </div>
    );
};