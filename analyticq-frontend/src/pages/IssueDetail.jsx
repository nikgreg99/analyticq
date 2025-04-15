import React, { useState, useCallback, useEffect } from "react";
import LoadingSpinner from "components/ui/LoadingSpinner";
import ErrorDisplay from "components/layout/ErrorDisplay";
import { getIssueById } from "services/issueService";
import { useParams, useNavigate } from "react-router-dom";
import BackButton from "components/ui/BackButton";
import {
    Box,
    Flex,
    Heading,
    HStack,
    Badge,
    Stack,
    SimpleGrid,
    Code,
    Text
} from "@chakra-ui/react";
import { updatePageMetadata } from "components/utils/metadata";
import { SEVERITY_COLOR, CONFIDENCE_COLOR } from "components/utils/issues";

/**
 * Renders a detailed view of a security issue.
 *
 * @component
 * @param {Object} props
 * @param {Object} [props.initialIssueData=null] - Initial issue data to display. If not provided, data will be fetched from API.
 *
 * @returns {JSX.Element} A detailed page displaying issue information including:
 *  - Issue ID and location
 *  - Severity and confidence badges
 *  - Metadata (rule ID, file path, line range, creation date)
 *  - Issue message
 *  - Related code snippet
 *
 * @example
 * <IssueDetailPage initialIssueData={issueData} />
 */
export const IssueDetailPage = ({ initialIssueData = null }) => {

    const [issueData, setIssueData] = useState(initialIssueData);
    const [loading, setLoading] = useState(!initialIssueData);
    const [error, setError] = useState(null);
    const { issueId } = useParams();
    const navigate = useNavigate();

    // Update metadata when product data changes
    useEffect(() => {
        // Set initial loading metadata
        updatePageMetadata(
            'Issue loading...',
            'Loading issues information...',
            `/issues/${issueId}`
        );

        // Update with product data once loaded
        if (issueData) {
            updatePageMetadata(
                `Issue ${issueId}`,
                issueId,
                `/issues/${issueId}`
            );
        }
    }, [issueData, issueId]);

    const fetchIssueById = useCallback(async () => {
        try {
            setLoading(true);
            const data = await getIssueById(issueId);
            console.log("Fetched issue data", data);
            setIssueData(data);
            setError(null);
        }
        catch (error) {
            console.error("Error fetching issue with ID", error);
            setError("Error fetch issue with ID. Please try again");
        }
        finally {
            setLoading(false);
        }
    }, [issueId]);

    const handleBackClick = () => {
        navigate("/");
    }

    useEffect(() => {
        if (!initialIssueData) {
            fetchIssueById()
        }
    }, [fetchIssueById, initialIssueData]);


    if (loading) {
        return <LoadingSpinner />
    }

    if (error) {
        return <ErrorDisplay
            title="Issue with Id not found"
            error={error}
            backButton={
                <BackButton onClick={handleBackClick} label="Back to Home Page" />
            }
        />
    }

    return (

        <Box
            maxW="6xl"
            mx="auto"
            p={6}
        >
            <Box
                borderRadius="lg"
                boxShadow="md"
                p={[4, 6]}
                mb={6}
            >
                <Flex
                    direction={["column", "row"]}
                    align={["flex-start", "center"]}
                    justify="space-between"
                    flexWrap="wrap"
                    gap={4}
                >
                    <Heading size="lg" mb={1} color="blackAlpha.800">Issue Details {issueData.id}</Heading>
                    <Text color="gray.600">
                        Found at <strong>{issueData.path}:{issueData.start_line}</strong>
                    </Text>
                    <HStack spacing={3}>
                        <Badge colorPalette={SEVERITY_COLOR[issueData.severity.toUpperCase()]} px={2} py={1} fontSize="0.8em">
                            Severity: {issueData.severity}
                        </Badge>
                        <Badge colorPalette={CONFIDENCE_COLOR[issueData.confidence.toUpperCase()]} px={2} py={1} fontSize="0.8em">
                            Confidence: {issueData.confidence}
                        </Badge>
                    </HStack>
                </Flex>
            </Box>

            <Stack spacing={6}>
                <Box p={4} borderRadius="md" color="blackAlpha.800">
                    <Heading
                        size="sm"
                        mb={2}
                        color="blackAlpha.800"
                        textAlign="center"
                    >
                        Metadata
                    </Heading>
                    <SimpleGrid columns={[1, 2]} spacing={4}>
                        <Box>
                            <Text fontWeight="semibold">Rule ID:</Text>
                            <Text>{issueData.rule_id}</Text>
                        </Box>
                        <Box>
                            <Text fontWeight="semibold">File Path:</Text>
                            <Text>{issueData.path}</Text>
                        </Box>
                        <Box>
                            <Text fontWeight="semibold">Location:</Text>
                            {issueData.start_line && issueData.end_line ? (
                                <Text>
                                    {issueData.start_line === issueData.end_line
                                        ? `Line: ${issueData.start_line}`
                                        : `Lines: ${issueData.start_line}–${issueData.end_line}`}
                                    , Column: {issueData.column ?? 'N/A'}
                                </Text>
                            ) : (
                                <Text>Line/Column information not available</Text>
                            )}
                        </Box>
                        <Box>
                            <Text fontWeight="semibold">Created:</Text>
                            <Text>{new Date(issueData.created_at).toLocaleString()}</Text>
                        </Box>
                    </SimpleGrid>
                </Box>

                <Box p={4} borderRadius="md">
                    <Heading
                        size="sm"
                        mb={2}
                        color="blackAlpha.800"
                        textAlign="center"
                    >Message</Heading>
                    <Text color="gray.700">{issueData.message}</Text>
                </Box>

                <Box p={4} borderRadius="md" color="blackAlpha.800">
                    <Heading
                        size="sm"
                        mb={2}
                        textAlign="center"
                        color="blackAlpha.800"
                    >
                        Code Snippet</Heading>
                    <Code
                        mt={5}
                        display="block"
                        whiteSpace="pre-wrap"
                        p={4}
                        fontFamily="monospace"
                        bg="gray.100"
                        color="blackAlpha.800"
                        overflowX="auto"
                        borderRadius="0 0 md md"
                    >
                        {issueData.code || 'Not present'}
                    </Code>
                </Box>

            </Stack>
        </Box>
    )

}
