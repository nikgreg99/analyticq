import React, { useMemo } from "react";
import {
  Box,
  Card,
  Flex,
  Heading,
  Text,
  Wrap,
  VisuallyHidden,
} from "@chakra-ui/react";
import { Tooltip } from "../general/Tooltip";
import LegendItem from "./LegendItem";

/**
 * A component that displays the distribution of programming languages in a repository
 * through a horizontal stacked bar chart and a legend.
 *
 * @component
 * @param {Object} props
 * @param {Object} props.languageStats - An object containing language statistics where each key is a language
 *                                      and contains file_count data
 * @param {Object} props.colorMap - An object mapping language names to their corresponding colors
 * @param {string} [props.title="Language Distribution (Files)"] - The title displayed above the chart
 *
 * @returns {JSX.Element} A card containing:
 *                        - A horizontal stacked bar chart showing the proportion of each language
 *                        - Interactive tooltips showing detailed information on hover
 *                        - A legend with language names, file counts and percentages
 *                        - Accessible description for screen readers
 *
 * @example
 * const languageStats = {
 *   JavaScript: { file_count: 50 },
 *   Python: { file_count: 30 }
 * };
 * const colorMap = {
 *   JavaScript: "yellow",
 *   Python: "blue"
 * };
 *
 * <LanguageStatsDistribution
 *   languageStats={languageStats}
 *   colorMap={colorMap}
 *   title="Repository Languages"
 * />
 */
export const LanguageStatsDistribution = ({
  languageStats,
  colorMap,
  title = "Language Distribution (Files)",
}) => {
  const { sortedLanguages } = useMemo(() => {
    const total = Object.values(languageStats).reduce(
      (sum, lang) => sum + lang.file_count,
      0,
    );

    const sorted = Object.entries(languageStats)
      .sort((a, b) => b[1].file_count - a[1].file_count)
      .map(([language, stats]) => ({
        language,
        fileCount: stats.file_count,
        percentage: ((stats.file_count / total) * 100).toFixed(1),
        color: colorMap[language] || "gray",
      }));

    return { sortedLanguages: sorted };
  }, [languageStats, colorMap]);

  // Create accessibility description
  const accessibilityDescription = useMemo(() => {
    return `This chart shows the distribution of programming languages in files: ${sortedLanguages
      .map(
        (item) =>
          `${item.language}: ${item.fileCount} files, ${item.percentage}%`,
      )
      .join(". ")}`;
  }, [sortedLanguages]);

  if (!languageStats || Object.keys(languageStats).length === 0) {
    return (
      <Card.Root
        borderRadius="lg"
        boxShadow="md"
        height="full"
        borderWidth="1px"
      >
        <Card.Body>
          <Text textAlign="center">No language data available</Text>
        </Card.Body>
      </Card.Root>
    );
  }

  return (
    <Card.Root borderRadius="lg" boxShadow="md" height="full" borderWidth="1px">
      <Card.Header pb={2}>
        <Heading size="md" textAlign="center">
          {title}
        </Heading>
      </Card.Header>
      <Card.Body>
        <VisuallyHidden>
          {accessibilityDescription}
        </VisuallyHidden>
        <Box mb={6}>
          <Flex h="8px" borderRadius="full" overflow="hidden">
            {sortedLanguages.map(
              ({ language, fileCount, percentage, color }) => (
                <Tooltip
                  showArrow
                  key={language}
                  content={`${language}: ${fileCount} files (${percentage}%)`}
                  placement="top"
                >
                  <Box
                    h="full"
                    w={`${percentage}%`}
                    transition="all 0.3s"
                    _hover={{
                      transform: "translateY(-2px) scale(1.02)",
                      opacity: 0.9,
                      boxShadow: "sm",
                    }}
                    bg={`${color}.500`}
                    data-testid={`bar-${language}`}
                  />
                </Tooltip>
              ),
            )}
          </Flex>
        </Box>

        <Wrap spacing={3} justify="center">
          {sortedLanguages.map((item) => (
            <LegendItem key={item.language} {...item} />
          ))}
        </Wrap>
      </Card.Body>
    </Card.Root>
  );
};
