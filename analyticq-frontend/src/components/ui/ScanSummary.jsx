import React, { useMemo } from "react";
import {
    Box,
    Flex,
    Heading,
    Text,
    Badge,
    Grid,
    Stat,
    VisuallyHidden,
} from "@chakra-ui/react";
import { SeverityCounter } from "./SeverityIssueCounter";
import { getIssueCounts } from "components/utils/issues";
import { MdOutlineInfo } from "react-icons/md";
import { Tooltip } from "./Tooltip";

// Configuration constants
const SEVERITY_WEIGHTS = {
    critical: 10,
    high: 5,
    medium: 2,
    low: 1,
    info: 0,
    unknown: 0,
};

const HEALTH_COLOR_THRESHOLDS = [
    { min: 90, color: "green.500", label: "Good" },
    { min: 70, color: "yellow.500", label: "Fair" },
    { min: 0, color: "red.500", label: "Poor" },
];

const SEVERITY_LEVELS = [
    { label: "Critical", key: "critical" },
    { label: "High", key: "high", },
    { label: "Medium", key: "medium" },
    { label: "Low", key: "low" },
    { label: "Info", key: "info" },
    { label: "Unknown", key: "unknown" },
];

const MAX_SCORE_IMPACT = 100; // Maximum score impact from issues

/**
 * Renders a summary component for scan results displaying health score and issue distribution
 * with enhanced accessibility features
 * @component
 * @param {Object} props - Component props
 * @param {Object} props.scanData - Data containing scan results with issue information
 * @param {Object} props.scanData.issues - Array or collection of issues found in scan
 * @returns {JSX.Element} An accessible Box component containing scan summary information
 */
export const ScanSummary = ({ scanData }) => {

    const issueCounts = getIssueCounts(scanData);
    const totalIssues = Object.values(issueCounts).reduce((sum, count) => sum + count, 0);
    const hasCritical = issueCounts.critical > 0;

    const healthScore = useMemo(() => {
        if (totalIssues === 0) return 100;

        const totalPenalty = Object.entries(SEVERITY_WEIGHTS).reduce(
            (sum, [key, weight]) => sum + (issueCounts[key] * weight),
            0
        );

        // Cap the penalty at MAX_SCORE_IMPACT to ensure the score doesn't go negative
        const cappedPenalty = Math.min(totalPenalty, MAX_SCORE_IMPACT);

        // Calculate score as percentage of remaining "health" after deducting penalties
        const score = Math.max(0, 100 - cappedPenalty);

        return Math.round(score);

    }, [issueCounts, totalIssues]);

    /**
     * Determines the color and label for the health score display based on the score value
     * @returns {Object} The Chakra UI color string and accessibility label
     */
    const getHealthScoreInfo = () => {
        const threshold = HEALTH_COLOR_THRESHOLDS.find(
            ({ min }) => healthScore >= min
        ) || HEALTH_COLOR_THRESHOLDS[HEALTH_COLOR_THRESHOLDS.length - 1];

        return {
            color: threshold.color,
            label: threshold.label
        };
    }

    const healthScoreInfo = getHealthScoreInfo();

    return (
        <Box
            mt={8}
            mb={8}
            p={6}
            borderWidth="1px"
            borderRadius="lg"
            boxShadow="sm"
            role="region"
            aria-label="Scan Results Summary"
        >
            <Flex
                justify="space-between"
                align="center"
                color="blackAlpha.800"
                mb={6}
            >
                <Heading size="md" color="blackAlpha.800" id="scan-summary-heading">
                    Scan Summary
                </Heading>
                {totalIssues > 0 && (
                    <Badge
                        colorScheme={hasCritical ? 'red' : 'blue'}
                        fontSize="sm"
                        px={3}
                        py={1}
                        borderRadius="full"
                        aria-live="polite"
                    >
                        {totalIssues} {totalIssues === 1 ? 'Issue' : 'Issues'} Detected
                    </Badge>
                )}
            </Flex>

            <Grid
                templateColumns={{ base: "1fr", md: "repeat(2, 1fr)" }}
                gap={6}
                mb={6}
                aria-labelledby="scan-summary-heading"
            >
                <Stat.Root
                    p={4}
                    borderRadius="md"
                    boxShadow="sm"
                    borderWidth="1px"
                    role="status"
                    aria-label="Health Score Status"
                >
                    <Flex align="center">
                        <Stat.Label fontSize="sm" color="blackAlpha.800" id="health-score-label">Health Score</Stat.Label>
                        <Tooltip
                            content="The health score is calculated based on the severity of issues found in your codebase. A higher score indicates a healthier codebase."
                            placement="top"
                            showArrow
                            aria-describedby="health-score-label"
                        >
                            <Box as="span" tabIndex={0} aria-label="Health score information" role="button">
                                <MdOutlineInfo color="black" focusable="false" aria-hidden="true" />
                            </Box>
                        </Tooltip>
                    </Flex>
                    <Stat.ValueText
                        fontSize="3xl"
                        color={healthScoreInfo.color}
                        fontWeight="bold"
                        aria-describedby="health-score-description"
                    >
                        {healthScore}/100
                        <VisuallyHidden> - {healthScoreInfo.label} health score</VisuallyHidden>
                    </Stat.ValueText>
                    <Stat.HelpText
                        fontSize="small"
                        mt={1}
                        color="gray.600"
                        id="health-score-description"
                    >
                        {hasCritical
                            ? "Critical issues significantly impact score"
                            : "Based on issue severity distribution"}
                    </Stat.HelpText>
                </Stat.Root>

                <Box role="region" aria-label="Issues by Severity">
                    <Text
                        fontSize="sm"
                        mb={2}
                        fontWeight="medium"
                        color="blackAlpha.800"
                        textAlign="center"
                        marginBottom={4}
                        id="severity-heading"
                    >
                        Issues by Severity
                    </Text>
                    <Flex
                        wrap="wrap"
                        gap={3}
                        align="center"
                        justify={{ base: "center", sm: "flex-start" }}
                        aria-labelledby="severity-heading"
                    >
                        {totalIssues === 0 ? (
                            <Text
                                color="blackAlpha.800"
                                textAlign="center"
                                role="status"
                                aria-live="polite"
                            >
                                No Issues were detected
                            </Text>
                        ) : (
                            SEVERITY_LEVELS.map(({ label, key}) =>
                                issueCounts[key] > 0 && (
                                    <SeverityCounter
                                        key={label}
                                        label={label}
                                        count={issueCounts[key]}
                                        hasCritical={hasCritical}
                                        aria-label={`${issueCounts[key]} ${label} ${issueCounts[key] === 1 ? 'issue' : 'issues'}`}
                                    />
                                )
                            )
                        )}
                    </Flex>
                </Box>
            </Grid>
        </Box>
    );
};
