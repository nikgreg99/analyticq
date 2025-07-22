import { useState } from "react";
import { downloadScanReportService } from "services/reportService";

/**
 * Custom hook for downloading scan reports.
 * @returns {Object} An object containing:
 *   - downloadReport: {Function} Async function to download a report
 *     @param {string|number} scanId - The ID of the scan to download
 *     @param {string} [format="pdf"] - The desired format of the report
 *     @returns {Promise<Blob>} The downloaded report data
 *   - isDownloading: {boolean} Indicates if a download is in progress
 *   - error: {Error|null} Error object if download fails, null otherwise
 * @throws {Error} If the download fails
 */
export const useDownloadScanReport = () => {
  const [isDownloading, setIsDownloading] = useState(false);
  const [error, setError] = useState(null);

  const downloadReport = async (scanId, repoName, format = "pdf") => {
    setIsDownloading(true);
    setError(null);

    try {
      const { data, fileName } = await downloadScanReportService(
        scanId,
        repoName,
        format,
      );

      const url = window.URL.createObjectURL(data);
      const link = document.createElement("a");
      link.href = url;
      link.setAttribute("download", fileName);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);

      return data;
    } catch (err) {
      console.error("Error downloading report:", err);
      setError(err);
      throw err;
    } finally {
      setIsDownloading(false);
    }
  };

  return { downloadReport, isDownloading, error };
};
