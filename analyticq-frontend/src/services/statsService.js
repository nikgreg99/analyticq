import axios from "axios";
import { API_BASE_URL } from "config";

/**
 * Axios instance configured for making HTTP requests to the stats API endpoint.
 * @constant {AxiosInstance}
 * @default
 * @example
 * // Making a GET request using stats_api
 * stats_api.get('/some-endpoint')
 *   .then(response => console.log(response.data))
 *   .catch(error => console.error(error));
 */
const stats_api = axios.create({
  baseURL: `${API_BASE_URL}/stats`,
  headers: {
    "Content-Type": "application/json",
  },
});

/**
 * Retrieves statistics data for a specific stats ID
 * @param {string|number} statsId - The unique identifier for the statistics to retrieve
 * @returns {Promise<Object>} A promise that resolves with the statistics data
 * @throws {Error} If the API request fails
 */
export const getStats = async (statsId) =>
  stats_api.get(`/${statsId}`).then((res) => res.data);

/**
 * Deletes statistics entry by its ID.
 * @param {string|number} statsId - The ID of the statistics entry to delete.
 * @returns {Promise} A promise that resolves when the deletion is complete.
 */
export const deleteStats = async (statsId) => stats_api.delete(`/${statsId}`);
