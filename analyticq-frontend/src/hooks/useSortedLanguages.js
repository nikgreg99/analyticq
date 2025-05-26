import { useMemo } from "react";

/**
 * Custom hook that sorts language statistics by file count in descending order.
 *
 * @param {Object} languageStats - An object containing language statistics where each key is a language
 *                                and each value is an object containing file_count.
 * @returns {Array} A sorted array of [language, stats] pairs, ordered by file_count in descending order.
 *
 */
export const useSortedLanguages = (languageStats = {}) => {
  return useMemo(() => {
    return Object.entries(languageStats).sort(
      (a, b) => b[1].file_count - a[1].file_count,
    );
  }, [languageStats]);
};
