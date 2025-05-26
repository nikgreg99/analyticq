import React, { useMemo } from "react";

export const useLanguageFilter = (languages, searchTerm, selectedTool) => {
  return useMemo(() => {
    if (!languages) return [];
    return languages.filter((lang) => {
      const matchSearch = lang.name
        .toLowerCase()
        .includes(searchTerm.toLowerCase());
      const matchTool =
        selectedTool[0] === "all" || lang.tools.includes(selectedTool[0]);
      return matchSearch && matchTool;
    });
  }, [languages, searchTerm, selectedTool]);
};
