import React from "react";
import {
    Alert,
    Flex,
    CloseButton
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
        <Flex
            p={6}
            textAlign="center"
            width="100%"
            height="100%"
            align="center"
            justify="center"
        >
            <Alert.Root
                status="info"
                title={title}
                role="alert" // Ensure the alert is announced immediately
                aria-live="assertive" // Ensure screen readers announce this content as soon as it appears
                aria-atomic="true"
                 width="100%"
            >
                <Alert.Indicator />
                <Alert.Content  textAlign="center">
                    <Alert.Title>{title}</Alert.Title>
                    <Alert.Description>{message}</Alert.Description>
                </Alert.Content>
                <CloseButton pos="relative" top="-2" insetEnd="-2" />
            </Alert.Root>
        </Flex>
    );
};

export default EmptyState;
