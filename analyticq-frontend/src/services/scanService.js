import axios from "axios";
import { API_BASE_URL } from "config";

const scans_api = axios.create({
    baseURL: `${API_BASE_URL}/scans`,
    headers: {
        "Content-Type": "application/json",
    },
});

export const createScan = (scanData) =>
    scans_api.post("/", scanData).then((res) => res.data)


/**
 * Retrieves filtered scan issues based on specified parameters
 * @param {string} scanId - The ID of the scan to retrieve issues from
 * @param {string} severity - The severity level to filter issues by
 * @param {string} confidence - The confidence level to filter issues by
 * @returns {Promise<Object>} A promise that resolves to the filtered scan issues data
 */
export const getFilteredScanIssues = (scanId, severity, confidence) =>
    scans_api
        .get(`/${scanId}/issues`, {
            params: { severity, confidence },
        })
    .then((res) => res.data)

/**
 * Retrieves scans filtered by tool name from the API
 * @param {string} toolName - The name of the tool to filter scans by
 * @returns {Promise<Array>} A promise that resolves to an array of scan objects
 * @throws {Error} If the API request fails
 */
export const getScansByToolName = (toolName) =>
    scans_api.get(`/tool/${toolName}`).then((res) => res.data);

/**
 * Retrieves scan issues for a specific tool from the API
 * @param {string} toolName - The name of the tool to get issues for
 * @returns {Promise<Array>} Promise that resolves to an array of scan issues
 * @throws {Error} If the API request fails
 */
export const getScanIssuesByToolName = (toolName) =>
    scans_api.get(`/tool/${toolName}/issues`).then((res) => res.data);


/**
 * Deletes a scan by its ID.
 * @param {string|number} scanId - The unique identifier of the scan to delete.
 * @returns {Promise<AxiosResponse>} A promise that resolves to the response from the API.
 * @throws {AxiosError} When the API call fails.
 */
export const deleteScan = (scanId) => scans_api.delete(`/${scanId}`)
