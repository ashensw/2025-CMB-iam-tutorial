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
import React, { FunctionComponent, ReactElement, useEffect } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import { Footer } from "../components/Footer";
import { NavBar } from "../components/NavBar";
import { LoadingSpinner } from "../components/LoadingSpinner";
import { Typography, Button, Box } from "@oxygen-ui/react";
import { handleMissingClientId } from "../util/IdvProviderMessages";
import { useConfig } from "../ConfigContext";

const PIZZA_RIDER_IMAGE = `/images/rider.webp`;
const PIZZA_LOGO = `/images/logo.jpg`;

export const LoginPage: FunctionComponent = (): ReactElement => {
    const { state, signIn } = useAuthContext();
    const navigate = useNavigate();
    const location = useLocation();
    const config = useConfig();

    useEffect(() => {
        if (state?.isAuthenticated) {
            const from = (location.state as any)?.from?.pathname || "/";
            navigate(from, { replace: true });
        }
    }, [state?.isAuthenticated, navigate, location]);

    if (!config?.clientID) {
        return handleMissingClientId();
    }

    if (state?.isLoading) {
        return <LoadingSpinner />;
    }

    const handleLogin = () => {
        signIn()
            .catch((error) => {
                console.error("Error during sign-in:", error);
                navigate('/auth-error');
            });
    };

    return (
        <div className="login-background">
            <NavBar />
            <div className="login-box">
                <img 
                    src={PIZZA_LOGO} 
                    className="login-logo" 
                    alt="Pizza Shack Logo" 
                />
                <h1>Pizza Shack Riders</h1>
                <p>Join our delivery team</p>
                <p>
                    Log in to register as a Pizza Shack delivery rider and complete your age verification.
                </p>
                <button 
                    onClick={handleLogin}
                    className="btn-primary btn-lg btn-full"
                >
                    Login to Start Registration
                </button>
            </div>
            <Footer />
        </div>
    );
};
