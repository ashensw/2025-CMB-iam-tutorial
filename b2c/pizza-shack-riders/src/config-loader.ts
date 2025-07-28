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

export interface ConfigInterface {
  clientID: string;
  baseUrl: string;
  signInRedirectURL: string;
  signOutRedirectURL: string;
  userPortalURL: string;
  scope: string[];
  identityVerificationProviderId: string;
}

export const loadConfig = async () => {
  try {
    const response = await fetch(`/runtime-config.json`);
    const runtimeConfig = await response.json();

    return runtimeConfig;
  } catch (error) {
    console.error('Failed to load runtime config', error);
    throw new Error('Failed to load runtime config');
  }
}
