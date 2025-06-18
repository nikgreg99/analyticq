import React, { memo, useCallback } from "react";
import {
  Box,
  Badge,
  Text,
  Flex,
  IconButton,
  HStack,
  Tag,
} from "@chakra-ui/react";
import { Tooltip } from "../general/Tooltip";
import { useNavigate } from "react-router-dom";
import { FaForward, FaClock } from "react-icons/fa";
import { FiInfo } from "react-icons/fi";
import { SEVERITY_COLOR } from "components/utils/issues";
import { getFileNameFromPath } from "components/utils/files";
import { formatDate } from "components/utils/time";
import { capitalizeFirstLetter } from "components/utils/strings";

/**
 * A component that displays an issue card with severity, rule ID, file path, and message.
 *
 * @component
 * @param {Object} props
 * @param {Object} props.issue - The issue object to display
 * @param {string} props.issue.severity - The severity level of the issue ('red', 'medium', 'low')
 * @param {string} props.issue.rule_id - The identifier of the rule that triggered the issue
 * @param {string} props.issue.path - The file path where the issue was found
 * @param {number} props.issue.start_line - The line number where the issue starts
 * @param {string} props.issue.message - The description or message of the issue
 * @param {boolean} [props.showCreationDate=true] - Whether to display the issue's creation date
 *
 * @returns {JSX.Element} A card component displaying the issue information
 */
export const IssueCard = ({ issue, showCreationDate = true }) => {
  const navigate = useNavigate();

  const handleNavigate = useCallback(() => {
    navigate(`/issues/${issue.id}`);
  }, [navigate, issue.id]);

  const handleKeyDown = useCallback((event) => {
    if (event.key === 'Enter' || event.key === ' ') {
      event.preventDefault();
      handleNavigate();
    }
  }, [handleNavigate]);

  const handleIconButtonClick = useCallback((event) => {
    event.stopPropagation();
    handleNavigate();
  }, [handleNavigate]);


  // Validate required issue properties
  if (!issue?.id || !issue?.rule_id || !issue?.severity) {
    console.warn('IssueCard: Missing required issue properties', issue);
    return null;
  }



  return (
    <Box
      onClick={handleNavigate}
      onKeyDown={handleKeyDown}
      p={3}
      borderWidth="1px"
      borderRadius="md"
      borderColor="gray.200"
      _hover={{ boxShadow: "sm", bg: "gray.50" }}
      _focus={{ boxShadow: "outline" }}
      transition="background 0.2s"
      role="button"
      tabIndex={0}
      aria-label={`Open details for issue ${issue.rule_id}`}
      cursor="pointer"
    >
      <Flex justifyContent="space-between" alignItems="flex-start" gap={2}>
        <Flex alignItems="center" gap={2} flexWrap="wrap" minWidth={0}>
          <Tooltip content={`Severity: ${issue.severity}`} showArrow>
            <Badge colorPalette={SEVERITY_COLOR[issue.severity]}>
              {capitalizeFirstLetter(issue.severity)}
            </Badge>
          </Tooltip>

          <Text
            fontWeight="medium"
            fontSize="sm"
            color="blackAlpha.800"
            noOfLines={1}
            isTruncated
          >
            {issue.rule_id}
          </Text>

          <Text fontSize="xs" color="gray.700" isTruncated>
            {getFileNameFromPath(issue?.path) ?? "Unknown"}:
            {issue?.start_line ?? "?"}
          </Text>
        </Flex>

        <Flex alignItems="center" gap={1} flexShrink={0}>
          <Tooltip
            content="These details are reported directly from the analysis tool without further processing."
            showArrow
          >
            <Box
              as="span"
              display="inline-flex"
              cursor="help"

            >
              <FiInfo
                color="black"
                size={12}
                cursor="help"
                aria-label="Data source information"
              />
            </Box>

          </Tooltip>

          <Tooltip content="View issue details" showArrow>

            <IconButton
              size="sm"
              aria-label={`View details for ${issue.rule_id}`}
              onClick={handleIconButtonClick}
              cursor="pointer"
              variant="subtle"
              _hover={{ bg: "gray.700" }}
            >
              <FaForward />
            </IconButton>
          </Tooltip>
        </Flex>
      </Flex>


      {issue.message && (
        <Text
          mt={2}
          fontSize="sm"
          noOfLines={2}
          color="gray.700"
          title={issue.message}
        >
          {issue.message}
        </Text>
      )}

      {showCreationDate && issue.created_at && (
        <HStack mt={2} aria-label="creation-date">
          <FaClock size={12} color="black" />
          <Tag.Root colorPalette="gray">
            <Tag.Label>Created: {formatDate(issue.created_at)}</Tag.Label>
          </Tag.Root>
        </HStack>
      )}
    </Box>
  );
};

IssueCard.displayName = "IssueCard";

export default memo(IssueCard);
