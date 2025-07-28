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
import { Button, Typography, Container, Box } from '@oxygen-ui/react';
import { Footer } from "../components/Footer";
import { NavBar } from "../components/NavBar";
import { useNavigate } from "react-router-dom";

/**
 * Page to display for Invalid System Time Page.
 *
 * @return {React.ReactElement}
 */
export const InvalidSystemTimePage: FunctionComponent = (): ReactElement => {
    const navigate = useNavigate();

    return (
        <>
            <NavBar />
            <Container maxWidth="sm" sx={{ py: 8, minHeight: "70vh" }}>
                <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
                    <Typography
                        variant="h4"
                        align="center"
                        color="error"
                        gutterBottom
                    >
                        Your Clock is Invalid!
                    </Typography>
                    <Typography 
                        variant="body1" 
                        align="center" 
                        color="text.secondary" 
                        sx={{ mt: 2, mb: 4 }}
                    >
                        It looks like your computer&apos;s date and time is incorrect. 
                        Please validate and try again.
                    </Typography>
                    <Button 
                        variant="contained" 
                        onClick={() => navigate("/")}
                        sx={{ mt: 2 }}
                    >
                        Back to home
                    </Button>
                </Box>
            </Container>
            <Footer />
        </>
    );
};
