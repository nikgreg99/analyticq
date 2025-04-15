import axios from "axios";
import { API_BASE_URL } from "config";

/**
 * Axios instance for making HTTP requests to the issues endpoint.
 * @constant {import('axios').AxiosInstance}
 * @description Creates a pre-configured Axios instance for handling issue-related API calls
 * with base URL set to the issues endpoint and JSON content type header.
 */
const issue_api = axios.create({
    baseURL: `${API_BASE_URL}/issues`,
    headers: {
        "Content-Type": "application/json",
    },
});

/**
 * Retrieves an issue by its ID from the API.
 * @param {string|number} issueId - The unique identifier of the issue to retrieve
 * @returns {Promise<Object>} A promise that resolves to the issue data
 * @throws {Error} If the API request fails
 */
export const getIssueById = async (issueId) =>  issue_api.get(`/${issueId}`).then((res) => res.data);

/**
 * Updates an existing issue in the system
 * @param {string|number} issueId - The unique identifier of the issue to update
 * @param {Object} updateData - The data to update the issue with
 * @returns {Promise<Object>} A promise that resolves to the updated issue data
 * @throws {Error} If the API request fails
 */
export const updateIssue = (issueId, updateData) => issue_api.put(`/${issueId}`, updateData).then((res) => res.data);

/**
 * Deletes an issue by its ID.
 * @param {string|number} issueId - The unique identifier of the issue to delete
 * @returns {Promise} A promise that resolves when the issue is successfully deleted
 * @throws {Error} If the deletion request fails
 */
export const deleteIssue = async (issueId) => issue_api.delete(`/${issueId}`);
