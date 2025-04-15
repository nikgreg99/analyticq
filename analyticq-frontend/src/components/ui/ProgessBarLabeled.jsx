import React from "react"
import {
    Box,
    Progress,
    HStack
} from "@chakra-ui/react";

/**
 * A labeled progress bar component with percentage display
 * @component
 * @param {Object} props - Component props
 * @param {string} props.label - Text label for the progress bar
 * @param {number} props.percentage - Progress percentage value (0-100)
 * @param {string} props.colorScheme- Color scheme for progress bar
 * @returns {JSX.Element} A progress bar with label and percentage display
 */
export const ProgessBarLabeled = ({ label, percentage, colorScheme = "" }) => {
    <Box
        position="relative"
        mb={4}
    >
        < Progress.Root
            maxW="sm"
            borderRadius="full"
            size="md"
            flex="1"
            mr={2}
            colorPalette={colorScheme ? colorScheme : null}
        >
            <HStack gap={5}>
                <Progress.Label>{label}</Progress.Label>
                <Progress.Track flex="1">
                    <Progress.Range />
                </Progress.Track>
                <Progress.ValueText>{percentage}%</Progress.ValueText>
            </HStack>
        </Progress.Root>
    </Box>

}
