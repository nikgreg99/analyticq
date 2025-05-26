import React, { useState, useCallback, useEffect, useRef } from "react";
import LoadingSpinner from "components/ui/general/LoadingSpinner";
import ErrorDisplay from "components/layout/ErrorDisplay";
import DeleteConfirmationDialog from "components/ui/general/DeleteConfirmationDialog";
import { useParams, useNavigate } from "react-router-dom";
import BackButton from "components/ui/general/BackButton";
import { Toaster } from "components/ui/general/Toaster";
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
  Spacer,
  useBreakpointValue,
} from "@chakra-ui/react";
import { Tooltip } from "components/ui/general/Tooltip";
import { updatePageMetadata } from "components/utils/metadata";
import { useOptimalCharEstimate } from "hooks/useOptimalCharEstimation";
import { SEVERITY_COLOR, CONFIDENCE_COLOR } from "components/utils/issues";
import { IssueMetadataDisplay } from "components/ui/issue/IssueMetadataDisplay";
import { CopyButton } from "components/ui/general/CopyButton";
import ExpandableText from "components/ui/general/ExpandableText";
import { useIssueDetails } from "hooks/useIssueDetails";

export const IssueDetailPage = ({ initialIssueData = null }) => {
  const [deleteModalOpen, setDeleteModalOpen] = useState(false);
  const { issueId } = useParams();
  const navigate = useNavigate();
  const cancelRef = useRef();

  const { issueData, loading, error, deleting, handleDelete } = useIssueDetails(
    issueId,
    initialIssueData,
  );

  const isMobile = useBreakpointValue({ base: true, md: false });
  const optimalChars = useOptimalCharEstimate();

  useEffect(() => {
    updatePageMetadata(
      issueData ? `Issue ${issueId}` : "Issue loading...",
      issueData ? issueId : "Loading issue information...",
      `/issues/${issueId}`,
    );
  }, [issueData, issueId]);

  const handleBackClick = useCallback(() => navigate(-1), [navigate]);

  if (loading) return <LoadingSpinner />;

  if (error) {
    return (
      <ErrorDisplay
        title="Issue with ID not found"
        error={error}
        backButton={
          <BackButton
            onClick={handleBackClick}
            label={isMobile ? "Back" : "Back to Issues"}
          />
        }
      />
    );
  }

  return (
    <Box as="main" maxW="full" mx="auto" px={{ base: 4, md: 8 }} py={6}>
      <Flex mb={6} align="center" justify="space-between" wrap="wrap" gap={4}>
        <Heading
          id="issue-detail-heading"
          size="lg"
          fontWeight="semibold"
          color="blackAlpha.800"
          textAlign="center"
        >
          Issue #{issueData.id} Details
        </Heading>
        <DeleteConfirmationDialog
          isOpenModal={deleteModalOpen}
          setIsOpenModal={setDeleteModalOpen}
          itemName={issueId}
          itemType="issue"
          isLoading={deleting}
          onConfirm={handleDelete}
          cancelRef={cancelRef}
        />
      </Flex>

      <Box borderRadius="xl" boxShadow="lg" p={{ base: 4, md: 6 }}>
        <Stack spacing={8}>
          <Box>
            <Stack spacing={3}>
              <HStack spacing={3} wrap="wrap">
                <Box color="blackAlpha.800">
                  <Flex
                    align="center"
                    gap={2}
                    wrap="wrap"
                    color="blackAlpha.800"
                  >
                    <ExpandableText
                      text={issueData.message}
                      expansableTextColorr="blackAlpha.800"
                      texmaxChars={optimalChars}
                    />
                  </Flex>
                </Box>
                <Tooltip content="Severity" showArrow>
                  <Badge
                    colorPalette={
                      SEVERITY_COLOR[issueData.severity.toUpperCase()]
                    }
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
                <Tooltip content="Confidence" showArrow>
                  <Badge
                    colorPalette={
                      CONFIDENCE_COLOR[issueData.confidence.toUpperCase()]
                    }
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
            </Stack>
            <Spacer mt={6} />
          </Box>

          <Box color="blackAlpha.800">
            <Heading size="md" mb={4}>
              Details
            </Heading>
            <SimpleGrid columns={{ base: 1, md: 2, lg: 3 }} spacing={6}>
              <Box>
                <Text fontWeight="medium" mb={1}>
                  Rule ID
                </Text>
                <Flex align="center" gap={2} wrap="wrap">
                  <Code fontSize="sm" fontFamily="mono" isTruncated>
                    {issueData.rule_id}
                  </Code>
                  <CopyButton value={issueData.rule_id} />
                </Flex>
              </Box>
              <Box gridColumn={{ lg: "span 2" }}>
                <Text fontWeight="medium" mb={1}>
                  File Path
                </Text>
                <Code>
                  <ExpandableText
                    text={issueData.path}
                    expansableTextcolor="whiteAlpha.800"
                    maxChars={optimalChars}
                  />
                </Code>
              </Box>
              <Box>
                <Text fontWeight="medium" mb={1}>
                  Location
                </Text>
                <Code fontSize="sm" fontFamily="mono">
                  Line {issueData.start_line}
                  {issueData.end_line !== issueData.start_line &&
                    issueData.end_line !== 0 &&
                    `-${issueData.end_line}`}
                  {issueData.column && `, Column ${issueData.column}`}
                </Code>
              </Box>
              <Box>
                <Text fontWeight="medium" mb={1}>
                  First Detected
                </Text>
                <Code fontSize="sm" fontFamily="mono">
                  {new Date(issueData.created_at).toLocaleDateString()}
                </Code>
              </Box>
            </SimpleGrid>
          </Box>

          <Box color="blackAlpha.800">
            <Heading size="md" mb={4}>
              Code Snippet
            </Heading>
            <Box
              borderRadius="lg"
              overflowX="auto"
              border="1px solid"
              borderColor="gray.200"
              bg="gray.50"
              role="region"
              aria-label="Code snippet"
            >
              <Code
                display="block"
                p={4}
                whiteSpace="pre"
                fontSize="sm"
                fontFamily="mono"
              >
                {issueData.code || "No code available"}
              </Code>
            </Box>
          </Box>

          {issueData.issue_metadata && (
            <Box color="blackAlpha.800">
              <Heading size="md" mb={4}>
                Additional Context
              </Heading>
              <Box
                borderRadius="lg"
                bg="gray.50"
                p={4}
                border="1px solid"
                borderColor="gray.200"
              >
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

IssueDetailPage.displayName = "IssueDetailPage";
