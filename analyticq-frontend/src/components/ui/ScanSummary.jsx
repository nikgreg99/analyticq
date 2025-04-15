import React from "react";
import {
    Box,
    Flex,
    Heading,
    Text,
    Badge,
    Grid,
    Stat,

} from "@chakra-ui/react";
import { SeverityCounter } from "./SeverityIssueCounter";
import { getIssueCounts } from "components/utils/issues";

/**
 * Renders a summary component for scan results displaying health score and issue distribution
 * @component
 * @param {Object} props - Component props
 * @param {Object} props.scanData - Data containing scan results with issue information
 * @param {Object} props.scanData.issues - Array or collection of issues found in scan
 * @returns {JSX.Element} A Box component containing scan summary information including:
 * - Overall health score (0-100)
 * - Total number of issues detected
 * - Distribution of issues by severity level (Critical, High, Medium, Low, Info, Unknown)
 *
 * The component uses a grid layout that adjusts responsively between mobile and desktop views.
 * Health score is calculated based on weighted severity of issues, with color coding for quick assessment.
 * Issues are displayed using severity counters with appropriate color schemes for each severity level.
 */
export const ScanSummary = ({ scanData }) => {

    const issueCounts = getIssueCounts(scanData);
    const totalIssues = Object.values(issueCounts).reduce((sum, count) => sum + count, 0);
    const hasCritical = issueCounts.critical > 0;

    const severityLevels = [
        { label: "Critical", key: "critical", colorScheme: "red" },
        { label: "High", key: "high", colorScheme: "orange" },
        { label: "Medium", key: "medium", colorScheme: "yellow" },
        { label: "Low", key: "low", colorScheme: "green" },
        { label: "Info", key: "info", colorScheme: "blue" },
        { label: "Unknown", key: "unknown", colorScheme: "gray" },
    ];

    /**
     * Calculates a health score based on the severity and number of issues.
     * The score ranges from 0 to 100, where:
     * - 100 represents a perfect score (no issues)
     * - Issues reduce the score based on their severity:
     *   - Critical: -10 points per issue
     *   - High: -5 points per issue
     *   - Medium: -2 points per issue
     *   - Low: -0.5 points per issue
     * The final score is weighted by the total number of issues and cannot go below 0.
     * @returns {number} The calculated health score rounded to the nearest integer
     */
    const calculateHealthScore = () => {
        if (totalIssues === 0) return 100;

        const weighted =
            issueCounts.critical * 10 +
            issueCounts.high * 5 +
            issueCounts.medium * 2 +
            issueCounts.low * 0.5;

        const score = Math.max(0, 100 - (weighted / totalIssues) * 20);
        return Math.round(score);
    }

    const healthScore = calculateHealthScore();

    /**
     * Determines the color for the health score display based on the score value
     * @returns {string} The Chakra UI color string - "green.500" if score >= 90, "red.500" otherwise
     */
    const getHealthScoreColor = () => {
        if (healthScore >= 90) return "green.500";
        return "red.500";
    }

    return (
        <Box
            mb={8}
            p={6}
            borderWidth="1px"
            borderRadius="lg"
            boxShadow="sm"
        >
            <Flex
                justify="space-between"
                align="center"
                color="blackAlpha.800"
                mb={6}
            >
                <Heading size="md">
                    Scan Summary
                </Heading>
                {totalIssues > 0 && (
                    <Badge
                        colorPalette={hasCritical ? 'red' : 'blue'}
                        fontSize="sm"
                        px={3}
                        py={1}
                        borderRadius="full"
                    >
                        {totalIssues} {totalIssues === 1 ? 'Issue' : 'Issues'} Detected
                    </Badge>
                )}
            </Flex>

            <Grid
                templateColumns={{ base: "1fr", md: "1fr 2fr" }}
                gap={6}
                mb={6}
            >
                <Stat.Root
                    p={4}
                    borderRadius="md"
                    boxShadow="sm"
                    borderWidth="1px"
                >
                    <Stat.Label fontSize="sm" color="blackAlpha.800">Health Score</Stat.Label>
                    <Stat.ValueText
                        fontSize="3xl"
                        color={getHealthScoreColor()}
                        fontWeight="bold"
                    >
                        {healthScore}/100
                    </Stat.ValueText>
                    <Stat.HelpText
                        fontSize="small"
                        mt={1}
                        color="gray.600"
                    >Based on issue severity distribution</Stat.HelpText>
                </Stat.Root>

                <Box>
                    <Text
                        fontSize="sm"
                        mb={2}
                        fontWeight="medium"
                        color="blackAlpha.800"
                        textAlign="center"
                        marginBottom={4}
                    >
                        Issues by Severity
                    </Text>
                    <Flex
                        wrap="wrap"
                        gap={3}
                        align="center"
                        justify={{ base: "center", sm: "flex-start" }}
                    >
                        {severityLevels.map(({ label, key, colorScheme }) => (
                            issueCounts[key] > 0 && (
                                <SeverityCounter
                                    key={label}
                                    label={label}
                                    count={issueCounts[key]}
                                    colorScheme={colorScheme}
                                    hasCritical={hasCritical}
                                />
                            )
                        ))}
                    </Flex>
                </Box>
            </Grid>
        </Box>
    )

}
