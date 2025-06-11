import React from "react";
import {
  Card,
  Stack,
  Flex,
  Text,
  Heading,
  Box,
  useBreakpointValue,
  Tooltip,
  Link,
  HStack,
  Icon,
} from "@chakra-ui/react";
import { formatDate } from "components/utils/time";
import RepositoryTypeBadge from "components/ui/context/RepositoryTypeBadge";
import { InfoRow } from "./RepositoryInfoRow";
import { FaCodeBranch, FaCopy } from "react-icons/fa6";
import { HiCalendarDateRange } from "react-icons/hi2";
import { RiGitRepositoryFill } from "react-icons/ri";
import { MdContentCopy } from "react-icons/md";

/**
 * Repository context data interface
 * @typedef {Object} RepositoryContextData
 * @property {string} repo_name - The name of the repository
 * @property {string} input_type - The type of the repository
 * @property {string} [branch] - The branch name (optional)
 * @property {string} [last_commit_hash] - The last commit hash (optional)
 * @property {string} created_at - The creation date of the repository
 * @property {string} updated_at - The last update date of the repository
 * @property {string} [repo_url] - The repository URL (optional)
 */

/**
 * A component that displays repository information in a card format.
 *
 * @component
 * @param {Object} props - The component props
 * @param {RepositoryContextData} props.contextData - The repository context data object
 * @param {boolean} [props.isLoading=false] - Loading state indicator
 * @param {Function} [props.onCopyHash] - Callback when commit hash is copied
 * @param {Object} [props.cardProps] - Additional props to pass to the Card component
 *
 * @returns {JSX.Element} A card component displaying repository information
 */
const RepositoryInfoCard = ({
  contextData,
  isLoading = false,
  onCopyHash,
  ...cardProps
}) => {
  const labelWidth = useBreakpointValue({ base: "100%", sm: "40%" });

  // Validation for required data
  if (!contextData) {
    return (
      <Card.Root mb={6} variant="elevated" {...cardProps}>
        <Card.Body>
          <Text color="gray.500" textAlign="center">
            No repository information available
          </Text>
        </Card.Body>
      </Card.Root>
    );
  }

  const handleCopyCommitHash = async () => {
    if (contextData.last_commit_hash) {
      try {
        await navigator.clipboard.writeText(contextData.last_commit_hash);
        onCopyHash?.(contextData.last_commit_hash);
      } catch (err) {
        console.error('Failed to copy commit hash:', err);
      }
    }
  };

  const formatCommitHash = (hash) => {
    if (!hash) return "N/A";
    return hash.length > 8 ? `${hash.substring(0, 8)}...` : hash;
  };

  const renderRepositoryName = () => {
    const name = contextData.repo_name || "N/A";

    if (contextData.repo_url) {
      return (
        <Link
          href={contextData.repo_url}
          isExternal
          color="blue.300"
          _hover={{ color: "blue.200", textDecoration: "underline" }}
        >
          {name}
        </Link>
      );
    }

    return name;
  };

  const renderCommitHash = () => {
    if (!contextData.last_commit_hash) return null;

    return (
      <HStack spacing={2}>
        <Text fontSize="sm" fontFamily="mono">
          {formatCommitHash(contextData.last_commit_hash)}
        </Text>
        {contextData.last_commit_hash.length > 8 && (
          <Tooltip label="Copy full commit hash" hasArrow>
            <Box
              as="button"
              onClick={handleCopyCommitHash}
              color="gray.400"
              _hover={{ color: "gray.200" }}
              cursor="pointer"
              aria-label="Copy commit hash"
            >
              <MdContentCopy size={14} />
            </Box>
          </Tooltip>
        )}
      </HStack>
    );
  };

  const renderRepositoryType = () => {
    return (
      <RepositoryTypeBadge
        inputType={contextData.input_type}
      />
    );
  };

  return (
    <Card.Root
      mb={6}
      variant="elevated"
      opacity={isLoading ? 0.7 : 1}
      {...cardProps}
    >
      <Card.Header>
        <Heading
          size="md"
          color="whiteAlpha.800"
          role="heading"
          aria-level={2}
        >
          Repository Information
        </Heading>
      </Card.Header>

      <Card.Body>
        <Stack spacing={4} as="dl">
          <InfoRow
            label="Repository name"
            icon={RiGitRepositoryFill}
            value={renderRepositoryName()}
          />

          <InfoRow
            label="Repository Type"
            icon={RiGitRepositoryFill}
            value={renderRepositoryType()}
          />

          {contextData.branch && (
            <InfoRow
              label="Branch"
              value={contextData.branch}
              icon={FaCodeBranch}
            />
          )}

          {contextData.last_commit_hash && (
            <Flex
              direction={{ base: "column", sm: "row" }}
              justify="space-between"
              align={{ base: "flex-start", sm: "center" }}
              wrap="wrap"
            >
              <Text
                color="whiteAlpha.800"
                fontWeight="semibold"
                fontSize="sm"
                mb={{ base: 1, sm: 0 }}
                w={labelWidth}
                flexShrink={0}
              >
                Last Commit Hash
              </Text>
              <Box>
                {renderCommitHash()}
              </Box>
            </Flex>
          )}

          {contextData.created_at && (
            <InfoRow
              label="Created At"
              icon={HiCalendarDateRange}
              value={formatDate(contextData.created_at)}
            />
          )}

          {contextData.updated_at && (
            <InfoRow
              label="Last Updated At"
              icon={HiCalendarDateRange}
              value={formatDate(contextData.updated_at)}
            />
          )}
        </Stack>
      </Card.Body>
    </Card.Root>
  );
};

// Add PropTypes for better development experience (optional)
RepositoryInfoCard.displayName = "RepositoryInfoCard";

export default RepositoryInfoCard;
