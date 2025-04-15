import axios from "axios";
import { API_BASE_URL } from "config";

/**
 * Axios instance for making HTTP requests to the tools endpoint.
 * @constant {import('axios').AxiosInstance}
 * @description Creates a configured Axios instance for handling tool-related API calls
 * with predefined baseURL and headers.
 */
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
export const getSupportedLanguages = async () =>
    tool_api.get("/supported-languages").then((res) => res.data.languages);

/**
 * Retrieves a list of all available tools from the API.
 * @async
 * @function getAllTools
 * @returns {Promise<Array>} A promise that resolves to an array of tool objects.
 * @throws {Error} If the API request fails.
 */
export const getAllTools = async () =>
    tool_api.get("/list/all").then((res) => res.data.tools);

/**
 * Retrieves all tools for a specific programming language
 * @param {string} language - The programming language to filter tools by
 * @returns {Promise<Array>} A promise that resolves to an array of tools
 * @throws {Error} If the API request fails
 */
export const getAllToolsByLanguage = async (language) =>
    tool_api.get(`/list/${language}`).then((res) => res.data.tools);
