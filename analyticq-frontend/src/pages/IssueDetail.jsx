import React, { useState, useCallback, useEffect, useRef } from "react";
import LoadingSpinner from "components/ui/LoadingSpinner";
import ErrorDisplay from "components/layout/ErrorDisplay";
import DeleteConfirmationDialog from "components/ui/DeleteConfirmationDialog";
import { getIssueById, deleteIssue } from "services/issueService";
import { useParams, useNavigate } from "react-router-dom";
import BackButton from "components/ui/BackButton";
import { Toaster, toaster } from "components/ui/Toaster";
import {
    Box,
    Flex,
    Heading,
    HStack,
    Badge,
    Stack,
    SimpleGrid,
    Code,
    Text,
    Spacer
} from "@chakra-ui/react";
import { Tooltip } from "components/ui/Tooltip";
import { updatePageMetadata } from "components/utils/metadata";
import { SEVERITY_COLOR, CONFIDENCE_COLOR } from "components/utils/issues";
import { IssueMetadataDisplay } from "components/ui/IssueMetadataDisplay";
import { getFileName } from "components/utils/files";

export const IssueDetailPage = ({ initialIssueData = null }) => {
    const [issueData, setIssueData] = useState(initialIssueData);
    const [loading, setLoading] = useState(!initialIssueData);
    const [error, setError] = useState(null);
    const [deleteModalOpen, setDeleteModalOpen] = useState(false);
    const [deleting, setDeleting] = useState(false);
    const { issueId } = useParams();
    const navigate = useNavigate();
    const cancelRef = useRef();

    useEffect(() => {
        updatePageMetadata(
            issueData ? `Issue ${issueId}` : 'Issue loading...',
            issueData ? issueId : 'Loading issue information...',
            `/issues/${issueId}`
        );
    }, [issueData, issueId]);

    const fetchIssueById = useCallback(async () => {
        try {
            setLoading(true);
            const data = await getIssueById(issueId);
            setIssueData(data);
            setError(null);
        } catch (error) {
            console.error("Error fetching issue with ID", error);
            setError("Error fetching issue with ID. Please try again.");
        } finally {
            setLoading(false);
        }
    }, [issueId]);

    const handleDeleteIssue = useCallback(async () => {
        try {
            setDeleting(true);
            await deleteIssue(issueId);
            navigate("/", { replace: true });
            toaster.create({
                title: 'Issue Deleted',
                description: `Issue ${issueId} has been successfully deleted`,
                type: "success",
                duration: 5000
            });
        } catch (error) {
            console.error("Error deleting issue", error);
            toaster.create({
                title: 'Error Deleting Issue',
                description: "There was an error deleting the issue. Please try again.",
                type: "error",
                duration: 5000
            });
        } finally {
            setDeleting(false);
            setDeleteModalOpen(false);
        }
    }, [issueId, navigate]);

    const handleBackClick = () => navigate("/");

    useEffect(() => {
        if (!initialIssueData) {
            fetchIssueById();
        }
    }, [fetchIssueById, initialIssueData]);

    if (loading) return <LoadingSpinner />;

    if (error) {
        return (
            <ErrorDisplay
                title="Issue with ID not found"
                error={error}
                backButton={<BackButton onClick={handleBackClick} label="Back to Home Page" />}
            />
        );
    }

    return (
        <Box as="main" maxW="6xl" mx="auto" p={{ base: 4, md: 8 }}>
            <Flex mb={6} align="center" justify="space-between" color="gray.600">
                <Heading id="issue-detail-heading" size="xl" fontWeight="semibold">
                    Issue {issueData.id}
                </Heading>
                <DeleteConfirmationDialog
                    isOpenModal={deleteModalOpen}
                    setIsOpenModal={setDeleteModalOpen}
                    itemName={issueId}
                    itemType="issue"
                    isLoading={deleting}
                    onConfirm={handleDeleteIssue}
                    cancelRef={cancelRef}
                />
            </Flex>

            <Box borderRadius="xl" boxShadow="lg" p={{ base: 4, md: 8 }}>
                <Stack spacing={10}>
                    {/* Header Section */}
                    <Box>
                        <Flex justify="space-between" direction={{ base: 'column', md: 'row' }} gap={4}>
                            <Box color="blackAlpha.800">
                                <Text fontSize="lg" mb={1}>
                                    {getFileName(issueData.path)}
                                    <Text as="span" fontWeight="semibold" ml={1}>:{issueData.start_line}</Text>
                                </Text>
                                <Heading as="h2" size="lg">{issueData.message}</Heading>
                            </Box>
                            <HStack spacing={3} align="start">
                                <Tooltip
                                    content="Severity"
                                    showArrow
                                >
                                    <Badge
                                        colorPalette={SEVERITY_COLOR[issueData.severity.toUpperCase()]}
                                        px={3}
                                        py={1}
                                        fontSize="sm"
                                        borderRadius="full"
                                        textTransform="capitalize"
                                        cursor="help"
                                    >
                                        {issueData.severity}
                                    </Badge>
                                </Tooltip>
                                <Tooltip
                                    content="Confidence"
                                    showArrow
                                >
                                    <Badge
                                        colorPalette={CONFIDENCE_COLOR[issueData.confidence.toUpperCase()]}
                                        px={3}
                                        py={1}
                                        fontSize="sm"
                                         borderRadius="full"
                                         textTransform="capitalize"
                                         cursor="help"
                                    >
                                        {issueData.confidence}
                                    </Badge>
                                </Tooltip>

                            </HStack>
                        </Flex>
                        <Spacer mt={6} />
                    </Box>

                    {/* Metadata Section */}
                    <Box color="blackAlpha.800">
                        <Heading size="md" mb={4}>Details</Heading>
                        <SimpleGrid columns={{ base: 1, md: 2, lg: 3 }} spacing={6}>
                            <Box>
                                <Text fontWeight="medium" mb={1}>Rule ID</Text>
                                <Text fontSize="sm" fontFamily="mono" isTruncated>{issueData.rule_id}</Text>
                            </Box>
                            <Box gridColumn={{ lg: "span 2" }}>
                                <Text fontWeight="medium" mb={1}>File Path</Text>
                                <Text fontSize="sm" fontFamily="mono" whiteSpace="pre-wrap">{issueData.path}</Text>
                            </Box>
                            <Box>
                                <Text fontWeight="medium" mb={1}>Location</Text>
                                <Text fontSize="sm" fontFamily="mono">
                                    Line {issueData.start_line}
                                    {issueData.end_line !== issueData.start_line && issueData.end_line !== 0 && `-${issueData.end_line}`}
                                    {issueData.column && `, Column ${issueData.column}`}
                                </Text>
                            </Box>
                            <Box>
                                <Text fontWeight="medium" mb={1}>First Detected</Text>
                                <Text fontSize="sm" fontFamily="mono">
                                    {new Date(issueData.created_at).toLocaleDateString()}
                                </Text>
                            </Box>
                        </SimpleGrid>
                    </Box>

                    {/* Code Snippet Section */}
                    <Box color="blackAlpha.800">
                        <Heading size="md" mb={4}>Code Snippet</Heading>
                        <Box borderRadius="lg" overflow="auto" border="1px solid" borderColor="gray.200" bg="gray.50" role="region" aria-label="Code snippet">
                            <Code display="block" p={4} whiteSpace="pre" fontSize="sm" fontFamily="mono">
                                {issueData.code || 'No code available'}
                            </Code>
                        </Box>
                    </Box>

                    {/* Additional Metadata */}
                    {issueData.issue_metadata && (
                        <Box color="blackAlpha.800">
                            <Heading size="md" mb={4}>Additional Context</Heading>
                            <Box borderRadius="lg" bg="gray.50" p={4} border="1px solid" borderColor="gray.200">
                                <IssueMetadataDisplay metadata={issueData.issue_metadata} />
                            </Box>
                        </Box>
                    )}
                </Stack>
                <Toaster />
            </Box>
        </Box>
    );
};
