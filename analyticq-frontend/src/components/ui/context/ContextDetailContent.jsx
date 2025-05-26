import React from "react";
import RepositoryInfoCard from "components/ui/context/RepositoryInfoCard";
import { ScanResultList } from "components/ui/scan/ScanResultList";
import ContextDetailActions from "components/ui/context/ContextDetailAction";

/**
 * Component that renders the detailed content of a repository context.
 *
 * @param {Object} props - The component props
 * @param {Object} props.contextData - Data object containing repository context information
 * @param {boolean} props.isOpenModal - Controls the visibility state of the deletion modal
 * @param {function} props.setIsOpenModal - Function to update the modal visibility state
 * @param {boolean} props.deleteLoading - Loading state for delete operation
 * @param {function} props.handleDeleteConfirm - Handler function for confirming deletion
 * @param {Object} props.cancelRef - React ref object for the cancel button
 * @param {function} props.navigateToStats - Function to navigate to statistics page
 * @returns {JSX.Element|null} Returns null if contextData is not provided, otherwise returns the context detail content
 */
const ContextDetailContent = ({
  contextData,
  isOpenModal,
  setIsOpenModal,
  deleteLoading,
  handleDeleteConfirm,
  cancelRef,
  navigateToStats,
}) => {
  if (!contextData) return null;

  return (
    <>
      <RepositoryInfoCard contextData={contextData} />
      <ScanResultList repoName={contextData.repo_name} />
      <ContextDetailActions
        repoName={contextData.repo_name}
        isOpenModal={isOpenModal}
        setIsOpenModal={setIsOpenModal}
        isLoading={deleteLoading}
        onConfirm={handleDeleteConfirm}
        cancelRef={cancelRef}
        onStatsClick={navigateToStats}
      />
    </>
  );
};

ContextDetailContent.displayName = "ContextDetailContent";

export default ContextDetailContent;
