import React from "react";
import {
    Flex,
    Text,
    useBreakpointValue
} from "@chakra-ui/react";

// Helper component for info rows
export const InfoRow = ({ label, value }) => {

    const isMobile = useBreakpointValue({ base: true, md: false });

    return (
        <Flex
            as="div"
            justifyContent={isMobile ? "flex-start" : "space-between"}
            alignItems={isMobile ? "flex-start" : "center"}
            direction={isMobile ? "column" : "row"}
            gap={1}
            py={1}
        >
            <Text
                color="whiteAlpha.800"
                fontWeight="semibold"
                fontSize="sm"
                minWidth="120px"
                flexShrink={0}
            >
                {label}
            </Text>
            <Text
                color="whiteAlpha.800"
                fontSize="sm"
                maxWidth={isMobile ? "100%" : "70%"}
                wordBreak="break-word"
            >
                {value}
            </Text>
        </Flex>
    )
};
