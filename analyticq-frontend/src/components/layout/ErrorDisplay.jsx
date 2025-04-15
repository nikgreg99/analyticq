import React from "react";
import {
    Box,
    Heading,
    Alert,
    HStack
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
    <Box p={6}>
        <Heading
            size="lg"
            mb={4}
            textAlign="center" c
            color="blackAlpha.800">
                {title}
        </Heading>
        <Alert.Root status="error" mb={4}>
            {error}
        </Alert.Root>
        {backButton && (
            <HStack justifyContent="space-between">
                {backButton}
            </HStack>
        )}
    </Box>
)

export default ErrorDisplay;
