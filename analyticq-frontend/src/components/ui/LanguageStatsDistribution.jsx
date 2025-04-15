import React from "react";
import {
  Box,
  Card,
  Flex,
  Heading,
  HStack,
  Text,
  Wrap,
  WrapItem,
} from "@chakra-ui/react";
import { Tooltip } from "./tooltip";

/**
 * A component that displays the distribution of programming languages in a project.
 * Shows both a visual bar chart and a legend with detailed statistics.
 *
 * @component
 * @param {Object} props - The component props
 * @param {Object} props.languageStats - An object containing language statistics where:
 *   @param {Object} props.languageStats[language] - Statistics for each language
 *   @param {number} props.languageStats[language].file_count - Number of files for the language
 * @param {Object} props.colorMap - An object mapping language names to color schemes
 *   @param {string} props.colorMap[language] - Color scheme name for each language
 *
 * @returns {JSX.Element} A card containing a horizontal stacked bar chart showing language distribution
 *                       and a legend with detailed statistics for each language
 *
 * @example
 * const stats = {
 *   "JavaScript": { file_count: 50 },
 *   "Python": { file_count: 30 }
 * };
 * const colors = {
 *   "JavaScript": "yellow",
 *   "Python": "blue"
 * };
 *
 * <LanguageDistribution languageStats={stats} colorMap={colors} />
 */
export const LanguageStatsDistribution = ({ languageStats, colorMap }) => {

  const totalFiles = Object.values(languageStats)
    .reduce((sum, lang) => sum + lang.file_count, 0);

  const sortedLanguages = Object.entries(languageStats)
    .sort((a, b) => b[1].file_count - a[1].file_count);


  return (
    <Card.Root
      borderRadius="lg"
      boxShadow="md"
      height="full"
      borderWidth="1px"
    >
      <Card.Header pb={2}>
        <Heading size="md" textAlign="center">Language Distribution (Files)</Heading>
      </Card.Header>
      <Card.Body>
        <Box mb={6}>
          <Flex
            h="8px"
            borderRadius="full"
            overflow="hidden"
          >
            {sortedLanguages.map(([language, stats]) => {
              const width = (stats.file_count / totalFiles) * 100;
              const color = colorMap[language];
              return (
                <Tooltip
                  showArrow
                  key={language}
                  content={`${language}: ${stats.file_count} files (${width.toFixed(1)}%)`}
                >
                  <Box
                    h="full"
                    w={`${width}%`}
                    transition="all 0.2s"
                    _hover={{ transform: "translateY(-2px)", opacity: 0.8 }}
                    bg={`${color}.500`}
                  />
                </Tooltip>
              );
            })}
          </Flex>
        </Box>

        <Wrap spacing={3} justify="center">
          {sortedLanguages.map(([language, stats]) => {
            const color = colorMap[language];
            const percentage = ((stats.file_count / totalFiles) * 100).toFixed(1);

            return (
              <WrapItem key={language}>
                <HStack spacing={2} align="center">
                  <Box
                    w="12px"
                    h="12px"
                    borderRadius="sm"
                    bg={`${color}.500`}
                    flexShrink={0}
                  />
                  <Text fontSize="sm" fontWeight="medium">
                    {language}
                  </Text>
                  <Text fontSize="xs" color="gray.500">
                    ({stats.file_count} | {percentage}%)
                  </Text>
                </HStack>
              </WrapItem>
            );
          })}
        </Wrap>
      </Card.Body>
    </Card.Root>
  );
};
