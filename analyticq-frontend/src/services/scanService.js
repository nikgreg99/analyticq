import axios from "axios";
import { API_BASE_URL } from "config";

/**
 * Axios instance configured for making HTTP requests to the scans endpoint.
 * @constant {import('axios').AxiosInstance} scans_api
 * @description Creates an Axios instance with predefined configuration for interacting with the scans API.
 * The instance is configured with:
 * - A base URL pointing to the scans endpoint
 * - Default headers specifying JSON as the content type
 */
const scans_api = axios.create({
    baseURL: `${API_BASE_URL}/scans`,
    headers: {
        "Content-Type": "application/json",
    },
});



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
 * Retrieves a scan by its ID from the scans API
 * @param {string|number} id - The unique identifier of the scan to retrieve
 * @returns {Promise<Object>} A promise that resolves to the scan data
 * @throws {Error} If the request fails or the scan is not found
 */
export const getScanById = async (id) =>
    scans_api.get(`/${id}`).then((res) => res.data);


/**
 * Deletes a scan by its ID.
 * @param {string|number} scanId - The unique identifier of the scan to delete.
 * @returns {Promise<AxiosResponse>} A promise that resolves to the response from the API.
 * @throws {AxiosError} When the API call fails.
 */
export const deleteScanById = async (scanId) => scans_api.delete(`/${scanId}`)
