import React from "react";
import { Box, Flex, Text, VStack } from "@chakra-ui/react";
import { FaClock } from "react-icons/fa6";
import { IssueCard } from "./IssueCard";
import EmptyState from "components/layout/EmptyState";
import { PaginationFooter } from "../general/PaginationFooter";
import { calculatePagination } from "components/utils/pagination";

/**
 * A component that renders a list of security issues with pagination controls
 *
 * @component
 * @param {Object} props
 * @param {Array} props.issues - Array of security issues to display (already filtered and sorted)
 * @param {string} props.sortOrder - Current sort order ('severity', 'newest', 'oldest')
 * @param {Object} props.pageSizeOptions - Collection of page size options
 * @param {Array} props.pageSize - Current page size as an array with one value
 * @param {Function} props.setPageSize - Function to update page size
 * @param {number} props.currentPage - Current page number
 * @param {Function} props.setCurrentPage - Function to update current page
 *
 * @returns {JSX.Element} A component displaying filtered and sorted security issues with pagination
 */
export const IssueListTab = ({
  issues,
  sortOrder,
  pageSizeOptions,
  pageSize,
  setPageSize,
  currentPage,
  setCurrentPage,
}) => {
  if (!issues || issues.length === 0) {
    return (
      <Flex>
        <EmptyState
          title="No issues found"
          message="No issues found for the following scan"
        />
      </Flex>
    );
  }

  const { currentPageData, shouldShowPagination } = calculatePagination(
    issues,
    currentPage,
    pageSize[0],
  );

  const showDateInfo = sortOrder[0] === "newest" || sortOrder[0] === "oldest";

  return (
    <>
      {showDateInfo && (
        <Box mb={4} p={2}>
          <Flex align="center">
            <FaClock style={{ marginRight: "8px", color: "black" }} />
            <Text fontSize="sm" color="blackAlpha.800">
              Issues sorted by {sortOrder[0] === "newest" ? "newest" : "oldest"}{" "}
              first.
            </Text>
          </Flex>
        </Box>
      )}
      <VStack spacing={4} align="stretch" mt={4}>
        {currentPageData.map((issue) => (
          <IssueCard key={issue.id} issue={issue} />
        ))}
      </VStack>
      {shouldShowPagination && (
        <Flex
          justifyContent="space-between"
          alignItems="center"
          mt={6}
          borderTopWidth="1px"
          pt={4}
          pb={2}
          px={1}
          width="100%"
        >
          <PaginationFooter
            totalItems={issues.length}
            pageSize={pageSize}
            setPageSize={setPageSize}
            currentPage={currentPage}
            setCurrentPage={setCurrentPage}
            pageSizeOptions={pageSizeOptions}
          />
        </Flex>
      )}
    </>
  );
};

IssueListTab.displayName = "IssueListTab";
