import React from "react";
import {
    Box,
    Text
} from "@chakra-ui/react";

/**
 * A component that displays a counter with severity-based styling.
 * @component
 * @param {Object} props - The component props
 * @param {string} props.label - The text label to display above the count
 * @param {number} props.count - The numeric value to display
 * @param {('red'|'orange'|'yellow'|'green'|'blue')} props.colorScheme - The color scheme to use for styling
 * @param {boolean} props.hasCritical - Whether critical severity is present (affects width calculation)
 * @returns {JSX.Element} A box containing the label and count with severity-based styling
 */
export const SeverityCounter = ({ label, count, colorScheme, hasCritical }) => {

    const getBackgroundSeverityColor = () => {
        if (count === 0) return "gray.50";
        switch (colorScheme) {
            case "red": return "red.100";
            case "orange": return "orange.50";
            case "yellow": return "yellow.50";
            case "green": return "green.50";
            case "blue": return "blue.50";
            default: return "gray.50";
        }
    }

    const getTextSeverityColor = () => {
        if (count === 0) return "gray.600";
        switch (colorScheme) {
            case "red": return "red.700";
            case "orange": return "orange.600";
            case "yellow": return "yellow.600";
            case "green": return "green.600";
            case "blue": return "blue.600";
            default: return "gray.600";
        }
    }

    return (
        <Box
            p={4}
            bg={getBackgroundSeverityColor()}
            borderRadius="md"
            textAlign="center"
            width={{ base: "100%", sm: "45%", md: hasCritical ? "19%" : "22%" }}
        >
            <Text fontSize="sm" color={getTextSeverityColor()}>{label}</Text>
            <Text
                fontSize="2xl"
                fontWeight="bold"
                color={getTextSeverityColor()}
            >
                {count}
            </Text>
        </Box>
    )

}
