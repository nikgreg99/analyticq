import React from "react";
import { Table, Text } from "@chakra-ui/react";
import { formatDate } from "components/utils/time";
import { useNavigate } from "react-router-dom";

/**
 * A component that displays a list of code repository contexts in a table format.
 * Each context is represented as a clickable row that links to its detailed view.
 *
 * @component
 * @param {Object} props - The component props
 * @param {Array<{id: string|number, repo_name: string}>} props.contexts - Array of context objects to display
 * @param {string|number} props.contexts[].id - Unique identifier for each context
 * @param {string} props.contexts[].repo_name - Name of the repository to display
 *
 * @returns {JSX.Element} A table displaying the list of contexts
 */
const ContextList = ({ contexts }) => {

    const navigate = useNavigate();

    const handleRowNavigation = (id, event) => {
        if (event.type === "click") {
            navigate(`/contexts/${id}`);
        }
    };

    return (
        <Table.Root
            size="sm"
            interactive
            striped
            aria-label="Code repositories list"
            role="table"
        >
            <Table.Header>
                <Table.Row>
                    <Table.ColumnHeader scope="col">Codebase name</Table.ColumnHeader>
                    <Table.ColumnHeader scope="col">Created At</Table.ColumnHeader>
                    <Table.ColumnHeader scope="col">Updated At</Table.ColumnHeader>
                </Table.Row>
            </Table.Header>
            <Table.Body>
                {contexts.length === 0 ? (
                    <Table.Cell colSpan={3}>
                        <Text
                            color="gray.500"
                            py={4}
                            role="status"
                            textAlign="center"
                            aria-live="polite"
                        >
                            No code repositories found
                        </Text>
                    </Table.Cell>
                ) : (
                    contexts.map((item) => (
                    <Table.Row
                        key={item.id}
                        cursor="pointer"
                        _hover={{ bg: "blackAlpha.800" }}
                        _focus={{
                            bg: "blackAlpha.800",
                            outline: "none",
                            boxShadow: "outline"
                          }}
                        onClick={(e) =>  handleRowNavigation(item.id, e)}
                        onKeyDown={(e) => handleRowNavigation(item.id, e)}
                        tabIndex={0}
                        role="row"
                        transition="background-color 0.2s"
                        aria-label={`Repository: ${item.repo_name}`}
                    >
                        <Table.Cell
                            aria-label={`Repository Name: ${item.repo_name}`}
                        >
                            {item.repo_name}
                        </Table.Cell>
                        <Table.Cell
                            aria-label={`Created at: ${item.created_at}`}
                        >
                            {formatDate(item.created_at)}
                        </Table.Cell>
                        <Table.Cell
                            aria-label={`Updated at: ${item.updated_at}`}
                        >
                            {formatDate(item.updated_at)}
                        </Table.Cell>
                    </Table.Row>
                ))
            )}
            </Table.Body>
        </Table.Root>
    );
};

export default ContextList;
