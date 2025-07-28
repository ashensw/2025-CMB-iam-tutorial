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

interface AgeVerificationDrawerProps {
    isOpen: boolean;
    setIsOpen: (isOpen: boolean) => void;
    verifyAge: () => void;
    message: string;
    type: string;
    showButton: boolean;
}

export const AgeVerificationDrawer: React.FC<AgeVerificationDrawerProps> = (props) => {
    const {
        isOpen,
        setIsOpen,
        verifyAge,
        message,
        type,
        showButton
    } = props;

    const getNotificationClass = (messageType: string) => {
        switch(messageType){
            case "info":
                return 'notification-info'
            case "success":
                return "notification-success"
            default:
                return 'notification-info'
        }
    }

    if (!isOpen) return null;

    return (
        <div className={`notification-banner ${getNotificationClass(type)}`}>
            <div className="notification-content">
                <p>{message}</p>
                {showButton && (
                    <button
                        className="btn-primary btn-sm"
                        onClick={verifyAge}
                    >
                        Verify Age & Identity
                    </button>
                )}
                <button
                    className="btn-ghost btn-sm"
                    onClick={() => setIsOpen(false)}
                >
                    ✕
                </button>
            </div>
        </div>
    );
};
