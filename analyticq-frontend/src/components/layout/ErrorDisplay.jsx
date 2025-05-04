import React from "react";
import {
    Box,
    Alert,
    HStack,
    Flex,
} from "@chakra-ui/react";

/**
 * A component that displays an error message with a title and optional back button.
 *
 * @component
 * @param {Object} props - The component props
 * @param {string} props.title - The title to display above the error message
 * @param {string|ReactNode} props.error - The error message or node to display
 * @param {ReactNode} [props.backButton] - Optional back button component to display below the error
 * @returns {ReactElement} A box containing the error display
 */
const ErrorDisplay = ({ title, error, backButton }) => (
    <Flex
    >
        <Alert.Root
            role="alert"
            aria-live="assertive"
            aria-labelledby="error-title"
            status="error"
            mb={4}
            width="100%"
            height="100%"
             align="center"
            justify="center"
        >
            <Alert.Content textAlign="center">
                <Alert.Indicator />
                <Alert.Title>{title}</Alert.Title>
                <Alert.Description>{error}</Alert.Description>
            </Alert.Content>
            {error}
        </Alert.Root>
        {backButton && (
            <HStack justifyContent="space-between">
                {backButton}
            </HStack>
        )}
    </Flex>
)

export default ErrorDisplay;
