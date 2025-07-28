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
import { useLocation, useNavigate } from 'react-router-dom';
import { Box, Button, Container, Paper, Typography } from '@oxygen-ui/react';
import ErrorOutlineIcon from '@mui/icons-material/ErrorOutline';
import { Footer } from "../components/Footer";
import { NavBar } from "../components/NavBar";

interface LocationState {
    message?: string;
}

export const GenericErrorPage: React.FC = () => {
    const location = useLocation();
    const navigate = useNavigate();
    const state = location.state as LocationState;
    const errorMessage = state?.message || "An unexpected error occurred.";

    // Split the error message into an array of strings, each representing a paragraph or step
    const errorLines = errorMessage.split('\n').filter((line: string) => line.trim() !== '');

    return (
        <>
            <NavBar />
            <Container maxWidth="md">
                <Paper elevation={3} sx={{ p: 4, mt: 4, mb: 4 }}>
                    <Box display="flex" flexDirection="column" alignItems="center" textAlign="center">
                        <ErrorOutlineIcon sx={{ fontSize: 60, color: 'error.main', mb: 2 }} />
                        <Typography variant="h4" gutterBottom>
                            Oops! Something went wrong.
                        </Typography>
                        <Typography variant="body1" paragraph>
                            We apologize for the inconvenience. Here are the error details:
                        </Typography>
                        <Box sx={{ width: '100%', maxWidth: '80%', textAlign: 'left' }}>
                            {errorLines.map((line: string, index: number) => (
                                <Typography 
                                    key={index} 
                                    variant="body2" 
                                    color="text.secondary" 
                                    paragraph
                                    sx={{ mb: 1 }}
                                >
                                    {line}
                                </Typography>
                            ))}
                        </Box>
                        <Button
                            color="primary" 
                            variant="outlined"
                            onClick={() => navigate("/")}
                            sx={{ mt: 3 }}
                        >
                            Back to Home
                        </Button>
                    </Box>
                </Paper>
            </Container>
            <Footer />
        </>
    );
};
