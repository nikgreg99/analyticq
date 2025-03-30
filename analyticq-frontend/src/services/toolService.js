import axios from "axios";
import { API_BASE_URL } from "config";

const tool_api = axios.create({
    baseURL: `${API_BASE_URL}/tools`,
    headers: {
        "Content-Type": "application/json",
    },
});

/**
 * Fetches the list of supported programming languages from the server.
 * @async
 * @function getSupportedLanguages
 * @returns {Promise<string[]>} A promise that resolves to an array of supported programming language names.
 * @throws {Error} If the API request fails.
 */
export const getSupportedLanguages = () =>
    tool_api.get("/supported-languages").then((res) => res.data.languages);

/**
 * Retrieves a list of all available tools from the API.
 * @async
 * @function getAllTools
 * @returns {Promise<Array>} A promise that resolves to an array of tool objects.
 * @throws {Error} If the API request fails.
 */
export const getAllTools = () =>
    tool_api.get("/list/all").then((res) => res.data.tools);

/**
 * Retrieves all tools for a specific programming language
 * @param {string} language - The programming language to filter tools by
 * @returns {Promise<Array>} A promise that resolves to an array of tools
 * @throws {Error} If the API request fails
 */
export const getAllToolsByLanguage = (language) =>
    tool_api.get(`/list/${language}`).then((res) => res.data.toos);
