import axios from "axios";
import { API_BASE_URL } from "config";

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
export const getStats =(statsId) =>
    stats_api.get(`/${statsId}`).then((res) => res.data);


/**
 * Retrieves the context information for a specific stats ID.
 * @param {string|number} statsId - The unique identifier of the stats.
 * @returns {Promise<Object>} A promise that resolves to the context data.
 * @throws {Error} If the API request fails.
 */
export const getContextByStatsId = (statsId) =>
    stats_api.get(`/${statsId}/context`).then((res) => res.data);


/**
 * Deletes statistics entry by its ID.
 * @param {string|number} statsId - The ID of the statistics entry to delete.
 * @returns {Promise} A promise that resolves when the deletion is complete.
 */
export const deleteStats = (statsId) =>
    stats_api.delete(`/${statsId}`);
