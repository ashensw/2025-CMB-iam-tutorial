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

import { HttpRequestConfig, HttpResponse } from "@asgardeo/auth-react";
import { IdVClaim, SdkFlowStatus, IdVResponseInterface, ClaimVerificationStatus } from "../model/identity-verification";
import { IdVConstants } from "../constants/idv-constants";
import { AsgardeoSPAClient } from "@asgardeo/auth-react";
import { ConfigInterface } from "../config-loader";

const httpClient = AsgardeoSPAClient.getInstance();

export const initiateVerification = async (config: ConfigInterface): Promise<IdVResponseInterface> => {
    return changeVerificationStatus(SdkFlowStatus.INITIATED, config)
}

export const completeVerification = async (config: ConfigInterface): Promise<IdVResponseInterface> => {
    return changeVerificationStatus(SdkFlowStatus.COMPLETED, config);
}

export const reinitiateVerification = async (config: ConfigInterface): Promise<IdVResponseInterface> => {
    return changeVerificationStatus(SdkFlowStatus.REINITIATED, config);
}

const changeVerificationStatus = async (status: SdkFlowStatus, config: ConfigInterface): Promise<IdVResponseInterface> => {

    const requestConfig: HttpRequestConfig = {
        url: `${config?.baseUrl}/api/users/v1/me/idv/verify`,
        method: IdVConstants.HTTP_POST,
        headers: {
            'Content-Type': IdVConstants.APPLICATION_JSON,
            'Accept': IdVConstants.APPLICATION_JSON
        },
        data: {
            "idVProviderId": config?.identityVerificationProviderId,
            "claims": [
                "http://wso2.org/claims/dob",
                "http://wso2.org/claims/givenname",
                "http://wso2.org/claims/lastname"
            ],
            "properties": [
                {
                    "key": "status",
                    "value": status
                }
            ]
        }
    }

    return httpClient.httpRequest(requestConfig)
        .then((response: HttpResponse<IdVResponseInterface>) => {
            return response.data;
        })
        .catch((error) => {
            throw error;
        });
}

export const isClaimVerified = async (claimToVerify: string, config: ConfigInterface): Promise<ClaimVerificationStatus> => {

    console.log("Checking claim verification for:", claimToVerify);
    console.log("Config:", {
        baseUrl: config?.baseUrl,
        identityVerificationProviderId: config?.identityVerificationProviderId
    });

    const requestConfig: HttpRequestConfig = {
        url: `${config?.baseUrl}/api/users/v1/me/idv/claims/`,
        method: IdVConstants.HTTP_GET,
        headers: {
            'Content-Type': IdVConstants.URL_ENCODED,
            'Accept': IdVConstants.APPLICATION_JSON
        },
        params: {
            "idVProviderId": config?.identityVerificationProviderId ?? "",
        }
    }

    console.log("Making API request to:", requestConfig.url);
    console.log("Request config:", requestConfig);

    return httpClient.httpRequest(requestConfig)
        .then((response: HttpResponse<IdVClaim[]>) => {
            console.log("API response received:", response);
            const claims = response.data as IdVClaim[];
            console.log("Claims data:", claims);
            const claim = claims.find((claim) => claim.uri === claimToVerify);
            console.log("Found claim:", claim);
            const result = getClaimVerificationStatus(claim);
            console.log("Claim verification status:", result);
            return result;
        })
        .catch((error) => {
            console.error("API request failed:", error);
            console.error("Error details:", {
                status: error.response?.status,
                statusText: error.response?.statusText,
                data: error.response?.data,
                url: requestConfig.url
            });
            throw error;
        });
}

export const getClaimVerificationStatus = (claim: IdVClaim): ClaimVerificationStatus => {
    // If the claim is undefined, it means no verification has been initiated for this claim with Onfido
    if (!claim) {
        return { isVerified: undefined, workflowStatus: undefined };
    }
    return {
        isVerified: claim.isVerified,
        workflowStatus: claim.claimMetadata.onfido_workflow_status
    };
}
