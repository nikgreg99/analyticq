import React, { useState, useCallback, useEffect, useRef } from "react";
import LoadingSpinner from "components/ui/general/LoadingSpinner";
import ErrorDisplay from "components/layout/ErrorDisplay";
import DeleteConfirmationDialog from "components/ui/general/DeleteConfirmationDialog";
import { useParams, useNavigate, useSearchParams } from "react-router-dom";
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
  Button,
  VStack
} from "@chakra-ui/react";
import { Tooltip } from "components/ui/general/Tooltip";
import { updatePageMetadata } from "components/utils/metadata";
import { useOptimalCharEstimate } from "hooks/useOptimalCharEstimation";
import { SEVERITY_COLOR, CONFIDENCE_COLOR } from "components/utils/issues";
import { IssueMetadataDisplay } from "components/ui/issue/IssueMetadataDisplay";
import { CopyButton } from "components/ui/general/CopyButton";
import ExpandableText from "components/ui/general/ExpandableText";
import { useIssueDetails } from "hooks/useIssueDetails";

// Helper component for handling long code snippets
const CodeSnippetDisplay = ({ code, maxLines = 20 }) => {
  const [isExpanded, setIsExpanded] = useState(false);


  const lines = code.split('\n');
  const shouldTruncate = lines.length > maxLines;
  const displayCode = shouldTruncate && !isExpanded
    ? lines.slice(0, maxLines).join('\n') + '\n...'
    : code;

  return (
    <Box>
      <Box
        borderRadius="lg"
        overflowX="auto"
        border="1px solid"
        borderColor="gray.200"
        bg="gray.50"
        role="region"
        aria-label="Code snippet"
        position="relative"
      >
        <Code
          display="block"
          p={4}
          whiteSpace="pre"
          fontSize="sm"
          fontFamily="mono"
          maxHeight={isExpanded ? "none" : "400px"}
          overflow="hidden"
          scrollBehavior="auto"
        >
          {displayCode || "No code available"}
        </Code>

        {shouldTruncate && (
          <Flex
            position="absolute"
            bottom={0}
            right={0}
            left={0}
            bg="linear-gradient(transparent, gray.50)"
            p={2}
            justify="center"
          >
            <Button
              size="sm"
              margin="-1"
              variant="plain"
              onClick={() => setIsExpanded(!isExpanded)}
            >
              {isExpanded
                ? `Show Less (${maxLines} lines)`
                : `Show All (${lines.length} lines)`
              }
            </Button>
          </Flex>
        )}
      </Box>
    </Box>
  );
};

// Enhanced path display with better truncation
const PathDisplay = ({ path, maxLength = 30 }) => {
  const [showFull, setShowFull] = useState(false);

  const shouldTruncate = path.length > maxLength;
  const displayPath = path || "No path available";

  if (!shouldTruncate) {
    return (
      <>
        <Code
          fontSize="sm"
          fontFamily="mono"
          aria-label={`File path: ${displayPath}`}
          role="text"
        >
          {displayPath}
        </Code>
      </>
    );
  }

  // Smart truncation - show beginning and end of path
  const truncatedPath = showFull
    ? path
    : `${path.substring(0, maxLength / 2)}...${path.substring(path.length - maxLength / 2)}`;

  return (
    <>
      <Code
        fontSize="sm"
        fontFamily="mono"
        aria-label={`File path: ${path}`}
        wordBreak={showFull ? "break-all" : "normal"}
        overflowWrap={showFull ? "break-word" : "normal"}
        overflow={showFull ? "visible" : "hidden"}
        role="text"
        aria-expanded={showFull}
        flex={showFull ? 1 : "none"}
        minWidth="0"
        minHeight="1.1em"
        py={1}
      >
        {truncatedPath}
      </Code>
      <Flex >
        <Button
          size="xs"
          bg="transparent"
          variant="ghost"
          onClick={() => setShowFull(!showFull)}
          aria-expanded={showFull}
          aria-label={showFull ? "Collapse path display" : "Expand path display"}
          color="blue.500"
        >
          {showFull ? "Show Less" : "Show Full"}
        </Button>
      </Flex>
    </>
  );
};

export const IssueDetailPage = ({ initialIssueData = null }) => {
  const [deleteModalOpen, setDeleteModalOpen] = useState(false);
  const { issueId } = useParams();
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const headingRef = useRef(null);
  const cancelRef = useRef();
  const tool = searchParams.get("tool") || null;
  const repoName = searchParams.get("reponame") || null;

  const { issueData, loading, error, deleting, handleDelete } = useIssueDetails(
    issueId,
    initialIssueData,
  );

  const isMobile = useBreakpointValue({ base: true, md: false });
  const optimalChars = useOptimalCharEstimate();

  const filterCodePath = (path) => {
    if (!path) return path;
    return path.startsWith('/code') ? path.substring(5) : path;
  };

  useEffect(() => {
    updatePageMetadata(
      issueData ? `Issue ${issueId}` : "Issue loading...",
      issueData ? issueId : "Loading issue information...",
      `/issues/${issueId}`,
    );
  }, [issueData, issueId]);

  useEffect(() => {
    if (issueData && headingRef.current) {
      headingRef.current.focus();
    }
  }, [issueData]);

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
      <Flex
        mb={6}
        align="center"
        justify="space-between"
        wrap="wrap"
        gap={4}
        aria-labelledby="issue-detail-heading"
      >
        <Heading
          ref={headingRef}
          tabIndex={-1}
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
                      maxChars={optimalChars}
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
                    aria-label={`Severity: ${issueData.severity}`}
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
                    aria-label={`Confidence: ${issueData.confidence}`}
                  >
                    {issueData.confidence}
                  </Badge>
                </Tooltip>
              </HStack>
            </Stack>
            <Spacer mt={6} />
          </Box>

          <Box color="blackAlpha.800">
            <Heading size="lg" mb={4}>
              Details
            </Heading>
            <SimpleGrid columns={{ base: 1, md: 2, lg: 3 }} spacing={6}>
              <Box>
                <Text fontWeight="medium" mb={1}>
                  Rule ID
                </Text>
                <Flex align="center" gap={2} wrap="wrap">
                  <Code fontSize="sm" fontFamily="mono" truncate>
                    {issueData.rule_id}
                  </Code>
                  <CopyButton
                    value={issueData.rule_id}
                    size="sm"
                    aria-label="Copy Rule ID to clipboard"
                  />
                </Flex>
              </Box>
              <Box>
                <Text fontWeight="medium" mb={1}>
                  File Path
                </Text>
                <Flex align="center" gap={2} wrap="wrap">
                  <PathDisplay
                    path={filterCodePath(issueData.path)}
                    maxLength={isMobile ? 25 : 30}
                  />
                </Flex>
              </Box>
              <Box>
                <Text fontWeight="medium" mb={1}>
                  Location
                </Text>
                <Code fontSize="sm" fontFamily="mono">
                  Line {issueData.start_line}
                  {issueData.end_line !== issueData.start_line &&
                    issueData.end_line !== 0 ?
                    `-${issueData.end_line}` : ''}
                  {issueData.column != 0 && `, Column ${issueData.column}`}
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
              <Box>
                <Text fontWeight="medium" mb={1}>
                  Codebase
                </Text>
                <Code fontSize="sm" fontFamily="mono">
                  {repoName ? repoName : "Unknown"}
                </Code>
              </Box>
              <Box>
                <Text fontWeight="medium" mb={1}>
                  Tool
                </Text>
                <Code fontSize="sm" fontFamily="mono">
                  {tool ? tool : "Unknown"}
                </Code>
              </Box>
            </SimpleGrid>
          </Box>

          <Box color="blackAlpha.800">
            <Heading size="md" mb={4}>
              Code Snippet
            </Heading>
            <CodeSnippetDisplay
              code={issueData.code}
              maxLines={isMobile ? 15 : 20}
            />
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
                role="region"
                aria-labelledby="additional-context-heading"
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
