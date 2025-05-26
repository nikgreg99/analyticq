import React, { memo } from "react";
import {
  Card,
  SimpleGrid,
  Stat,
  Heading,
  VStack,
  Separator,
  Text,
  Box,
} from "@chakra-ui/react";
import { formatBytes, getFileName } from "components/utils/files";
import { ProgessBarLabeled } from "../general/ProgessBarLabeled";

/**
 * A card component that displays statistics about a programming language.
 *
 * @component
 * @param {Object} props - The component props
 * @param {string} props.language - The name of the programming language
 * @param {Object} props.stats - Statistics about the language
 * @param {number} props.stats.file_count - Number of files in this language
 * @param {number} props.stats.total_size - Total size of files in bytes
 * @param {number} props.stats.percentage_files - Percentage of files in this language
 * @param {Object} [props.stats.largest_file] - Information about the largest file
 * @param {string} props.stats.largest_file.path - Path to the largest file
 * @param {number} props.stats.largest_file.size - Size of the largest file in bytes
 * @param {Object} props.stats.smallest_file - Information about the smallest file
 * @param {string} props.stats.smallest_file.path - Path to the smallest file
 * @param {number} props.stats.smallest_file.size - Size of the smallest file in bytes
 * @param {Object} props.colorScheme - Color scheme for the card styling
 * @returns {JSX.Element} A card displaying language statistics
 */
export const LanguageStatsCard = memo(({ language, stats, colorScheme }) => {
  return (
    <Card.Root
      borderRadius="lg"
      boxShadow="md"
      transition="transform 0.2s"
      _hover={{ transform: "translateY(-5px)" }}
    >
      <Card.Header
        pb={0}
        alignItems="center"
        aria-label={`Statistics for ${language} programming language`}
      >
        <Heading size="md" color={`${colorScheme}.500`}>
          {language}
        </Heading>
      </Card.Header>
      <Card.Body>
        <SimpleGrid columns={2} spacing={4} mb={4}>
          <Stat.Root>
            <Stat.Label fontSize="xs">Files</Stat.Label>
            <Stat.ValueText fontSize="lg">{stats.file_count}</Stat.ValueText>
          </Stat.Root>
          <Stat.Root>
            <Stat.Label>Total Size</Stat.Label>
            <Stat.ValueText fontSize="lg">
              {formatBytes(stats.total_size)}
            </Stat.ValueText>
          </Stat.Root>
        </SimpleGrid>

        {stats.largest_file || stats.smallest_file ? (
          <>
            <Separator my={4} />
            <VStack align="start" spacing={2}>
              {stats.largest_file && (
                <Box
                  display="flex"
                  flexDirection="column"
                  alignItems="flex-start"
                >
                  <Text fontSize="sm" fontWeight="bold">
                    Largest File
                  </Text>
                  <Text fontSize="sm" title={stats.largest_file.path}>
                    {getFileName(stats.largest_file.path)} (
                    {formatBytes(stats.largest_file.size)})
                  </Text>
                </Box>
              )}

              {stats.smallest_file && (
                <Box
                  display="flex"
                  flexDirection="column"
                  alignItems="flex-start"
                  mt={2}
                >
                  <Text fontSize="sm" fontWeight="bold">
                    Smallest File
                  </Text>
                  <Text fontSize="sm" title={stats.smallest_file.path}>
                    {getFileName(stats.smallest_file.path)} (
                    {formatBytes(stats.smallest_file.size)})
                  </Text>
                </Box>
              )}
            </VStack>
          </>
        ) : (
          <Text fontSize="sm" color="gray.500">
            No file size data available for this language.
          </Text>
        )}
      </Card.Body>
    </Card.Root>
  );
});
