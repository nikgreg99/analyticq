import React from "react";
import {
    Box,
    Heading,
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

        <Alert.Root status="info">
            <Alert.Title mt={4} mb={1} fontSize="lg">
                {title}
            </Alert.Title>
            <Alert.Content maxWidth="md">
                {message}
            </Alert.Content>
        </Alert.Root>
    );
};

export default EmptyState;
