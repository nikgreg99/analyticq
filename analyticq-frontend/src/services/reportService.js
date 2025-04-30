import axios from "axios";
import { API_BASE_URL } from "config";

const report_api = axios.create({
  baseURL: `${API_BASE_URL}/reports`,
  responseType: "blob"
});

/**
 * Extracts or generates a filename for a report
 * @param {string} contentDisposition - The Content-Disposition header value from HTTP response
 * @param {string} scanId - The ID of the scan
 * @param {string} format - The file format extension
 * @returns {string} The extracted filename from Content-Disposition or a generated filename in the format "analyticq_report_[scanId]_[date].[format]"
 */
const getFileName = (contentDisposition, scanId, format) => {
  if (contentDisposition) {
    const filenameMatch = contentDisposition.match(/filename=([^;]+)/);
    if (filenameMatch) return filenameMatch[1].trim();
  }

  return `analyticq_report_${scanId}_${new Date()
    .toISOString()
    .slice(0, 10)
    .replace(/-/g, "")}.${format}`;
};

/**
 * Downloads a scan report in the specified format.
 *
 * @async
 * @param {string} scanId - The unique identifier of the scan.
 * @param {string} format - The desired format of the report (e.g., 'pdf', 'csv').
 * @returns {Promise<{data: Blob, fileName: string}>} An object containing the report data as a Blob and the generated filename.
 * @throws {Error} If the API request fails.
 */
export const downloadScanReportService = async (scanId, format) => {
  const response = await report_api.get(`/download/${scanId}`, {
    params: { format },
    responseType: "blob"
  });

  const fileName = getFileName(response.headers["content-disposition"], scanId, format);
  return { data: response.data, fileName };
};
