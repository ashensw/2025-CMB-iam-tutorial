import React from "react";
import { Typography, Container, Box, Link } from '@oxygen-ui/react';
import { Footer } from "../components/Footer";
import { NavBar } from "../components/NavBar";

export const handleMissingIdvpId = () => {
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
                        Identity Verification Provider ID Required
                    </Typography>
                    <Typography 
                        variant="body1" 
                        align="center" 
                        color="text.secondary" 
                        sx={{ mt: 2, mb: 4 }}
                    >
                        Please open &quot;public/runtime-config.json&quot; file using an editor, and add
                        the <code>identityVerificationProviderId</code> value with the configured Onfido identity verification provider&apos;s ID.
                    </Typography>
                    <Typography variant="body2" align="center">
                        Visit the{' '}
                        <Link 
                            href="https://github.com/wso2-extensions/identity-verification-onfido/blob/main/docs/config.md#configuring-onfido-identity-verification-provider-in-wso2-identity-server-console"
                            target="_blank"
                            rel="noopener noreferrer"
                        >
                            README
                        </Link>
                        {' '}for more details.
                    </Typography>
                </Box>
            </Container>
            <Footer />
        </>
    );
}

export const handleMissingClientId = () => {
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
                        Client ID Required
                    </Typography>
                    <Typography 
                        variant="body1" 
                        align="center" 
                        color="text.secondary" 
                        sx={{ mt: 2, mb: 4 }}
                    >
                        Please open &quot;public/runtime-config.json&quot; file using an editor, and add
                        the <code>clientID</code> value with the registered application&apos;s client ID.
                    </Typography>
                    <Typography variant="body2" align="center">
                        Visit the{' '}
                        <Link 
                            href="https://github.com/wso2-extensions/identity-verification-onfido/blob/main/samples/react-sample-app/README.md"
                            target="_blank"
                            rel="noopener noreferrer"
                        >
                            README
                        </Link>
                        {' '}for more details.
                    </Typography>
                </Box>
            </Container>
            <Footer />
        </>
    );
}
