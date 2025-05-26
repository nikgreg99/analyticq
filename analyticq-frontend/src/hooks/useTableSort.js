import { useState, useMemo } from "react";

/**
 * Custom hook for handling table sorting logic
 *
 * @param {Array} data - The data to sort
 * @param {Array} columns - Column definitions with sorting configuration
 * @param {Object} [defaultSort] - Default sort configuration { key: string, direction: 'asc' | 'desc' }
 * @param {Function} [onSort] - Callback when sort changes
 * @returns {Object} - { sortedData, sortConfig, handleSort, getSortIcon, isSortable }
 */
export const useTableSort = (data, columns, defaultSort = null, onSort) => {
  const [sortConfig, setSortConfig] = useState(defaultSort);

  // Sort data based on current sort configuration
  const sortedData = useMemo(() => {
    if (!sortConfig || !data) return data;

    const { key, direction } = sortConfig;
    const column = columns.find(col => col.accessor === key);

    return [...data].sort((a, b) => {
      let aVal = a[key];
      let bVal = b[key];

      // Handle custom sort function if provided
      if (column?.sortFn) {
        return direction === 'asc'
          ? column.sortFn(a, b)
          : column.sortFn(b, a);
      }

      // Handle null/undefined values
      if (aVal == null && bVal == null) return 0;
      if (aVal == null) return direction === 'asc' ? 1 : -1;
      if (bVal == null) return direction === 'asc' ? -1 : 1;

      // Convert to string for comparison if not already
      if (typeof aVal !== 'string' && typeof aVal !== 'number') {
        aVal = String(aVal);
      }
      if (typeof bVal !== 'string' && typeof bVal !== 'number') {
        bVal = String(bVal);
      }

      // Numeric comparison
      if (typeof aVal === 'number' && typeof bVal === 'number') {
        return direction === 'asc' ? aVal - bVal : bVal - aVal;
      }

      // String comparison (case insensitive)
      const aStr = String(aVal).toLowerCase();
      const bStr = String(bVal).toLowerCase();

      if (direction === 'asc') {
        return aStr < bStr ? -1 : aStr > bStr ? 1 : 0;
      } else {
        return aStr > bStr ? -1 : aStr < bStr ? 1 : 0;
      }
    });
  }, [data, sortConfig, columns]);

  const handleSort = (columnKey) => {
    const column = columns.find(col => col.accessor === columnKey);

    // Don't sort if column is not sortable
    if (column?.sortable === false) return;

    let newDirection = 'asc';

    if (sortConfig?.key === columnKey) {
      // If already sorting by this column, toggle direction or clear sort
      if (sortConfig.direction === 'asc') {
        newDirection = 'desc';
      } else {
        // Clear sort (return to original order)
        setSortConfig(null);
        onSort?.(null);
        return;
      }
    }

    const newSortConfig = { key: columnKey, direction: newDirection };
    setSortConfig(newSortConfig);
    onSort?.(newSortConfig);
  };

  const getSortIcon = (columnKey) => {
    if (sortConfig?.key !== columnKey) return null;
    return sortConfig.direction;
  };

  const isSortable = (column) => column.sortable !== false;

  const getSortAriaLabel = (columnKey) => {
    if (sortConfig?.key === columnKey) {
      return sortConfig.direction === 'asc' ? 'ascending' : 'descending';
    }
    return isSortable(columns.find(col => col.accessor === columnKey)) ? 'none' : undefined;
  };

  return {
    sortedData,
    sortConfig,
    handleSort,
    getSortIcon,
    isSortable,
    getSortAriaLabel,
  };
};
