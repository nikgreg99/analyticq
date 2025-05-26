import { useCallback, useEffect, useState } from "react";
import { getStatsByContextId } from "services/contextService";

/**
 * Custom hook for managing context statistics data.
 *
 * @param {Object} params - The parameters object
 * @param {string|number} params.contextId - The ID of the context to fetch stats for
 * @param {Object} [params.initStatsData] - Initial statistics data (optional)
 * @param {number} [params.initStatsData.context_id] - The context ID within the initial stats data
 *
 * @returns {Object} An object containing:
 *   @property {Object} statsData - The current statistics data
 *   @property {boolean} loading - Indicates if data is currently being fetched
 *   @property {string|null} error - Error message if fetch failed, null otherwise
 *   @property {Function} fetchStats - Function to manually trigger stats refresh
 *
 * @throws {Error} When the stats fetching fails
 */
export const useContextStats = ({ contextId, initStatsData }) => {
  const DEFAULT_RADIX_INT = 10;

  const [statsData, setStatsData] = useState(initStatsData);
  const [loading, setLoading] = useState(!initStatsData);
  const [error, setError] = useState(null);

  const fetchStats = useCallback(async () => {
    try {
      setLoading(true);
      const data = await getStatsByContextId(contextId);
      setStatsData(data);
      setError(null);
    } catch (err) {
      console.error("Error fetching stat details:", err);
      setError(
        `Failed to load context stats details related to context with id ${contextId}. Please try again later.`,
      );
    } finally {
      setLoading(false);
    }
  }, [contextId]);

  useEffect(() => {
    if (
      !initStatsData ||
      initStatsData.context_id !== parseInt(contextId, DEFAULT_RADIX_INT)
    ) {
      fetchStats();
    }
  }, [contextId, initStatsData, fetchStats]);

  return { statsData, loading, error, fetchStats };
};
