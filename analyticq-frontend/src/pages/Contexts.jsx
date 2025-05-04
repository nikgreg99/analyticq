import React, { useState, useEffect, useMemo } from "react";
import {
  Box,
  Heading,
  Stack,
  Text
} from "@chakra-ui/react";
import { useDispatch, useSelector } from "react-redux";
import { useNavigate } from "react-router-dom";
import { searchByRepoNamePrefix } from "redux/searchSlice";
import { getAllContexts } from "services/contextService";
import LoadingSpinner from "components/ui/LoadingSpinner";
import ContextList from "components/ui/ContextList";
import EmptyState from "components/layout/EmptyState";
import BackButton from "components/ui/BackButton";
import ErrorDisplay from "components/layout/ErrorDisplay";
import PaginationControls from "components/ui/PaginationControls";
import { updatePageMetadata } from "components/utils/metadata";

export const ContextsPage = () => {
  const PAGE_SIZE_DEFAULT = 10;
  const dispatch = useDispatch();
  const navigate = useNavigate();

  const { searchResults, loading, error, searchQuery } = useSelector((state) => state.search);

  const [contextsData, setContextsData] = useState({
    items: [],
    total: 0,
    page: 1,
    page_size: PAGE_SIZE_DEFAULT,
    has_more: false
  });

  const hasSearch = searchQuery.length > 3;

  // Update page metadata on mount
  useEffect(() => {
    updatePageMetadata("Codebase Homepage", "All contexts analyzed", "/contexts");
  }, []);

  // Fetch context data
  const fetchContexts = async (page = 1, pageSize = PAGE_SIZE_DEFAULT) => {
    try {
      const data = await getAllContexts({ page, pageSize });
      setContextsData(data);
    } catch (err) {
      console.error("Error fetching contexts:", err);
    }
  };

  useEffect(() => {
    fetchContexts();
  }, []);

  // Search when query is long enough
  useEffect(() => {
    if (hasSearch) {
      dispatch(searchByRepoNamePrefix(searchQuery));
    }
  }, [searchQuery, dispatch, hasSearch]);

  const handlePageChange = (newPage) => {
    fetchContexts(newPage, contextsData.page_size);
  };

  const filteredContexts = useMemo(() => {
    if (hasSearch) {
      return searchResults;
    }
    return contextsData.items;
  }, [hasSearch, searchResults, contextsData.items]);

  const isEmptySearchResult = hasSearch && searchResults.length === 0 && !loading;
  const isInitialEmpty = !loading && contextsData.total === 0 && !error;

  if (isInitialEmpty) {
    return (
      <EmptyState
        title="Repository Contexts"
        message="There are currently no repository contexts in the system. Please add a repository to get started."
      />
    );
  }

  return (
    <Box p={6}>
      <Heading
        size="lg"
        mb={4}
        textAlign="center"
        color="blackAlpha.800"
        aria-label="Contexts page heading"
      >
        Codebase Analyzed
      </Heading>

      {error ? (
        <ErrorDisplay
          title="Contexts"
          error={error}
          backButton={<BackButton onClick={() => navigate("/")} label="Back to Home" />}
        />
      ) : loading ? (
        <LoadingSpinner />
      ) : (
        <Stack width="full" gap={5}>
          {filteredContexts.length > 0 ? (
            <>
              <ContextList contexts={filteredContexts} />
              {!hasSearch && (
                <PaginationControls
                  total={contextsData.total}
                  pageSize={contextsData.page_size}
                  currentPage={contextsData.page}
                  onPageChange={handlePageChange}
                />
              )}
            </>
          ) : (
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
          )}
        </Stack>
      )}
    </Box>
  );
};

export default ContextsPage;
