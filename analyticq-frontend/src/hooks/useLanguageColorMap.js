import { useMemo } from "react";
import { generateColorFromString } from "components/utils/colors";

/**
 * A custom hook that generates a mapping of programming languages to colors.
 *
 * @param {Object} languageStats - An object containing programming language statistics.
 *                                The keys are language names and values are their corresponding stats.
 * @returns {Object} A memoized object mapping language names to their generated colors.
 *                   The colors are consistently generated based on the language name and position.
 */
export const useLanguageColorMap = (languageStats = {}) => {
  return useMemo(() => {
    const languages = Object.keys(languageStats).sort();
    return languages.reduce((acc, language, index) => {
      acc[language] = generateColorFromString(
        language,
        index,
        languages.length,
      );
      return acc;
    }, {});
  }, [languageStats]);
};
