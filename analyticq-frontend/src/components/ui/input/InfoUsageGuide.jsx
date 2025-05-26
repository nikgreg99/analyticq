import React from "react";
import { Box, SimpleGrid, HStack, Text } from "@chakra-ui/react";
import { FaFileArchive, FaGit } from "react-icons/fa";

/**
 * InfoUsageGuide is a React component that displays a guide for repository input methods.
 * It shows two sections in a responsive grid layout:
 * 1. Git Repository section with instructions for Git URL input
 * 2. Local Files section with instructions for file upload
 *
 * The component uses Chakra UI components for styling and layout.
 *
 * @component
 * @returns {JSX.Element} A box containing a grid with usage instructions
 */
const InfoUsageGuide = () => (
  <Box p={4} borderRadius="md" borderWidth="1px" borderColor="gray.200">
    <SimpleGrid columns={{ base: 1, md: 2 }} spacing={4}>
      <Box>
        <HStack spacing={2} mb={1}>
          <FaGit size={12} color="#718096" />
          <Text fontWeight="medium" color="gray.700">
            Git Repository
          </Text>
        </HStack>
        <Text fontSize="sm" color="gray.600" pl={5}>
          Enter Git URL, specify branch (optional), click Start
        </Text>
      </Box>
      <Box>
        <HStack spacing={2} mb={1}>
          <FaFileArchive size={12} color="#718096" />
          <Text fontWeight="medium" color="gray.700">
            Local Files
          </Text>
        </HStack>
        <Text fontSize="sm" color="gray.600" pl={5}>
          Upload .zip/.tar/.gz files, click Start
        </Text>
      </Box>
    </SimpleGrid>
  </Box>
);

InfoUsageGuide.displayName = "InfoUsageGuide";

export default InfoUsageGuide;
