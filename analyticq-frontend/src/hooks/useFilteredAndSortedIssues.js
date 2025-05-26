import { useMemo } from "react";
import { sortIssues, filterIssues } from "components/utils/issues";

/**
 * Custom hook that filters and sorts issues based on search term and sort order
 * @param {Array} issues - Array of issue objects to filter and sort
 * @param {string} searchTerm - Term to filter issues by
 * @param {Array} sortOrder - Array containing sort configuration [sortField, sortDirection]
 * @param {Object} severityConfig - Configuration object for severity levels and their order
 * @returns {Array} Filtered and sorted array of issues
 */
export function useFilteredAndSortedIssues(
  issues,
  searchTerm,
  sortOrder,
  severityConfig,
) {
  const filteredIssues = useMemo(
    () => filterIssues(issues, searchTerm),
    [issues, searchTerm],
  );
  const sortedIssues = useMemo(
    () => sortIssues(filteredIssues, sortOrder[0], severityConfig),
    [filteredIssues, sortOrder, severityConfig],
  );

  return sortedIssues;
}
