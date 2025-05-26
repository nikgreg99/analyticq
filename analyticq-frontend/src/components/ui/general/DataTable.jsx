import React from "react";
import { Table, Text, HStack } from "@chakra-ui/react";
import { FaChevronUp, FaChevronDown } from "react-icons/fa";
import { useTableSort} from "hooks/useTableSort";

/**
 * A reusable table component with sorting functionality.
 *
 * @param {Object} props
 * @param {Array} props.columns - Array of column definitions (header, accessor, sortable, optional render).
 * @param {Array} props.data - Array of data to render in rows.
 * @param {Function} props.rowKey - Function to generate a unique key for each row.
 * @param {Function} [props.onRowClick] - Optional row click handler.
 * @param {string} [props.emptyText="No data available"] - Text to show when data is empty.
 * @param {string} [props.ariaLabel="Data table"] - ARIA label for accessibility.
 * @param {Object} [props.defaultSort] - Default sort configuration { key: string, direction: 'asc' | 'desc' }.
 * @param {Function} [props.onSort] - Optional callback when sort changes.
 */
export const DataTable = ({
  columns,
  data,
  rowKey,
  onRowClick,
  emptyText = "No data available",
  ariaLabel = "Data table",
  defaultSort = null,
  onSort,
}) => {
  const {
    sortedData,
    handleSort,
    getSortIcon,
    isSortable,
    getSortAriaLabel,
  } = useTableSort(data, columns, defaultSort, onSort);

  const renderSortIcon = (columnKey) => {
    const sortDirection = getSortIcon(columnKey);

    if (sortDirection === 'asc') {
      return <FaChevronUp boxSize={4} />;
    } else if (sortDirection === 'desc') {
      return <FaChevronDown boxSize={4} />;
    }

    // Show subtle hint for sortable columns
    return (
      <FaChevronUp
        boxSize={3}
        color="gray.300"
        opacity={0.5}
      />
    );
  };

  return (
    <Table.Root
      size="sm"
      interactive={!!onRowClick}
      striped
      aria-label={ariaLabel}
      role="table"
    >
      <Table.Header>
        <Table.Row>
          {columns.map((col) => (
            <Table.ColumnHeader
              key={col.accessor}
              cursor={isSortable(col) ? "pointer" : "default"}
              onClick={() => handleSort(col.accessor)}
              onKeyDown={(e) => {
                if ((e.key === 'Enter' || e.key === ' ') && isSortable(col)) {
                  e.preventDefault();
                  handleSort(col.accessor);
                }
              }}
              tabIndex={isSortable(col) ? 0 : undefined}
              role="columnheader"
              aria-sort={getSortAriaLabel(col.accessor)}
              _hover={isSortable(col) ? { bg: "blackAlpha.50" } : {}}
              _focus={isSortable(col) ? {
                outline: "none",
                boxShadow: "outline",
                bg: "blackAlpha.100"
              } : {}}
            >
              <HStack spacing={2} justify="space-between">
                <Text>{col.header}</Text>
                {isSortable(col) && renderSortIcon(col.accessor)}
              </HStack>
            </Table.ColumnHeader>
          ))}
        </Table.Row>
      </Table.Header>
      <Table.Body>
        {sortedData.length === 0 ? (
          <Table.Row>
            <Table.Cell colSpan={columns.length}>
              <Text
                color="gray.500"
                py={4}
                role="status"
                textAlign="center"
                aria-live="polite"
              >
                {emptyText}
              </Text>
            </Table.Cell>
          </Table.Row>
        ) : (
          sortedData.map((row) => (
            <Table.Row
              key={rowKey(row)}
              cursor={onRowClick ? "pointer" : "default"}
              _hover={onRowClick ? { bg: "Background" } : {}}
              _focus={
                onRowClick
                  ? {
                      bg: "blackAlpha.100",
                      outline: "none",
                      boxShadow: "outline",
                    }
                  : {}
              }
              onClick={() => onRowClick?.(row)}
              onKeyDown={(e) => e.key === "Enter" && onRowClick?.(row)}
              tabIndex={onRowClick ? 0 : undefined}
              role="row"
            >
              {columns.map((col) => (
                <Table.Cell key={col.accessor}>
                  {col.render ? col.render(row) : row[col.accessor]}
                </Table.Cell>
              ))}
            </Table.Row>
          ))
        )}
      </Table.Body>
    </Table.Root>
  );
};

DataTable.displayName = "DataTable";
