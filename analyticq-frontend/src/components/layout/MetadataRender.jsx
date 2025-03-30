import React from "react";
import {
    Box,
    Text,
    VStack,
    Separator
    } from "@chakra-ui/react";

export const MetadataRenderer = ({ metadata, title = "Metadata" }) => {

    if (!metadata || Object.keys(metadata).length === 0) {
        return (
            <>
                return <Text color="blackAlpha.800">No metadata available</Text>;
            </>
        )
    }

    return (
        <Box p={4} borderRadius="md" bg="gray.50" borderWidth={1} width="full" color="blackAlpha.800">
            <Text fontWeight="bold" mb={2}>{title}:</Text>
            <VStack align="start" spacing={2}>
                {Object.entries(metadata).map(([key, value]) => (
                    <Box key={key} width="full">
                        <Text fontWeight="semibold">{key}:</Text>
                        <Text>{typeof value === "object" ? JSON.stringify(value, null, 2) : value}</Text>
                        <Separator/>
                    </Box>
                ))}
            </VStack>
        </Box>
    );
};
