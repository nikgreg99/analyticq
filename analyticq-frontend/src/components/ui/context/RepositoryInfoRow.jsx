import React from "react";
import {
  Flex,
  Text,
  Icon
}
  from "@chakra-ui/react";

/**
 * A responsive row for displaying a label-value pair.
 *
 * @param {Object} props
 * @param {string} props.label - Label text
 * @param {string|React.ReactNode} props.value - Value content
 */
export const InfoRow = ({ label, value, icon = null }) => {
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
      <Flex
        align="center"
        gap={2}
        minW={{ base: "100%", md: "40%" }}
        flexShrink={0}
      >
        {icon && (
          <Icon
            as={icon}
            boxSize={4}
            mr={2}
            flexShrink={0}
          />
        )}
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
      </Flex>

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
