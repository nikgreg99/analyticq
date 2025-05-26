import { createListCollection } from "@chakra-ui/react";

export const DEFAULT_PAGE_SIZE_OPTIONS = createListCollection({
  items: [
    { label: "5 per page", value: "5" },
    { label: "10 per page", value: "10" },
    { label: "20 per page", value: "20" },
  ],
});

/**
 * Calculate pagination details based on current state
 *
 * @param {Array} items - The full list of items to paginate
 * @param {number} currentPage - Current page number
 * @param {string|number} pageSize - Number of items per page
 * @returns {Object} Pagination details including currentPageData, totalPages, etc.
 */
export const calculatePagination = (items, currentPage, pageSize) => {
  const parsedPageSize = parseInt(pageSize);
  const totalItems = items.length;
  const totalPages = Math.ceil(totalItems / parsedPageSize);
  const startIndex = (currentPage - 1) * parsedPageSize;
  const endIndex = Math.min(startIndex + parsedPageSize, totalItems);
  const currentPageData = items.slice(startIndex, endIndex);

  return {
    totalItems,
    totalPages,
    startIndex,
    endIndex,
    currentPageData,
    shouldShowPagination: totalItems >= parsedPageSize,
  };
};
