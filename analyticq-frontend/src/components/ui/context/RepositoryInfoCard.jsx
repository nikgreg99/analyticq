import React from "react";
import {
  Card,
  Stack,
  Flex,
  Text,
  Heading,
  Box,
  useBreakpointValue,
} from "@chakra-ui/react";
import { formatDate } from "components/utils/time";
import RepositoryTypeBadge from "components/ui/context/RepositoryTypeBadge";
import { InfoRow } from "./RepositoryInfoRow";

/**
 * A component that displays repository information in a card format.
 *
 * @component
 * @param {Object} props - The component props
 * @param {Object} props.contextData - The repository context data object
 * @param {string} props.contextData.repo_name - The name of the repository
 * @param {string} props.contextData.input_type - The type of the repository
 * @param {string} [props.contextData.branch] - The branch name (optional)
 * @param {string} [props.contextData.last_commit_hash] - The last commit hash (optional)
 * @param {string} props.contextData.created_at - The creation date of the repository
 * @param {string} props.contextData.updated_at - The last update date of the repository
 *
 * @returns {JSX.Element} A card component displaying repository information including
 * repository name, type, branch, last commit hash, creation date, and last update date
 */
const RepositoryInfoCard = ({ contextData }) => {
  const labelWidth = useBreakpointValue({ base: "100%", sm: "40%" });

  return (
    <Card.Root mb={6} variant="elevated">
      <Card.Header>
        <Heading size="md" color="whiteAlpha.800">
          Repository Information
        </Heading>
      </Card.Header>

      <Card.Body>
        <Stack spacing={4} as="dl">
          <InfoRow
            label="Repository name"
            value={contextData.repo_name ?? "N/A"}
          />

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
              Repository Type
            </Text>
            <Box>
              <RepositoryTypeBadge inputType={contextData.input_type} />
            </Box>
          </Flex>

          {contextData.branch && (
            <InfoRow label="Branch" value={contextData.branch} />
          )}

          {contextData.last_commit_hash && (
            <InfoRow
              label="Last Commit Hash"
              value={contextData.last_commit_hash.substring(0, 8)}
            />
          )}

          <InfoRow
            label="Created At"
            value={formatDate(contextData.created_at)}
          />
          <InfoRow
            label="Last Updated"
            value={formatDate(contextData.updated_at)}
          />
        </Stack>
      </Card.Body>
    </Card.Root>
  );
};

RepositoryInfoCard.displayName = "RepositoryInfoCard";

export default RepositoryInfoCard;
