import React from "react";
import { Flex, Text } from "@chakra-ui/react";

/**
 * A responsive row for displaying a label-value pair.
 *
 * @param {Object} props
 * @param {string} props.label - Label text
 * @param {string|React.ReactNode} props.value - Value content
 */
export const InfoRow = ({ label, value }) => {
  return (
    <Flex
      as="div"
      direction={{ base: "column", md: "row" }}
      justify={{ base: "flex-start", md: "space-between" }}
      align={{ base: "flex-start", md: "center" }}
      gap={1}
      py={1}
      wrap="wrap"
    >
      <Text
        as="dt"
        color="whiteAlpha.800"
        fontWeight="semibold"
        fontSize="sm"
        minW={{ base: "100%", md: "120px" }}
        flexShrink={0}
      >
        {label}
      </Text>
      <Text
        as="dd"
        color="whiteAlpha.800"
        fontSize="sm"
        maxW={{ base: "100%", md: "70%" }}
        wordBreak="break-word"
      >
        {value}
      </Text>
    </Flex>
  );
};

InfoRow.displayName = "RepositoryInfoRow";
