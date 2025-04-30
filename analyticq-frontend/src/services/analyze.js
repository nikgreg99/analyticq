import axios from "axios";
import { API_BASE_URL } from "config";

/**
 * Axios instance for making HTTP requests to the analyze API endpoints.
 * @constant {import('axios').AxiosInstance}
 * @description Creates a pre-configured axios instance with the base URL set to /analyze
 * and default headers for JSON content type.
 */
const analyze_api = axios.create({
    baseURL: `${API_BASE_URL}/analyze`,
    headers: {
      'Content-Type': 'application/json',
    },
});


/**
 * Sends a POST request to analyze a Git repository
 * @async
 * @param {Object} params - The parameters for the Git repository analysis
 * @returns {Promise<Object>} The response from the analysis API
 * @throws {Error} If the API request fails
 */
export const analyzeGitRepo = async (params) => {
    return analyze_api.post('/git', params);
}

export const analyzeFiles = async(params) => {

    const formData = new FormData();
    params.files.forEach(file => {
        formData.append('files', file);
    });

    if(params.config_paths) {
        formData.append('config_paths', JSON.stringify(params.config_paths));
    }


    if(params.timeout) {
        formData.append('timeout', params.timeout);
    }

    return analyze_api.post('/files', formData, {
        headers: {
            'Content-Type': 'multipart/form-data',
        },
    })
}

/**
 * Retrieves the status of a specific analysis.
 * @param {string} analysisId - The unique identifier of the analysis to check.
 * @returns {Promise<Object>} A promise that resolves with the analysis status data.
 * @throws {Error} If the request fails or the analysis is not found.
 */
export const getAnalysisStatus = async (analysisId) => {
    return analyze_api.get(`/status/${analysisId}`);
}
