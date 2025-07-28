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

import { useAuthContext } from "@asgardeo/auth-react";
import React, { FunctionComponent, ReactElement, useCallback, useEffect, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { isClaimVerified } from "../api/identity-verification-client";
import { Footer } from "../components/Footer";
import { NavBar } from "../components/NavBar";
import { AgeVerificationDrawer } from "../components/AgeVerificationDrawer";
import { LoadingSpinner } from "../components/LoadingSpinner";
import { Plans } from "../components/Plans";
import { ClaimVerificationStatus, WorkflowStatus } from "../model/identity-verification";
import { useConfig } from "../ConfigContext";
import { handleMissingIdvpId } from "../util/IdvProviderMessages";
import { DebugInfo } from "../components/DebugInfo";

/**
 * Home page for the Sample.
 *
 * @return {React.ReactElement}
 */
export const HomePage: FunctionComponent = (): ReactElement => {
    const { state } = useAuthContext();
    const navigate = useNavigate();
    const location = useLocation();
    const config = useConfig();

    const [verificationStatus, setVerificationStatus] = useState<ClaimVerificationStatus | null>(null);
    const [isDrawerOpen, setIsDrawerOpen] = useState<boolean>(false);
    const [drawerMessageType, setDrawerMessageType] = useState("info");
    const [drawerMessage, setDrawerMessage] = useState<string>("");
    const [isLoading, setIsLoading] = useState<boolean>(true);
    const [missingIdvpContent, setMissingIdvpContent] = useState<React.ReactNode | null>(null);

    const checkVerificationStatus = useCallback(() => {
        if (!config?.identityVerificationProviderId) {
            setIsLoading(false);
            setMissingIdvpContent(handleMissingIdvpId());
            return;
        }
        isClaimVerified("http://wso2.org/claims/dob", config)
            .then((status: ClaimVerificationStatus) => {
                setVerificationStatus(status);
                
                if (status.isVerified === true) {
                    setIsDrawerOpen(false);
                } else if (status.isVerified === undefined) {
                    setDrawerMessage("You need to verify your age and identity to register as a Pizza Shack delivery rider.");
                    setIsDrawerOpen(true);
                } else {
                    switch(status.workflowStatus) {
                        case WorkflowStatus.AWAITING_INPUT:
                            setDrawerMessage("Your age verification was interrupted. Please resume the verification to continue.");
                            break;
                        case WorkflowStatus.PROCESSING:
                            setDrawerMessage("Your age verification is in progress. Please check back later to complete your rider registration.");
                            break;
                        case WorkflowStatus.APPROVED:
                        case WorkflowStatus.DECLINED:
                        case WorkflowStatus.ABANDONED:
                            setDrawerMessage("Age verification failed. Please contact support for assistance.");
                            break;
                        case WorkflowStatus.REVIEW:
                            setDrawerMessage("Your age verification is under review. Please check back later.");
                            break;
                        case WorkflowStatus.ERROR:
                            setDrawerMessage("An error occurred during age verification. Please try again later or contact support.");
                            break;
                        default:
                            setDrawerMessage("Age verification status unclear. Please contact support for assistance.");
                    }
                    setIsDrawerOpen(true);
                }
            })
            .catch((error) => {
                console.error("Error verifying age:", error);
                console.error("Error details:", {
                    message: error.message,
                    response: error.response,
                    status: error.response?.status,
                    data: error.response?.data,
                    config: {
                        identityVerificationProviderId: config?.identityVerificationProviderId,
                        baseUrl: config?.baseUrl
                    }
                });
                
                let errorMessage = "An error occurred while verifying your age. Please try again later or contact support.";
                
                if (error.response?.status === 400 && error.response?.data?.code === "OIDV-10002") {
                    errorMessage = `Age verification requires complete profile information. Please complete your profile:

                    🔧 How to fix this:
                    1. Go to MyAccount: ${config?.userPortalURL}
                    2. Navigate to "Profile" section
                    3. Ensure these fields are filled:
                       ✓ First Name
                       ✓ Last Name  
                       ✓ Date of Birth
                    4. Save your profile changes
                    5. Return here and try again

                    These attributes are required for identity verification.`;
                } else if (error.response?.status === 404) {
                    errorMessage = "Identity verification provider not found. Please check your configuration.";
                } else if (error.response?.status === 403) {
                    errorMessage = "Access denied. Please check your permissions and try again.";
                } else if (error.response?.status === 500) {
                    errorMessage = "Server error occurred. Please try again later.";
                } else if (error.message?.includes('identityVerificationProviderId')) {
                    errorMessage = "Identity verification provider ID is missing or invalid.";
                }
                
                navigate('/generic-error', { 
                    state: { 
                        message: errorMessage,
                        details: process.env.NODE_ENV === 'development' ? error.message : undefined
                    }
                });
            })
            .then(() => {
                setIsLoading(false);
            });
    }, [config, navigate]);

    useEffect(() => {
        if (location?.state?.idVerificationInitiated) {
            navigate("/verification-in-progress");
        } else {
            setIsLoading(true);
            checkVerificationStatus();
        }
    }, [navigate, checkVerificationStatus, location]);

    /**
     * This useEffect tracks whether to display the age verification success message after 
     * the user completes age verification. The message will only be shown once to enhance 
     * user experience. If displayed previously, it will not appear again to prevent it 
     * from lingering at the top of the subscription page on subsequent visits.
     */
    useEffect(() => {
        const isAgeVerifiedSuccessMsgShown = localStorage.getItem(state.sub + "_isAgeVerifiedSuccessMsgShown") === "true";

        if (!isAgeVerifiedSuccessMsgShown && verificationStatus?.isVerified === true) {
            setIsDrawerOpen(true)
            setDrawerMessageType("success")
            setDrawerMessage("Age verification is successful! You're all set to continue with rider registration.")
            localStorage.setItem(state.sub + "_isAgeVerifiedSuccessMsgShown", "true")
        }
    },[verificationStatus])

    const handleVerifyAge = () => {
        if (verificationStatus?.workflowStatus === WorkflowStatus.AWAITING_INPUT) {
            navigate("/verify", { state: { reinitiate: true } });
        } else {
            navigate("/verify");
        }
    };

    if (missingIdvpContent) {
        return <>{missingIdvpContent}</>;
    }

    if (isLoading) {
        return <div style={{ minHeight: "100vh", display: "flex", alignItems: "center", justifyContent: "center"}}>
        <LoadingSpinner />
    </div>;
    }

    return (
        <div className="app-container">
            <NavBar />
            <AgeVerificationDrawer
                isOpen={isDrawerOpen}
                setIsOpen={setIsDrawerOpen}
                verifyAge={handleVerifyAge}
                message={drawerMessage}
                type={drawerMessageType}
                showButton={verificationStatus?.isVerified === undefined || verificationStatus?.workflowStatus === WorkflowStatus.AWAITING_INPUT}
            />
            <Plans isAgeVerified={verificationStatus?.isVerified === true} setIsDrawerOpen={setIsDrawerOpen} />
            
            <Footer />
            <DebugInfo />
        </div>
    );
};
