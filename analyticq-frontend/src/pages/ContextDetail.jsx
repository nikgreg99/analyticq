import React, { useEffect, useCallback } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { Box } from "@chakra-ui/react";

import { capitalizeFirstLetter } from "components/utils/strings";
import { updatePageMetadata } from "components/utils/metadata";

import { useContextDetailsData } from "hooks/useContextDetailsData";
import { useDeleteContext } from "hooks/useDeleteContextDetail";
import LoadingSpinner from "components/ui/general/LoadingSpinner";
import ErrorDisplay from "components/layout/ErrorDisplay";
import BackButton from "components/ui/general/BackButton";

import ContextDetailHeader from "components/ui/context/ContextDetailHeader";
import ContextDetailContent from "components/ui/context/ContextDetailContent";

export const ContextDetailPage = ({ initialContextData = null }) => {
  const { contextId } = useParams();
  const navigate = useNavigate();

  const { contextData, loading, error } = useContextDetailsData(
    contextId,
    initialContextData,
  );

  const {
    isOpenModal,
    setIsOpenModal,
    deleteLoading,
    handleDeleteConfirm,
    cancelRef,
  } = useDeleteContext(contextId, contextData);

  const handleClickBack = useCallback(() => navigate(-1), [navigate]);

  const navigateToStats = () => {
    if (contextData) {
      navigate(
        `/contexts/${contextId}/stats?repo=${encodeURIComponent(contextData.repo_name)}`,
      );
    }
  };

  useEffect(() => {
    if (contextData) {
      const title = `${capitalizeFirstLetter(contextData.repo_name)} - Overview`;
      updatePageMetadata(
        title,
        contextData.repo_name,
        `/contexts/${contextId}`,
      );
    }
  }, [contextData, contextId]);

  if (loading) return <LoadingSpinner />;

  if (error) {
    return (
      <ErrorDisplay
        title="Context Details"
        error={error}
        backButton={
          <BackButton onClick={handleClickBack} label="Back to Contexts" />
        }
      />
    );
  }

  return (
    <Box p={{ base: 4, md: 6 }} mx="auto" maxW="1200px">
      <ContextDetailHeader contextId={contextData?.id} />
      <ContextDetailContent
        contextData={contextData}
        isOpenModal={isOpenModal}
        setIsOpenModal={setIsOpenModal}
        deleteLoading={deleteLoading}
        handleDeleteConfirm={handleDeleteConfirm}
        cancelRef={cancelRef}
        navigateToStats={navigateToStats}
      />
    </Box>
  );
};

ContextDetailPage.displayName = "ContextDetailPage";
