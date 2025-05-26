// components/context/ContextList.jsx
import React from "react";
import { formatDate } from "components/utils/time";
import { useNavigate } from "react-router-dom";
import { DataTable } from "../general/DataTable";

/**
 * A component that displays a list of code repository contexts in a table format.
 * Allows navigation to individual context details when a row is clicked.
 *
 * @component
 * @param {Object} props - Component props
 * @param {Array} props.contexts - Array of context objects to display
 * @param {string} props.contexts[].id - Unique identifier for each context
 * @param {string} props.contexts[].repo_name - Name of the code repository
 * @param {string} props.contexts[].created_at - Creation timestamp
 * @param {string} props.contexts[].updated_at - Last update timestamp
 *
 * @returns {JSX.Element} A DataTable component displaying the contexts
 */
export const ContextList = ({ contexts }) => {
  const navigate = useNavigate();

  return (
    <DataTable
      ariaLabel="Code repositories list"
      data={contexts}
      rowKey={(row) => row.id}
      onRowClick={(row) => navigate(`/contexts/${row.id}`)}
      emptyText="No code repositories found"
      columns={[
        { header: "Codebase name", accessor: "repo_name" },
        {
          header: "Created At",
          accessor: "created_at",
          render: (row) => formatDate(row.created_at),
        },
        {
          header: "Updated At",
          accessor: "updated_at",
          render: (row) => formatDate(row.updated_at),
        },
      ]}
    />
  );
};

ContextList.displayName = "ContextList";
