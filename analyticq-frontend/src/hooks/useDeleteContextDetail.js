import { useState, useRef } from "react";
import { useNavigate } from "react-router-dom";
import { deleteContextByRepoName } from "services/contextService";
import { toaster } from "components/ui/general/Toaster";

/**
 * Custom hook for handling context deletion
 * @param {string} contextId - The ID of the context
 * @param {object} contextData - Data about the context
 * @returns {object} - Delete-related state and handlers
 */
export const useDeleteContext = (contextId, contextData) => {
  const navigate = useNavigate();
  const cancelRef = useRef();

  const [isOpenModal, setIsOpenModal] = useState(false);
  const [deleteLoading, setDeleteLoading] = useState(false);

  const handleDeleteConfirm = async () => {
    try {
      setDeleteLoading(true);
      await deleteContextByRepoName(contextData?.repo_name);

      toaster.success({
        title: "Deletion successful",
        description: `Context ${contextData?.repo_name} has been deleted`,
      });

      navigate("/contexts");
    } catch (err) {
      console.error("Error deleting context:", err);
      toaster.error({
        title: "Deletion failed",
        description: "Failed to delete context. Please try again.",
      });
    } finally {
      setDeleteLoading(false);
    }
  };

  return {
    isOpenModal,
    setIsOpenModal,
    deleteLoading,
    handleDeleteConfirm,
    cancelRef,
  };
};
