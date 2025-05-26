import { useState, useEffect, useCallback } from "react";
import { getContextById } from "services/contextService";

/**
 * Custom hook for fetching and managing context details data
 *
 * @param {string|number} contextId - The ID of the context to fetch details for
 * @param {Object|null} initialContextData - Initial context data to use (optional)
 * @returns {Object} Hook state and controls
 * @returns {Object} .contextData - The fetched context data
 * @returns {boolean} .loading - Loading state indicator
 * @returns {string|null} .error - Error message if fetch failed, null otherwise
 * @returns {Function} .refetch - Function to manually trigger a refetch of context data
 *
 * @example
 * const { contextData, loading, error, refetch } = useContextDetailsData(123);
 */
export const useContextDetailsData = (contextId, initialContextData = null) => {
  const [contextData, setContextData] = useState(initialContextData);
  const [loading, setLoading] = useState(!initialContextData);
  const [error, setError] = useState(null);

  const fetchContextDetails = useCallback(async () => {
    if (!contextId) return;
    try {
      setLoading(true);
      const data = await getContextById(contextId);
      setContextData(data);
      setError(null);
    } catch (err) {
      console.error("Error fetching context details:", err);
      setError("Failed to load context details. Please try again later.");
    } finally {
      setLoading(false);
    }
  }, [contextId]);

  useEffect(() => {
    if (!initialContextData || initialContextData.id !== parseInt(contextId)) {
      fetchContextDetails();
    }
  }, [contextId, initialContextData, fetchContextDetails]);

  return { contextData, loading, error, refetch: fetchContextDetails };
};
