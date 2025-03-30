import React  from 'react';
import {
    Accordion,
    Box,
    Text,
    Badge,
    VStack,
    useDisclosure,
    Dialog,
    Portal,
    Button,
    CloseButton,
} from "@chakra-ui/react"
import { MetadataRenderer } from 'components/layout/MetadataRender';
import { deleteIssue } from 'services/issueService';

// Severity color mappings
const SEVERITY_COLORS = {
    'CRITICAL': 'red',
    'HIGH': 'orange',
    'MEDIUM': 'yellow',
    'LOW': 'green',
    'INFO': 'blue'
};

// Confidence color mapping
const CONFIDENCE_COLORS = {
    'HIGH': 'green',
    'MEDIUM': 'yellow',
    'LOW': 'orange'
};


/**
 * A component that renders an expandable card displaying issue details.
 *
 * @component
 * @param {Object} props - The component props
 * @param {Object} props.issue - The issue object to display
 * @param {string} props.issue.id - Unique identifier of the issue
 * @param {string} props.issue.severity - Severity level of the issue
 * @param {string} props.issue.confidence - Confidence level of the issue
 * @param {string} props.issue.rule_id - ID of the rule that triggered the issue
 * @param {string} props.issue.path - File path where the issue was found
 * @param {number} props.issue.start_line - Starting line number of the issue
 * @param {number} props.issue.end_line - Ending line number of the issue
 * @param {number} props.issue.column - Column number where the issue occurs (optional)
 * @param {string} props.issue.message - Detailed message about the issue
 * @param {string} props.issue.code - Code snippet where the issue was found (optional)
 * @param {Object} props.issue.issue_metadata - Additional metadata about the issue
 * @param {Object} props.issue.summary - Summary information about the issue
 *
 * @returns {JSX.Element} An accordion component containing the issue details
 */
export const IssueCard = ({ issue }) => {

    const dialog = useDisclosure();

    const handleDeleteIssue = async () => {
        try {
            await deleteIssue(issue.id);
            // Successfully deleted, close the modal
            dialog.setOpen(false);
        } catch (error) {
            console.error("Failed to delete issue:", error);
        }
    };

    return (
        <Accordion.Root
            collapsible
            width="full"
            borderWidth={1}
            borderRadius="lg"
        >
            <Accordion.Item value={issue.id.toString()}>
                <Accordion.ItemTrigger>
                    <Box display="flex" justifyContent="space-between" width="full">
                            <Box display="flex" alignItems="center">
                                <Badge
                                    colorScheme={SEVERITY_COLORS[issue.severity]}
                                    mr={2}
                                >
                                    {issue.severity}
                                </Badge>
                                <Badge
                                    colorScheme={CONFIDENCE_COLORS[issue.confidence]}
                                    mr={2}
                                 >
                                    {issue.confidence}
                                </Badge>
                                <Text fontWeight="semibold">
                                    {issue.rule_id}
                                </Text>
                            </Box>
                            <Text color="gray.500" fontSize="sm">
                                {issue.path}:{issue.start_line}
                            </Text>
                    </Box>
            </Accordion.ItemTrigger>
            <Accordion.ItemContent>
                <VStack spacing={4} align="stretch">
                    <Box>
                        <Text fontWeight="bold">Message:</Text>
                        <Text>{issue.message}</Text>
                    </Box>
                    <Box>
                        <Text fontWeight="bold"> Message: </Text>
                        <Text>
                            <br/>
                            Lines: {issue.start_line} - {issue.end_line}
                            {issue.column > 0 &&
                                <> | Column: {issue.column} </>
                            }
                        </Text>
                    </Box>
                    {issue.code && (
                        <Box>
                            <Text fontWeight="bold">Code Snippet:</Text>
                            <Box
                                p={2}
                                width="full"
                                overflowX="auto"
                                color="blackAlpha.800"
                            >
                                <pre>{issue.code}</pre>
                            </Box>
                        </Box>
                    )}
                    <Box>
                        <Text fontWeight="bold">Issue Metadata:</Text>
                        <MetadataRenderer metadata={issue.issue_metadata} />
                    </Box>
                    <Box>
                        <Text fontWeight="bold">Summary:</Text>
                        <MetadataRenderer metadata={issue.summary} />
                    </Box>
                    </VStack>
                </Accordion.ItemContent>
            </Accordion.Item>

            <Dialog.RootProvider role="alertdialog" value>
                <Dialog.Trigger asChild>
                    <Button variant="outline" size="sm">
                        Delete issue
                    </Button>
                </Dialog.Trigger>
                <Portal>
                    <Dialog.Backdrop />
                    <Dialog.Positioner>
                        <Dialog.Content>
                            <Dialog.Header>
                                <Dialog.Title>Are you sure to delete this issue?</Dialog.Title>
                            </Dialog.Header>
                            <Dialog.Body>
                            </Dialog.Body>
                            <Dialog.Footer>
                                <Dialog.ActionTrigger asChild>
                                    <Button variant="outline" onClick={handleDeleteIssue}>Cancel</Button>
                                </Dialog.ActionTrigger>
                            </Dialog.Footer>
                            <Dialog.CloseTrigger asChild>
                                <CloseButton size="sm"/>
                            </Dialog.CloseTrigger>
                        </Dialog.Content>
                    </Dialog.Positioner>
                </Portal>
            </Dialog.RootProvider>

        </Accordion.Root>

    );
};
