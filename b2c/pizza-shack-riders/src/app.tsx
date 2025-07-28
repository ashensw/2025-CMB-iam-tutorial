/**
 * Copyright (c) 2024, WSO2 LLC. (https://www.wso2.com).
 *
 * WSO2 LLC. licenses this file to you under the Apache License,
 * Version 2.0 (the "License"); you may not use this file except
 * in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing,
 * software distributed under the License is distributed on an
 * "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
 * KIND, either express or implied. See the License for the
 * specific language governing permissions and limitations
 * under the License.
 */

import React, { useState, useEffect, FunctionComponent, ReactElement } from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';

import { AuthProvider, useAuthContext } from '@asgardeo/auth-react';
import { ThemeProvider } from '@oxygen-ui/react';

import { loadConfig } from './config-loader';
import GuardioTheme from './styles/guardio-theme';

import { ConfigProvider } from './ConfigContext';
import { ErrorBoundary } from './ErrorBoundary';
import { LoadingSpinner } from './components/LoadingSpinner';
import { ProtectedRoute } from './components/ProtectedRoute';

import { 
    HomePage, 
    NotFoundPage, 
    GenericErrorPage, 
    VerificationInProgressPage, 
    SuccessPage, 
    VerifyPage, 
    LoginPage, 
    AuthenticationFailurePage } from "./pages";

const AppContent: FunctionComponent = (): ReactElement => {
    const { error } = useAuthContext();

    return (
        <ErrorBoundary error={error}>
            <Router basename={import.meta.env.VITE_BASE_URL || "/"}>
                <Routes>
                    <Route path="/login" element={<LoginPage />} />
                    <Route path="/" element={<ProtectedRoute><HomePage /></ProtectedRoute>} />
                    <Route path="/verify" element={<ProtectedRoute><VerifyPage /></ProtectedRoute>} />
                    <Route path="/success" element={<ProtectedRoute><SuccessPage /></ProtectedRoute>} />
                    <Route path="/verification-in-progress" element={<ProtectedRoute><VerificationInProgressPage /></ProtectedRoute>} />
                    <Route path="/generic-error" element={<GenericErrorPage />} />
                    <Route path="/auth-error" element={<AuthenticationFailurePage />} />
                    <Route path="*" element={<NotFoundPage />} />
                </Routes>
            </Router>
        </ErrorBoundary>
    );
};

const App: FunctionComponent = (): ReactElement => {
    const [config, setConfig] = useState(null);

    useEffect(() => {
        loadConfig().then(loadedConfig => {
            setConfig(loadedConfig);
        }).catch(error => {
            console.error('Error loading config:', error);
        });
    }, []);

    if (!config) {
        return (
            <div className="app-container">
                <LoadingSpinner />
            </div>
        );
    }

    return (
        <div className="app-container">
            <ConfigProvider config={config}>
                <AuthProvider config={config}>
                    <ThemeProvider theme={GuardioTheme} defaultMode="light">
                        <AppContent/>
                    </ThemeProvider>
                </AuthProvider>
            </ConfigProvider>
        </div>
    );
};

export default App;
