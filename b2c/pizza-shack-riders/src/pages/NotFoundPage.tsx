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

import React, { FunctionComponent, ReactElement } from "react";
import { useNavigate } from "react-router-dom";
import { Button, Typography, Container, Box } from '@oxygen-ui/react';
import { Footer } from "../components/Footer";
import { NavBar } from "../components/NavBar";

/**
 * Page to display for 404.
 *
 * @return {React.ReactElement}
 */
export const NotFoundPage: FunctionComponent = (): ReactElement => {
    const navigate = useNavigate();

    return (
        <>
            <NavBar />
            <Container maxWidth="sm" sx={{ py: 8, minHeight: "70vh" }}>
                <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
                    <Typography
                        variant="h4"
                        align="center"
                        color="text.primary"
                        gutterBottom
                    >
                        404: Page Not Found
                    </Typography>
                    <Typography 
                        variant="h6" 
                        align="center" 
                        color="text.secondary" 
                        sx={{ mt: 2, mb: 4 }}
                    >
                        Sorry, the page you are looking for doesn&apos;t exist or has been moved.
                    </Typography>
                    <Button 
                        color="primary" 
                        variant="outlined" 
                        onClick={() => navigate("/")}
                        sx={{ mt: 2 }}
                    >
                        Go back to Home Page
                    </Button>
                </Box>
            </Container>
            <Footer />
        </>
    );
};
