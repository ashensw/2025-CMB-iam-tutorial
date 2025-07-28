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

// Response interface for identity verification
export interface IdVResponseInterface {
    id: string;
    claims: IdVClaim[];
}

// Individual claim interface
export interface IdVClaim {
    id: string;
    uri: string;
    isVerified: boolean;
    claimMetadata: ClaimMetadata;
}

// Claim metadata interface
export interface ClaimMetadata {
    onfido_applicant_id: string;
    onfido_workflow_run_id: string;
    onfido_workflow_status: WorkflowStatus;
    sdk_token?: string;
}

// Verification workflow status interface
export interface ClaimVerificationStatus {
    isVerified: boolean | undefined;
    workflowStatus: WorkflowStatus | undefined;
}

// Onfido SDK flow status enum
export enum SdkFlowStatus {
    INITIATED = "INITIATED",
    COMPLETED = "COMPLETED",
    REINITIATED = "REINITIATED"
}

// Workflow status enum
export enum WorkflowStatus {
    PROCESSING = 'processing',
    AWAITING_INPUT = 'awaiting_input',
    APPROVED = 'approved',
    DECLINED = 'declined',
    REVIEW = 'review',
    ABANDONED = 'abandoned',
    ERROR = 'error'
}
