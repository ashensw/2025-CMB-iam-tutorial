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

import React, { FunctionComponent, useEffect, useState, useRef } from "react";
import { Onfido } from 'onfido-sdk-ui'
import { useNavigate, useLocation } from "react-router-dom";
import { completeVerification, initiateVerification, reinitiateVerification } from "../api/identity-verification-client";
import { IdVResponseInterface } from "../model/identity-verification";
import { Footer } from "../components/Footer";
import { NavBar } from "../components/NavBar";
import { LoadingSpinner } from "../components/LoadingSpinner";
import { ReactErrorBoundary } from "../components/ReactErrorBoundary";
import { Handle } from "onfido-sdk-ui/types/Onfido";
import { useConfig } from "../ConfigContext";

interface VerifyPageProps {
    setVerificationInitiated?: (isInitiated: boolean) => void;
    setShowVerificationWidget?: (show: boolean) => void;
}

export const VerifyPage: FunctionComponent<VerifyPageProps> = () => {
    const navigate = useNavigate();
    const config = useConfig();
    const [loading, setLoading] = useState<boolean>(true);
    const [onfidoInstance, setOnfidoInstance] = useState<Handle | null>(null);
    const [isInitialized, setIsInitialized] = useState<boolean>(false);
    const onfidoMountRef = useRef<HTMLDivElement>(null);

    const location = useLocation();
    const reinitiate = location.state?.reinitiate === true;

    const initIdentityVerification = async () => {
        // Prevent duplicate initialization
        if (isInitialized) {
            console.log("Onfido already initialized, skipping...");
            return;
        }

        try {
            setIsInitialized(true);
            console.log("Starting Onfido verification initialization...");

            // Clear any existing Onfido mount point content using ref
            if (onfidoMountRef.current) {
                try {
                    // Use innerHTML to avoid React DOM conflicts during initialization
                    onfidoMountRef.current.innerHTML = '';
                    console.log("Mount point cleared for new initialization");
                } catch (error) {
                    console.warn("Could not clear mount point:", error);
                }
            }

            let response: IdVResponseInterface;

            if (reinitiate) {
                console.log("Reinitiating verification");
                response = await reinitiateVerification(config);
            } else {
                console.log("Initiating verification");
                response = await initiateVerification(config);
            }

            const token = response?.claims?.[0]?.claimMetadata?.sdk_token;
            const workflowRunId = response?.claims?.[0]?.claimMetadata?.onfido_workflow_run_id;

            if (!token || !workflowRunId) {
                const missingItem = !token ? "SDK token" : "Workflow run ID";
                throw new Error(`${missingItem} not found in the identity verification initiation response from the Identity server`);
            }

            console.log("Initializing Onfido with token and workflowRunId...");
            const instance = Onfido.init({
                token,
                containerId: 'onfido-mount',
                onComplete: (data: any) => {
                    console.log('Verification completed', data);
                    completeVerification(config);
                    navigate('/', { state: { idVerificationInitiated: true } });
                },
                onError: (error: any) => {
                    console.error('Onfido error:', error);
                    setLoading(false); // Stop loading on error
                },
                workflowRunId
            });
            setOnfidoInstance(instance);
            console.log("Onfido initialization complete");

            // Multiple checks to monitor Onfido rendering using ref
            const checkOnfidoRendering = () => {
                if (onfidoMountRef.current) {
                    console.log("Onfido mount point found, children count:", onfidoMountRef.current.children.length);
                    if (onfidoMountRef.current.children.length > 0) {
                        console.log("✅ Onfido has rendered successfully!");
                        console.log("First child element:", onfidoMountRef.current.children[0]);
                        setLoading(false); // Stop loading when Onfido renders
                        return true;
                    }
                } else {
                    console.log("❌ Onfido mount point ref not available");
                }
                return false;
            };

            // Check multiple times to catch when Onfido renders
            setTimeout(() => checkOnfidoRendering(), 1000);
            setTimeout(() => checkOnfidoRendering(), 3000);
            setTimeout(() => checkOnfidoRendering(), 5000);
        } catch (error) {
            console.error("Identity verification initialization failed:", error);
            setIsInitialized(false); // Reset on error so it can be retried
            
            let ErrorMessage;
            if (error.response?.status === 400 && error.response?.data?.code === "OIDV-10002") {
                ErrorMessage = `Age verification requires complete profile information. Please complete your profile:

                    🔧 How to fix this:
                    1. Go to MyAccount: ${config?.userPortalURL}
                    2. Navigate to "Profile" section
                    3. Ensure these fields are filled:
                       ✓ First Name
                       ✓ Last Name  
                       ✓ Date of Birth
                    4. Save your profile changes
                    5. Return here and try again

                    These attributes are required for identity verification with Onfido.`;
            } else {
                ErrorMessage = error.response?.data?.description || error.message || "An unexpected error occurred during identity verification setup. Please try again later or contact support.";
            }
            navigate('/generic-error', { state: { message: ErrorMessage } });
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        initIdentityVerification();

        // Cleanup function to properly tear down Onfido instance
        return () => {
            console.log("Cleaning up Onfido instance...");
            
            // First tear down Onfido instance
            if (onfidoInstance) {
                try {
                    onfidoInstance.tearDown();
                    console.log("Onfido instance torn down successfully");
                } catch (error) {
                    console.error("Error tearing down Onfido instance:", error);
                }
                setOnfidoInstance(null);
            }
            
            // Clear the mount point very safely using ref
            setTimeout(() => {
                if (onfidoMountRef.current) {
                    try {
                        // Use innerHTML to avoid React DOM conflicts
                        onfidoMountRef.current.innerHTML = '';
                        console.log("Mount point cleared successfully");
                    } catch (error) {
                        console.error("Error clearing mount point:", error);
                    }
                }
            }, 100); // Small delay to avoid React conflicts
        }
    }, []) // Empty dependency array - only run once

    return (
        <div className="app-container">
            <NavBar/>
            <div className="verify-page-container">
                <ReactErrorBoundary>
                    <div 
                        ref={onfidoMountRef}
                        id="onfido-mount" 
                        className="onfido-container"
                    >
                        {loading && (
                            <div className="loading-container">
                                <LoadingSpinner/>
                            </div>
                        )}
                    </div>
                </ReactErrorBoundary>
            </div>
            <Footer/>
        </div>
    );
}
