import React from "react";
import {
    Card,
    Stack,
    Flex,
    Text,
    Heading,
} from "@chakra-ui/react";
import { formatDate } from "components/utils/time";
import RepositoryTypeBadge from "components/ui/RepositoryTypeBadge";
import { InfoRow } from "./InfoRow";


/**
 * A card component that displays repository information.
 *
 * @component
 * @param {Object} props - The component props
 * @param {Object} props.contextData - Repository data object
 * @param {string} props.contextData.repo_name - Name of the repository
 * @param {string} props.contextData.input_type - Type of the repository
 * @param {string} [props.contextData.branch] - Repository branch (optional)
 * @param {string} [props.contextData.last_commit_hash] - Last commit hash (optional)
 * @param {string} props.contextData.created_at - Repository creation date
 * @param {string} props.contextData.updated_at - Repository last update date
 *
 * @returns {JSX.Element} A card displaying formatted repository information including
 * name, type, branch, last commit hash, creation date, and last update date
 */
const RepositoryInfoCard = ({ contextData }) => {

    return (
        <Card.Root mb={6} variant="elevated">
            <Card.Header>
                <Heading size="md" color="whiteAlpha.800">Repository Information</Heading>
            </Card.Header>
            <Card.Body>
                <Stack spacing={4} as="dt">
                    <InfoRow label="Repository name" value={contextData.repo_name ?? "N/A"} />

                    <Flex justify="space-between">
                        <Text color="whiteAlpha.800">Repository Type</Text>
                        <RepositoryTypeBadge inputType={contextData.input_type}
                        />
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

                    <InfoRow label="Created At" value={formatDate(contextData.created_at)} />
                    <InfoRow label="Last Updated" value={formatDate(contextData.updated_at)} />
                </Stack>
            </Card.Body>
        </Card.Root>
    );
};

export default RepositoryInfoCard;
