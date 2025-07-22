import React from "react";
import { Box, SimpleGrid, HStack, Text } from "@chakra-ui/react";
import { FaFileArchive, FaGit } from "react-icons/fa";
import { UsageItem } from "./UsageItem";

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
  <Box
    p={4}
    borderRadius="md"
    borderWidth="1px"
    borderColor="gray.200"
    role="region"
    aria-labelledby="usage-guide-heading"
  >
    <SimpleGrid columns={{ base: 1, md: 2 }} spacing={4} aria-describedby="git-instructions">
      <UsageItem
        icon={FaGit}
        label="Git Repository"
        description="Enter Git URL, specify branch (optional), click Start"
        aria-describedby="git-instructions"
      />
      <UsageItem
        icon={FaFileArchive}
        label="Local Files"
        description="Upload .zip/.tar/.gz files, click Start"
        aria-describedby="file-instructions"
      />
    </SimpleGrid>
  </Box>
);

InfoUsageGuide.displayName = "InfoUsageGuide";

export default InfoUsageGuide;
