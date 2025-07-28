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

import React from 'react';
import { useLocation, useNavigate } from "react-router-dom";
import { Footer } from "../components/Footer";
import { NavBar } from "../components/NavBar";

export const SuccessPage = () => {
    const navigate = useNavigate();
    const location = useLocation();
    const plan = location?.state?.plan;

    return (
        <div className="app-container">
            <NavBar />
            <div className="main-content">
                <div className="content-panel">
                    <div style={{ 
                        padding: 'var(--space-20)', 
                        textAlign: 'center',
                        display: 'flex',
                        flexDirection: 'column',
                        alignItems: 'center',
                        justifyContent: 'center',
                        minHeight: '50vh'
                    }}>
                        <div style={{ fontSize: '4rem', marginBottom: 'var(--space-6)' }}>🎉</div>
                        <h2>Welcome to the Pizza Shack Riders Team!</h2>
                        <p style={{ 
                            fontSize: 'var(--text-lg)', 
                            marginBottom: 'var(--space-8)',
                            maxWidth: '600px',
                            lineHeight: '1.6'
                        }}>
                            Congratulations! You have successfully registered for the <strong>{plan ?? "delivery"}</strong> plan. 
                            Our team will contact you within 24 hours to complete your onboarding and schedule your first delivery shift.
                        </p>
                        <div style={{ 
                            background: 'var(--accent-mint)', 
                            padding: 'var(--space-6)', 
                            borderRadius: 'var(--radius-lg)',
                            marginBottom: 'var(--space-8)',
                            border: '1px solid var(--accent-green)'
                        }}>
                            <h4 style={{ color: 'var(--accent-green)', marginBottom: 'var(--space-3)' }}>Next Steps:</h4>
                            <ul style={{ textAlign: 'left', color: 'var(--text-primary)' }}>
                                <li>Check your email for onboarding instructions</li>
                                <li>Prepare your delivery vehicle and required documents</li>
                                <li>Download the Pizza Shack Rider mobile app</li>
                                <li>Complete your profile setup</li>
                            </ul>
                        </div>
                        <button 
                            className="btn-primary btn-lg"
                            onClick={() => navigate("/")}
                        >
                            Return to Dashboard
                        </button>
                    </div>
                </div>
            </div>
            <Footer />
        </div>
    );
}
