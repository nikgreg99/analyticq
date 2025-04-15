import React from "react";
import { Table } from "@chakra-ui/react";
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

    return (
        <Table.Root size="sm" interactive striped>
            <Table.Header>
                <Table.Row>
                    <Table.ColumnHeader>Codebase name</Table.ColumnHeader>
                    <Table.ColumnHeader>Created At</Table.ColumnHeader>
                    <Table.ColumnHeader>Updated At</Table.ColumnHeader>
                </Table.Row>
            </Table.Header>
            <Table.Body>
                {contexts.map((item) => (
                    <Table.Row
                        key={item.id}
                        cursor="pointer"
                        _hover={{ bg: "blackAlpha.800" }}
                        onClick={() => navigate(`/contexts/${item.id}`)}
                        tabIndex={item.id}
                        transition="background-color 0.2s"
                    >
                        <Table.Cell
                            aria-label={`${item.repo_name}`}
                        >
                            {item.repo_name}
                        </Table.Cell>
                        <Table.Cell
                            aria-label={`${item.created_at}`}
                        >
                            {formatDate(item.created_at)}
                        </Table.Cell>
                        <Table.Cell
                            aria-label={`${item.updated_at}`}
                        >
                            {formatDate(item.updated_at)}
                        </Table.Cell>
                    </Table.Row>
                ))}
            </Table.Body>
        </Table.Root>
    );
};

export default ContextList;
