import { useCallback, useEffect, useState } from "react";
import { getAllTools } from "services/toolService";
import { formatLanguageName } from "components/utils/strings";

/**
 * A custom hook for managing and exploring programming language tools data.
 *
 * @param {Array} initialLanguagesData - Initial array of language tools data (optional)
 * @returns {Object} An object containing:
 *   @property {Array} languages - Processed array of languages with their associated tools
 *   @property {boolean} loading - Loading state indicator
 *   @property {string|null} error - Error message if any
 *   @property {Function} fetchAllTools - Function to fetch and process all tools data
 *
 */
export const useToolExplorer = (initialLanguagesData) => {
  const [languages, setLanguages] = useState(initialLanguagesData);
  const [loading, setLoading] = useState(!initialLanguagesData);
  const [error, setError] = useState(null);

  const processToolsData = useCallback((data) => {
    const map = {};
    for (const [toolName, langs] of Object.entries(data)) {
      langs.forEach((lang) => {
        const key = lang.toLowerCase();
        if (!map[key]) map[key] = { name: formatLanguageName(lang), tools: [] };
        if (!map[key].tools.includes(toolName)) map[key].tools.push(toolName);
      });
    }
    return Object.values(map);
  }, []);

  const fetchAllTools = useCallback(async () => {
    try {
      setLoading(true);
      const data = await getAllTools();
      setLanguages(processToolsData(data));
      setError(null);
    } catch (err) {
      console.error(err);
      setError("Failed to fetch tools languages. Please try again later.");
    } finally {
      setLoading(false);
    }
  }, [processToolsData]);

  useEffect(() => {
    if (!initialLanguagesData) fetchAllTools();
  }, [initialLanguagesData, fetchAllTools]);

  return { languages, loading, error, fetchAllTools };
};
