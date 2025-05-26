import { useCallback, useEffect, useState } from "react";
import { getIssueById, deleteIssue } from "services/issueService";
import { useNavigate } from "react-router-dom";
import { toaster } from "components/ui/general/Toaster";

/**
 * A custom hook for managing issue details, including fetching and deletion operations.
 *
 * @param {string|number} issueId - The unique identifier of the issue
 * @param {Object} [initialIssueData=null] - Optional initial data for the issue
 *
 * @returns {Object} An object containing:
 *   @property {Object} issueData - The current issue data
 *   @property {boolean} loading - Indicates if the issue is being fetched
 *   @property {string|null} error - Error message if fetch operation fails
 *   @property {boolean} deleting - Indicates if the issue is being deleted
 *   @property {Function} fetchIssueById - Function to fetch the issue data
 *   @property {Function} handleDelete - Function to delete the issue
 *
 */
export const useIssueDetails = (issueId, initialIssueData = null) => {
  const [issueData, setIssueData] = useState(initialIssueData);
  const [loading, setLoading] = useState(!initialIssueData);
  const [error, setError] = useState(null);
  const [deleting, setDeleting] = useState(false);
  const navigate = useNavigate();

  const fetchIssueById = useCallback(async () => {
    try {
      setLoading(true);
      const data = await getIssueById(issueId);
      setIssueData(data);
      setError(null);
    } catch (err) {
      console.error("Error fetching issue", err);
      setError("Error fetching issue with ID. Please try again.");
    } finally {
      setLoading(false);
    }
  }, [issueId]);

  const handleDelete = useCallback(async () => {
    try {
      setDeleting(true);
      await deleteIssue(issueId);
      toaster.create({
        title: "Issue Deleted",
        description: `Issue ${issueId} has been successfully deleted`,
        type: "success",
        duration: 5000,
      });
      navigate("/", { replace: true });
    } catch (err) {
      console.error("Error deleting issue", err);
      toaster.create({
        title: "Error Deleting Issue",
        description: "There was an error deleting the issue. Please try again.",
        type: "error",
        duration: 5000,
      });
    } finally {
      setDeleting(false);
    }
  }, [issueId, navigate]);

  useEffect(() => {
    if (!initialIssueData) {
      fetchIssueById();
    }
  }, [fetchIssueById, initialIssueData]);

  return {
    issueData,
    loading,
    error,
    deleting,
    fetchIssueById,
    handleDelete,
  };
};
