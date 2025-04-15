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
    Spacer
} from "@chakra-ui/react";
import { ProgessBarLabeled } from "./ProgessBarLabeled";
import { formatBytes } from "components/utils/files";
import { Tooltip } from "./tooltip";

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

    const totalSize = Object.values(languageStats)
        .reduce((sum, lang) => sum + lang.total_size, 0);

    const sortedBySize = Object.entries(languageStats)
        .sort((a, b) => b[1].total_size - a[1].total_size);

    const topLanguages = sortedBySize.slice(0, 5);
    const otherLanguages = sortedBySize.slice(5);
    const otherSize = otherLanguages.reduce((sum, [_, stats]) => sum + stats.total_size, 0);
    const otherPercentage = (otherSize / totalSize) * 100;


    return (
        <Card.Root>
            <Card.Header>
                <Flex justify="space-between" align="center" width="100%">
                    <Heading size="md">Size Distribution</Heading>
                    <HStack spacing={2} flexWrap="wrap" justify="flex-end">
                        {topLanguages.map(([language, _]) => (
                            <Badge
                                key={language}
                                colorScheme={colorMap[language]}
                                variant="subtle"
                                px={2}
                                py={1}
                                borderRadius="md"
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
                        const color = colorMap[language];
                        const percentage = (stats.total_size / totalSize) * 100;

                        return (
                            <Box key={language}>
                                <Flex
                                    justify="space-between"
                                    mb={1}
                                    align="center"
                                >
                                    <Tooltip label={`${stats.file_count} files`} placement="top">
                                        <Text fontWeight="medium">{language}</Text>
                                    </Tooltip>
                                    <Spacer minWidth={4} />
                                    <Text fontSize="sm" color="gray.600">
                                        {formatBytes(stats.total_size)}
                                    </Text>
                                    <Text fontSize="sm" width="60px" textAlign="right">
                                        {percentage.toFixed(1)}%
                                    </Text>
                                </Flex>

                                <ProgessBarLabeled
                                    label={`${language} Percentage`}
                                    percentage={percentage}
                                    colorScheme={color}
                                />
                            </Box>
                        );
                    })}

                    {otherSize > 0 && (
                        <Box>
                            <Flex
                                justify="space-between"
                                mb={1}
                                align="center"
                            >
                                <Tooltip label={`${otherLanguages.length} languages`} placement="top">
                                    <Text fontWeight="medium">Others</Text>
                                </Tooltip>
                                <Spacer minWidth={4} />
                                <Text fontSize="sm" color="gray.600">
                                    {formatBytes(otherSize)}
                                </Text>
                                <Text fontSize="sm" width="60px" textAlign="right">
                                    {otherPercentage.toFixed(1)}%
                                </Text>
                            </Flex>

                            <ProgessBarLabeled
                                label="Other Languages Percentage"
                                percentage={otherPercentage}
                                colorScheme="gray"
                            />
                        </Box>
                    )}
                </VStack>
            </Card.Body>
        </Card.Root>
    );
};
