import axios from "axios";
import { API_BASE_URL } from "../config"; // Import base URL from config

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
export const getAllContexts = (options = {}) => {
    const { page, pageSize } = options;
    let queryParams = {};

    if (page !== undefined) {
        queryParams.page = page;
    }

    if (pageSize !== undefined) {
        queryParams.page_size = pageSize;
     }


    return context_api.get("/", { params: queryParams }).
        then((res) => res.data);
}

/**
 * Retrieves context information for a specific repository by its name.
 * @param {string} repoName - The name of the repository to fetch context for.
 * @returns {Promise<Object>} A promise that resolves to the repository context data.
 * @throws {Error} If the API request fails.
 */
export const getContextByRepoName = (repoName) =>
    context_api.get(`/${repoName}`).then((res) => res.data);

/**
 * Retrieves all scans associated with a specific repository context
 * @param {string} repoName - The name of the repository to fetch scans for
 * @returns {Promise<Array>} A promise that resolves to an array of scan objects
 * @throws {Error} If the API request fails
 */
export const getScansByContext = (repoName) =>
    context_api.get(`/${repoName}/scans`).then((res) => res.data);


/**
 * Deletes a context associated with the specified repository name.
 * @param {string} repoName - The name of the repository whose context should be deleted.
 * @returns {Promise<void>} A promise that resolves when the context is deleted successfully.
 * @throws {Error} If the deletion operation fails.
 */
export const deleteContext = (repoName) => context_api.delete(`/${repoName}`)
