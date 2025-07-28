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

import React, { FunctionComponent, ReactElement, useState } from "react";
import { useAuthContext } from "@asgardeo/auth-react";
import { Container, Box, Typography, Button } from "@mui/material";
import { Footer } from "../components/Footer";
import { NavBar } from "../components/NavBar";

/**
 * Page to display Authentication Failure Page.
 *
 * @param {AuthenticationFailureInterface} props - Props injected to the component.
 *
 * @return {React.ReactElement}
 */
export const AuthenticationFailurePage: FunctionComponent = (): ReactElement => {

    const { signIn } = useAuthContext();
    const [ hasAuthenticationErrors, setHasAuthenticationErrors ] = useState<boolean>(false);

    const handleLogin = () => {
        signIn()
            .catch(() => setHasAuthenticationErrors(true));
    };

    return (
        <>
            <NavBar />
            <Container maxWidth="sm" sx={{ py: 8, minHeight: "70vh" }}>
                <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
                    <Typography variant="h4" align="center" color="error" gutterBottom>
                        Authentication Error!
                    </Typography>
                    <Typography variant="body1" align="center" sx={{ mb: 4 }}>
                        Please check application configuration and try login again.
                    </Typography>
                    <Button 
                        variant="contained" 
                        color="primary" 
                        onClick={handleLogin}
                        disabled={hasAuthenticationErrors}
                    >
                        Login
                    </Button>
                </Box>
            </Container>
            <Footer />
        </>
    );
};
