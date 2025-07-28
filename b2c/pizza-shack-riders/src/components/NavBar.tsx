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

import React from "react";
import { useAuthContext } from "@asgardeo/auth-react";
import { useConfig } from "../ConfigContext";

export const NavBar = () => {
    const { state, signOut } = useAuthContext();
    const [dropdownOpen, setDropdownOpen] = React.useState(false);
    const config = useConfig();

    const handleLogout = () => {
        signOut().catch((e) => console.error("Error while signing out. ", e));
        setDropdownOpen(false);
    };

    const handleMyAccount = () => {
        window.open(config?.userPortalURL, '_blank');
        setDropdownOpen(false);
    };

    const PIZZA_LOGO = `/images/logo.jpg`;

    return (
        <nav className="top-nav">
            <div className="nav-brand">
                <img src={PIZZA_LOGO} alt="Pizza Shack" />
                <span>Pizza Shack Riders</span>
            </div>

            <div className="nav-buttons">
                {state?.isAuthenticated && (
                    <div className="nav-user dropdown">
                        <button 
                            className="nav-user-button"
                            onClick={() => setDropdownOpen(!dropdownOpen)}
                        >
                            <span>{state.username || "User"}</span>
                            <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
                                <path d="M8 9.5L5 6.5h6L8 9.5z"/>
                            </svg>
                        </button>
                        
                        {dropdownOpen && (
                            <div className="dropdown-content">
                                <button onClick={handleMyAccount}>
                                    My Account
                                </button>
                                <button onClick={handleLogout} className="danger">
                                    Logout
                                </button>
                            </div>
                        )}
                    </div>
                )}
            </div>
        </nav>
    );
}
