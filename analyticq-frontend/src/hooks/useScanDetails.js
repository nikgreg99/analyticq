import { useState, useEffect, useCallback } from "react";
import { getScanById } from "services/scanService";

/**
 * Custom hook to fetch and manage scan details.
 *
 * @param {string|number} scanId - The ID of the scan to fetch
 * @param {Object} [initialScanData] - Optional initial scan data to use instead of fetching
 * @param {number} initialScanData.id - The ID of the initial scan data
 *
 * @returns {Object} An object containing:
 *   @returns {Object|null} scanData - The fetched scan data or null if not loaded
 *   @returns {Object} status - Current status of the fetch operation
 *   @returns {boolean} status.loading - Whether the data is currently being fetched
 *   @returns {string|null} status.error - Error message if fetch failed, null otherwise
 *
 * @throws {Error} When the scan fetch operation fails
 *
 */
export const useScanDetails = (scanId, initialScanData) => {
  const [scanData, setScanData] = useState(initialScanData || null);
  const [status, setStatus] = useState({
    loading: !initialScanData,
    error: null,
  });

  const fetchScanDetails = useCallback(async () => {
    if (initialScanData?.id === parseInt(scanId)) {
      setScanData(initialScanData);
      setStatus({ loading: false, error: null });
      return;
    }

    try {
      setStatus({ loading: true, error: null });
      const data = await getScanById(scanId);
      setScanData(data);
      setStatus({ loading: false, error: null });
    } catch (err) {
      console.error("Error fetching scan details:", err);
      const errorMessage =
        err?.response?.status === 404
          ? "Scan not found."
          : "Failed to load scan details. Please try again later.";
      setStatus({
        loading: false,
        error: errorMessage,
      });
    }
  }, [scanId, initialScanData]);

  useEffect(() => {
    fetchScanDetails();
  }, [fetchScanDetails]);

  return { scanData, status };
};
