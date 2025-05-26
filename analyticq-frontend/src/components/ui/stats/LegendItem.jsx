import React from "react";
import { Box, HStack, WrapItem, Text } from "@chakra-ui/react";

/**
 * A component that renders a legend item for statistical visualization.
 *
 * @component
 * @param {Object} props - The component props
 * @param {string} props.language - The programming language name to display
 * @param {number} props.fileCount - The number of files for this language
 * @param {number} props.percentage - The percentage this language represents
 * @param {string} props.color - The color theme to use for the legend marker
 * @returns {JSX.Element} A legend item with a colored box, language name, and stats
 */
const LegendItem = ({ language, fileCount, percentage, color }) => (
  <WrapItem>
    <HStack spacing={2} align="center">
      <Box
        w="12px"
        h="12px"
        borderRadius="sm"
        bg={`${color}.500`}
        flexShrink={0}
        aria-hidden="true"
      />
      <Text fontSize="sm" fontWeight="medium">
        {language}
      </Text>
      <Text fontSize="xs" color="gray.600">
        ({fileCount} | {percentage}%)
      </Text>
    </HStack>
  </WrapItem>
);

export default React.memo(LegendItem);
