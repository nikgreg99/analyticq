import React from 'react';
import {
    Box,
    Container,
    Flex,
    Text
} from '@chakra-ui/react';

/**
 * Footer component that displays the copyright information at the bottom of the page
 * @component
 * @returns {JSX.Element} A footer element containing the copyright text
 */
export const Footer = () => {
    return (
        <Box
            as="footer"
            bg="blackAlpha.800"
            py={6}
        >
            <Container maxW="1/3">
                <Flex justify="center" align="center">
                    <Text
                        color="whiteAlpha.800"
                        textAlign="center"
                        fontWeight="medium"
                    >
                        © {new Date().getFullYear()} AnalyticQ Frontend. All rights reserved.
                    </Text>
                </Flex>
            </Container>
        </Box>
    );
};
