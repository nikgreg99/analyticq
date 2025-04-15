import React, { useMemo } from "react";
import {
    Box,
    Card,
    SimpleGrid,
    Stat,
    StatGroup,
    Text,
    VStack,
    Heading,
    Flex,
    Badge
} from "@chakra-ui/react"
import { Tooltip } from "./tooltip";
import { formatBytes, getFileName } from "components/utils/files";
import { ProgessBarLabeled } from "./ProgessBarLabeled";

/**
 * A component that displays a summary of excluded and analyzed files in a repository.
 *
 * @component
 * @param {Object} props - The component props
 * @param {Object} props.excludedFiles - Information about excluded files
 * @param {number} props.excludedFiles.total_size - Total size of excluded files in bytes
 * @param {Array} props.excludedFiles.files - Array of excluded file paths
 * @param {number} props.excludedFiles.count - Total count of excluded files
 * @param {number} props.totalScanned - Total size of scanned/analyzed files in bytes
 * @param {string} [props.repoName="cannypot"] - Name of the repository to extract relative paths
 *
 * @returns {JSX.Element} A card containing statistics about analyzed and excluded files,
 * progress bar showing inclusion percentage, and a list of excluded files grouped by filename
 */
export const ExclusionSummary = ({ excludedFiles, totalScanned, repoName = "cannypot" }) => {

    const totalAnalyzed = totalScanned + excludedFiles.total_size;
    const excludedPercentage = (excludedFiles.total_size / totalAnalyzed) * 100;
    const includedPercentage = 100 - excludedPercentage;

    const getRepoPath = (fullPath) => {
        if(repoName && fullPath.includes(repoName)){
            const repoIndex = fullPath.indexOf(repoName);
            return fullPath.substring(repoIndex +  repoName.length).replace(/^\/+/, '')
        }
    }

    const groupedFiles = useMemo(() => {

        if (!excludedFiles.files || excludedFiles.files.length === 0) {
            return [];
        }


        const fileCountMap = {};
        excludedFiles.files.forEach(file => {
            const fileName = getFileName(file);
            fileCountMap[fileName] = fileCountMap[fileName] || {
                fullPath: file,
                count: 0
            };
            fileCountMap[fileName].count++;
        })

        return Object.entries(fileCountMap)
            .map(([fileName, data]) => ({
                fileName,
                fullPath: data.fullPath,
                count: data.count
            }))
            .sort((a, b) => b.count - a.count);

    }, [excludedFiles.files]);

    return (
        <Card.Root
            borderRadius="lg"
            boxShadow="md"
            mb={6}
            mt={3}
        >
            <Card.Body>
                <SimpleGrid
                    columns={{ base: 1, md: 2 }}
                    spacing={6}
                    mb={6}
                >
                    <StatGroup
                        bg="green.50"
                        p={4}
                        borderRadius="lg"
                    >
                        <Stat.Root>
                            <Stat.Label color="blackAlpha.800">Analyzed Files</Stat.Label>
                            <Stat.ValueText color="blackAlpha.800">{formatBytes(totalScanned)}</Stat.ValueText>
                            <Stat.HelpText fontSize="sm" color="blackAlpha.600"> {includedPercentage.toFixed(1)}% of total</Stat.HelpText>
                        </Stat.Root>
                    </StatGroup>

                    <StatGroup
                        bg="red.50"
                        p={4}
                        borderRadius="lg"
                    >
                        <Stat.Root>
                            <Stat.Label color="blackAlpha.800">Excluded Files</Stat.Label>
                            <Stat.ValueText color="blackAlpha.800"> {formatBytes(excludedFiles.total_size)}</Stat.ValueText>
                            <Stat.HelpText fontSize="sm"  color="blackAlpha.600"> {excludedPercentage.toFixed(1)}% of total</Stat.HelpText>
                        </Stat.Root>
                    </StatGroup>
                </SimpleGrid>

                <ProgessBarLabeled
                    label="Included Percentage"
                    value={includedPercentage.toFixed(1)}
                    colorScheme="green"
                />

                <Text
                    textAlign="center"
                    fontSize="sm"
                    fontWeight="bold"
                    mb={4}
                >
                    Total repository size: {formatBytes(totalAnalyzed)}
                </Text>

                {excludedFiles.files && excludedFiles.count > 0 && (
                    <>
                        <Heading
                            size="md"
                            mb={2}
                            alignSelf="center"
                        >
                            Excluded Files {repoName && `(${repoName})`}
                        </Heading>
                        <VStack
                            align="stretch"
                            spacing={2}
                            maxH="200px"
                            overflowY="auto"
                            p={2}
                            borderRadius="md"
                        >
                            {groupedFiles.map((fileData, index) => (
                                <Tooltip
                                    key={index}
                                    content={getRepoPath(fileData.fullPath)}
                                    placement="top"
                                    hasArrow
                                >
                                    <Flex
                                        justify="space-between"
                                        align="center"
                                        py={1}
                                        px={2}
                                        _hover={{ bg: "transparent" }}
                                    >
                                        <Text fontSize="sm" noOfLines={1} maxW="80%">
                                            {fileData.fileName}
                                        </Text>
                                        {fileData.count > 1 && (
                                            <Badge colorPalette="whiteAlpha" borderRadius="full">
                                                 {fileData.count}×
                                            </Badge>
                                        )}
                                    </Flex>
                                </Tooltip>
                            ))}
                        </VStack>
                        <Box textAlign="center" mt={2}>
                            <Text fontSize="xs">
                                Showing {groupedFiles.length} unique files (total: {excludedFiles.count})
                            </Text>
                        </Box>
                    </>
                )}

            </Card.Body>
        </Card.Root>
    );
}
