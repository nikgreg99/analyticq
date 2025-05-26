import { useMemo } from "react";
import { createListCollection } from "@chakra-ui/react";
import { formatLanguageName } from "components/utils/strings";

/**
 * Custom hook to generate tool options for a Select dropdown from a list of languages.
 *
 * @param {Array} languages - Array of language objects, each with a `tools` array.
 * @returns {Object} A Chakra UI Select-compatible collection with tool options.
 */
const useToolOptions = (languages) => {
  return useMemo(() => {
    if (!languages)
      return createListCollection({ items: [{ label: "All", value: "all" }] });

    const uniqueTools = Array.from(
      new Set(languages.flatMap((lang) => lang.tools)),
    ).sort();

    return createListCollection({
      items: [
        { label: "All", value: "all" },
        ...uniqueTools.map((tool) => ({
          label: formatLanguageName(tool),
          value: tool,
        })),
      ],
    });
  }, [languages]);
};

export default useToolOptions;
