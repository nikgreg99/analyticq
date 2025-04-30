import React from "react";
import {
    Box,
    Alert
} from "@chakra-ui/react";

/**
 * A component that displays an empty state message with a title and alert.
 *
 * @component
 * @param {Object} props - The component props
 * @param {string} props.title - The main heading text to display
 * @param {string} props.message - The message to display in the alert description
 * @returns {JSX.Element} A box containing a heading and an error alert
 */
const EmptyState = ({ title, message }) => {
    return (
        <Box
            p={6}
            maxW="md"
            textAlign="center"
        >
            <Alert.Root
                status="info"
                title={title}
                role="alert" // Ensure the alert is announced immediately
                aria-live="assertive" // Ensure screen readers announce this content as soon as it appears
                aria-atomic="true"
            >
                <Alert.Indicator />
                <Alert.Content maxWidth="md">
                    <Alert.Title>{title}</Alert.Title>
                    <Alert.Description>{message}</Alert.Description>
                </Alert.Content>
            </Alert.Root>
        </Box>
    );
};

export default EmptyState;
