import { useState, useEffect, useCallback, useMemo } from "react";
import { useDispatch, useSelector } from "react-redux";
import { useDebounce } from "use-debounce";
import { searchByRepoNamePrefix } from "redux/searchSlice";
import { getAllContexts } from "services/contextService";
import { toaster } from "components/ui/general/Toaster";

const PAGE_SIZE_DEFAULT = 10;

/**
 * Custom hook for managing and fetching context data with search functionality.
 *
 * @returns {Object} An object containing:
 *   @property {string} searchQuery - Current search query string
 *   @property {boolean} loading - Loading state indicator
 *   @property {string|null} error - Error message if any occurred
 *   @property {Array} filteredContexts - List of contexts filtered by search query
 *   @property {Object} contextsData - Object containing:
 *     @property {Array} items - List of context items
 *     @property {number} total - Total number of contexts
 *     @property {number} page - Current page number
 *     @property {number} page_size - Number of items per page
 *     @property {boolean} has_more - Indicates if more pages are available
 *   @property {boolean} isInitialEmpty - Indicates if there are no contexts initially
 *   @property {boolean} isEmptySearchResult - Indicates if search returned no results
 *   @property {Function} handlePageChange - Function to handle pagination
 */
export const useContextsData = () => {
  const dispatch = useDispatch();

  const { searchResults, loading, error, searchQuery } = useSelector(
    (state) => state.search,
  );

  const [debouncedSearchQuery] = useDebounce(searchQuery, 400);
  const hasSearch = searchQuery.length > 3;

  const [contextsData, setContextsData] = useState({
    items: [],
    total: 0,
    page: 1,
    page_size: PAGE_SIZE_DEFAULT,
    has_more: false,
  });

  const [localError, setLocalError] = useState(null);

  const fetchContexts = useCallback(
    async (page = 1, pageSize = PAGE_SIZE_DEFAULT) => {
      try {
        const data = await getAllContexts({ page, pageSize });
        setContextsData(data);
        setLocalError(null);
      } catch (err) {
        console.error("Failed to fetch codebase:", err);
        setLocalError("Failed to fetch codebase");
        toaster.create({
          title: "Error Fetching Contexts",
          description:
            "An error occurred while retrieving context data. Please try again later.",
          type: "error",
          duration: 5000,
        });
      }
    },
    [],
  );

  useEffect(() => {
    if (debouncedSearchQuery.length > 3) {
      dispatch(searchByRepoNamePrefix(debouncedSearchQuery));
    }
  }, [debouncedSearchQuery, dispatch]);

  useEffect(() => {
    fetchContexts();
  }, [fetchContexts]);

  const handlePageChange = (newPage) => {
    fetchContexts(newPage, contextsData.page_size);
  };

  const filteredContexts = useMemo(() => {
    return hasSearch ? searchResults : contextsData.items;
  }, [hasSearch, searchResults, contextsData.items]);

  const isEmptySearchResult =
    hasSearch && searchResults.length === 0 && !loading;
  const isInitialEmpty = !loading && contextsData.total === 0 && !error;

  return {
    searchQuery,
    loading,
    error: error || localError,
    filteredContexts,
    contextsData,
    isInitialEmpty,
    isEmptySearchResult,
    handlePageChange,
  };
};
