import React from "react";
import {
  Card,
  Flex,
  Box,
  Heading,
  Text,
  VStack,
  HStack,
  Badge,
  Spacer,
} from "@chakra-ui/react";
import { ProgessBarLabeled } from "../general/ProgessBarLabeled";
import { formatBytes } from "components/utils/files";
import { Tooltip } from "../general/Tooltip";

/**
 * A component that displays the size distribution of files across different programming languages.
 *
 * @component
 * @param {Object} props
 * @param {Object} props.languageStats - An object containing statistics for each programming language
 *                                      with properties like total_size and file_count
 * @param {Object} props.colorMap - An object mapping language names to their corresponding color schemes
 *
 * @returns {JSX.Element} A card component displaying:
 *                        - Header with language badges for the top 5 languages
 *                        - Body with progress bars showing:
 *                          - Size distribution for top 5 languages
 *                          - Combined size for remaining languages (if any)
 *                        - Each language entry shows:
 *                          - Language name with file count tooltip
 *                          - Total size in bytes
 *                          - Percentage of total size
 *                          - Visual progress bar
 */
export const FileSizeDistribution = ({ languageStats, colorMap }) => {
  const totalSize = Object.values(languageStats).reduce(
    (sum, lang) => sum + lang.total_size,
    0,
  );

  const safePercentage = (size) =>
    totalSize === 0 ? 0 : (size / totalSize) * 100;

  const sortedBySize = Object.entries(languageStats).sort(
    (a, b) => b[1].total_size - a[1].total_size,
  );

  const topLanguages = sortedBySize.slice(0, 5);
  const otherLanguages = sortedBySize.slice(5);
  const otherSize = otherLanguages.reduce(
    (sum, [, stats]) => sum + stats.total_size,
    0,
  );
  const otherPercentage = safePercentage(otherSize);

  return (
    <Card.Root as="section" aria-labelledby="size-distribution-heading">
      <Card.Header as="header">
        <Flex justify="space-between" align="center" width="100%">
          <Heading id="size-distribution-heading" size="md">
            Size Distribution
          </Heading>
          <HStack spacing={2} flexWrap="wrap" justify="flex-end">
            {topLanguages.map(([language]) => (
              <Badge
                key={language}
                colorScheme={colorMap[language]}
                variant="subtle"
                px={2}
                py={1}
                borderRadius="md"
                aria-label={`${language} language badge`}
              >
                {language}
              </Badge>
            ))}
            {otherSize > 0 && (
              <Badge
                colorScheme="gray"
                variant="subtle"
                px={2}
                py={1}
                borderRadius="md"
                aria-label="Other languages badge"
              >
                Others
              </Badge>
            )}
          </HStack>
        </Flex>
      </Card.Header>
      <Card.Body>
        <VStack spacing={4} align="stretch">
          {topLanguages.map(([language, stats]) => {
            const percentage = safePercentage(stats.total_size);

            return (
              <Box
                key={language}
                as="section"
                aria-labelledby={`lang-${language}`}
              >
                <Flex justify="space-between" mb={1} align="center">
                  <Tooltip label={`${stats.file_count} files`} placement="top">
                    <Text
                      id={`lang-${language}`}
                      fontWeight="medium"
                      aria-label={`${language}: ${stats.file_count} files`}
                    >
                      {language}
                    </Text>
                  </Tooltip>
                  <Spacer minWidth={4} />
                  <Text
                    fontSize="sm"
                    color="gray.600"
                    aria-label={`Size ${formatBytes(stats.total_size)}`}
                  >
                    {formatBytes(stats.total_size)}
                  </Text>
                  <Text
                    fontSize="sm"
                    width="60px"
                    textAlign="right"
                    aria-label={`Percentage ${percentage.toFixed(1)}%`}
                  >
                    {percentage.toFixed(1)}%
                  </Text>
                </Flex>
              </Box>
            );
          })}

          {otherSize > 0 && (
            <Box as="section" aria-labelledby="other-languages">
              <Flex justify="space-between" mb={1} align="center">
                <Tooltip
                  label={`${otherLanguages.length} languages`}
                  placement="top"
                >
                  <Text id="other-languages" fontWeight="medium">
                    Others
                  </Text>
                </Tooltip>
                <Spacer minWidth={4} />
                <Text
                  fontSize="sm"
                  color="gray.600"
                  aria-label={`Size ${formatBytes(otherSize)}`}
                >
                  {formatBytes(otherSize)}
                </Text>
                <Text
                  fontSize="sm"
                  width="60px"
                  textAlign="right"
                  aria-label={`Percentage ${otherPercentage.toFixed(1)}%`}
                >
                  {otherPercentage.toFixed(1)}%
                </Text>
              </Flex>
            </Box>
          )}
        </VStack>
      </Card.Body>
    </Card.Root>
  );
};
