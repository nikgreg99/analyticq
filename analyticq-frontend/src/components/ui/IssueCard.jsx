import React from 'react';
import { Box, Badge, Text, Flex, IconButton } from '@chakra-ui/react';
import { Tooltip } from './tooltip';
import { useNavigate } from 'react-router-dom';
import { FaForward } from "react-icons/fa";
import { SEVERITY_COLOR } from 'components/utils/issues';

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
 *
 * @returns {JSX.Element} A card component displaying the issue information
 */
export const IssueCard = ({ issue }) => {

  const navigate = useNavigate();

  return (
    <Box
      p={3}
      borderWidth="1px"
      borderRadius="md"
      borderColor="gray.200"
      _hover={{ boxShadow: "sm", bg: "gray.50" }}
    >
      <Flex justifyContent="space-between" alignItems="center">
        <Flex alignItems="center" gap={2}>
          <Tooltip content={`Severity: ${issue.severity}`}>
            <Badge colorPalette={SEVERITY_COLOR[issue.severity]}>
              {issue.severity.charAt(0).toUpperCase()}
            </Badge>
          </Tooltip>

          <Text
            fontWeight="medium"
            fontSize="sm"
            color="blackAlpha.800"
          >
            {issue.rule_id}
          </Text>
        </Flex>

        <Text color="gray.500" fontSize="xs">
          {issue.path}:{issue.start_line}
        </Text>
        <Tooltip content="View Details">
          <IconButton
            size="sm"
            aria-label="View details"
            cursor="pointer"
            variant="subtle"
            onClick={() => navigate(`/issues/${issue.id}`)}
          >
            <FaForward />
          </IconButton>
        </Tooltip>
      </Flex>

      <Text
        mt={2}
        fontSize="sm"
        noOfLines={2}
        color="gray.700"
      >
        {issue.message}
      </Text>
    </Box>
  );
};

export default IssueCard;
