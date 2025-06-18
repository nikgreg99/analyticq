import React, { useEffect } from "react";
import { Box, Heading } from "@chakra-ui/react";
import { useNavigate } from "react-router-dom";
import { updatePageMetadata } from "components/utils/metadata";
import { Toaster } from "components/ui/general/Toaster";
import LoadingSpinner from "components/ui/general/LoadingSpinner";
import ErrorDisplay from "components/layout/ErrorDisplay";
import BackButton from "components/ui/general/BackButton";
import EmptyState from "components/layout/EmptyState";
import { ContextListSection } from "components/ui/context/ContextListSection";

import { useContextsData } from "../hooks/useContextsData";

/**
 * Displays all analyzed codebase contexts with search and pagination.
 */
export const ContextsPage = () => {
  const navigate = useNavigate();
  const {
    loading,
    error,
    searchQuery,
    filteredContexts,
    contextsData,
    isInitialEmpty,
    isEmptySearchResult,
    handlePageChange,
  } = useContextsData();

  useEffect(() => {
    updatePageMetadata(
      "Codebase Homepage",
      "All contexts analyzed",
      "/contexts",
    );
  }, []);

  if (isInitialEmpty) {
    return (
      <EmptyState
        title="Repository Contexts"
        message="There are currently no repository contexts in the system. Please add a repository to get started."
        role="region"
        aria-label="Emtpy repository context state"
      />
    );
  }

  if (error) {
    return (
      <ErrorDisplay
        title="Contexts"
        error={error}
        role="region"
        backButton={
          <BackButton onClick={() => navigate("/")} label="Back to Home" />
        }
        aria-live="assertive"
      />
    );
  }

  return (
    <Box as="main" p={6} aria-labelledby="contexts-page-handling">
      <Heading size="lg" mb={4} textAlign="center" color="blackAlpha.800">
        Codebase Analyzed
      </Heading>

      {loading ? (
        <LoadingSpinner aria-busy="true"  aria-label="Loading repository contexts"/>
      ) : (
        <ContextListSection
          filteredContexts={filteredContexts}
          hasPagination={!searchQuery || searchQuery.length <= 3}
          contextsData={contextsData}
          onPageChange={handlePageChange}
          searchQuery={searchQuery}
          isEmptySearchResult={isEmptySearchResult}
        />
      )}
      <Toaster />
    </Box>
  );
};

ContextsPage.displayName = "ContextsPage";
