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

import { useNavigate } from 'react-router-dom';
import { InsurancePlanCard } from "../model/insurance-plan";
import React from 'react';

const plans: InsurancePlanCard[] = [
    {
        title: 'Bicycle Rider',
        price: '200',
        description: [
            'Delivery for single location in one ride',
            'Delivery time: 30 minutes',
            'Delivery distance: 5 km',
        ],
        buttonText: 'Get started',
        buttonVariant: 'contained',
    },
    {
        title: 'Car Rider',
        price: '250',
        description: [
            'Delivery for 4 locations in one ride',
            'Delivery time: 2 hour',
            'Delivery distance: 15 km',
        ],
        buttonText: 'Get started',
        buttonVariant: 'contained',
    },
    {
        title: 'Delivery Van',
        price: '300',
        description: [
            'Delivery for 8 locations in one ride',
            'Delivery time: 4 hours',
            'Delivery distance: 30 km',
        ],
        buttonText: 'Get started',
        buttonVariant: 'contained',
    },
];

interface PlanProps {
    isAgeVerified: boolean;
    setIsDrawerOpen: (isDrawerOpen: boolean) => void;
}

export const Plans = (props: PlanProps) => {
    const { isAgeVerified, setIsDrawerOpen } = props;
    const navigate = useNavigate();

    /**
     * If the user is age verified, navigate to the success page. Else, open the age verification drawer.
     *
     * @param plan - The selected insurance plan.
     */
    const handlePlanSelection = (plan: InsurancePlanCard) => {
        if (isAgeVerified) {
            navigate("/success", { state: { plan: plan.title } });
        } else {
            setIsDrawerOpen(true);
        }
    }

    return (
        <div className="main-content">
            <div className="content-panel">
                <div style={{ padding: 'var(--space-8)', textAlign: 'center' }}>
                    <h2>🚗 Choose Your Delivery Plan</h2>
                    <p>Select your rider plan based on your license type, preferences, and delivery capacity.</p>
                </div>
                
                <div className="menu-grid">
                    {plans.map((plan: InsurancePlanCard) => (
                        <div key={plan.title} className="pizza-card">
                            <div className="pizza-content">
                                <h3 className="pizza-title">{plan.title}</h3>
                                <div className="pizza-price price-lg">${plan.price}/month</div>
                                <div className="pizza-description">
                                    {plan.description.map((line, index) => (
                                        <div key={index} style={{ marginBottom: 'var(--space-2)' }}>
                                            ✓ {line}
                                        </div>
                                    ))}
                                </div>
                                <div className="pizza-footer">
                                    <button
                                        className={`pizza-add-btn ${!isAgeVerified ? 'btn-secondary' : ''}`}
                                        disabled={!isAgeVerified}
                                        onClick={() => handlePlanSelection(plan)}
                                    >
                                        {isAgeVerified ? 'Register for Plan' : 'Verify Age First'}
                                    </button>
                                </div>
                            </div>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
}
