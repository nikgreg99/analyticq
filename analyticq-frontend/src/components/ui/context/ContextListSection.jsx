import React from "react";
import { Box, Stack, Text } from "@chakra-ui/react";
import { ContextList } from "components/ui/context/ContextList";
import PaginationControls from "components/ui/general/PaginationControls";

/**
 * Renders a section displaying a list of contexts with optional pagination controls
 *
 * @component
 * @param {Object} props - Component props
 * @param {Array} props.filteredContexts - Array of filtered context items to display
 * @param {boolean} props.hasPagination - Whether pagination controls should be shown
 * @param {Object} props.contextsData - Pagination data object
 * @param {number} props.contextsData.total - Total number of items
 * @param {number} props.contextsData.page_size - Number of items per page
 * @param {number} props.contextsData.page - Current page number
 * @param {Function} props.onPageChange - Callback function when page changes
 * @param {string} props.searchQuery - Current search query string
 * @param {boolean} props.isEmptySearchResult - Whether the search returned no results
 * @param {string} [props.paginationHeight="150px"] - Height of pagination container
 * @returns {JSX.Element} A stack containing either a "no results" message or the context list with pagination
 */
export const ContextListSection = ({
  filteredContexts,
  hasPagination,
  contextsData,
  onPageChange,
  searchQuery,
  isEmptySearchResult,
  paginationHeight = "150px", // Default height for pagination container
}) => {
  if (filteredContexts.length === 0) {
    return (
      <Stack width="full" gap={5}>
        <Box mt={6} p={6} borderWidth="1px" borderRadius="lg" bg="gray.50">
          <Text fontSize="lg" textAlign="center" color="gray.600">
            No codebase found
          </Text>
          <Text fontSize="md" color="gray.500">
            {isEmptySearchResult
              ? `No codebase matches "${searchQuery}". Try a different search term.`
              : "No codebase available."}
          </Text>
        </Box>

        {/* Always render pagination container with consistent height even when empty */}
        {hasPagination && <Box height={paginationHeight} />}
      </Stack>
    );
  }

  return (
    <Stack width="full" gap={5}>
      <Box
        // Set a minimum height for the list container to prevent layout shifts
        minHeight="300px"
      >
        <ContextList contexts={filteredContexts} />
      </Box>

      {/* Always render pagination container with the same fixed height */}
      {hasPagination ? (
        <PaginationControls
          total={contextsData.total}
          pageSize={contextsData.page_size}
          currentPage={contextsData.page}
          onPageChange={onPageChange}
          containerHeight={paginationHeight}
        />
      ) : (
        <Box height={paginationHeight} />
      )}
    </Stack>
  );
};

ContextListSection.displayName = "ContextListSection";
