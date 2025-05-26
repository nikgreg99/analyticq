import axios from "axios";
import { API_BASE_URL } from "../config"; // Import base URL from config

/**
 * Axios instance for making HTTP requests to the contexts endpoint.
 * @constant {import('axios').AxiosInstance} context_api
 * @description Creates a configured Axios instance for interacting with the contexts API endpoints.
 * The instance is pre-configured with:
 * - Base URL pointing to the contexts endpoint
 * - JSON content type header
 */
const context_api = axios.create({
  baseURL: `${API_BASE_URL}/contexts`,
  headers: {
    "Content-Type": "application/json",
  },
});

/**
 * Retrieves all contexts from the context API.
 * @async
 * @function getAllContexts
 * @returns {Promise<Array>} A promise that resolves to an array of context objects from the API
 */
export const getAllContexts = async (options = {}) => {
  const { page, pageSize } = options;
  let queryParams = {};

  if (page !== undefined) {
    queryParams.page = page;
  }

  if (pageSize !== undefined) {
    queryParams.page_size = pageSize;
  }

  return await context_api
    .get("/", { params: queryParams })
    .then((res) => res.data);
};

export const getContextById = async (id) =>
  context_api.get(`/${id}`).then((res) => res.data);

/**
 * Retrieves a context by its ID from the context API.
 * @param {string|number} id - The unique identifier of the context to retrieve.
 * @returns {Promise<Object>} A promise that resolves with the context data.
 * @throws {Error} If the API request fails.
 */
export const getContextByRepoName = async (repoName) =>
  context_api.get(`/repo/${repoName}`).then((res) => res.data);

export const getContextByRepoNamePrefix = async (prefix) =>
  context_api.get(`/repo/prefix/${prefix}`).then((res) => res.data);

/**
 * Retrieves statistics for a specific context by its ID.
 * @param {string|number} contextId - The unique identifier of the context.
 * @returns {Promise<Object>} A promise that resolves to the statistics data for the context.
 * @throws {Error} If the API request fails.
 */
export const getStatsByContextId = async (contextId) =>
  context_api.get(`/${contextId}/stats`).then((res) => res.data);

/**
 * Fetches contexts based on a repository name prefix
 * @param {string} prefix - The prefix to search for in repository names
 * @returns {Promise<Object[]>} A promise that resolves to an array of context objects matching the prefix
 * @throws {Error} If the API request fails
 */
export const getScansByRepoName = async (repoName) =>
  context_api.get(`/${repoName}/scans`).then((res) => res.data);

/**
 * Deletes a context associated with the specified repository name.
 * @param {string} repoName - The name of the repository whose context should be deleted.
 * @returns {Promise<void>} A promise that resolves when the context is deleted successfully.
 * @throws {Error} If the deletion operation fails.
 */
export const deleteContextByRepoName = async (repoName) =>
  context_api.delete(`/${repoName}`).then((res) => res.data);
