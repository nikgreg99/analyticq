import React, { useMemo } from "react";

export const useToolComparisonData = (selectedLanguages) => {
  return useMemo(() => {
    const allTools = Array.from(
      new Set(selectedLanguages.flatMap((lang) => lang.tools)),
    ).sort();
    return allTools
      .map((tool) => {
        const supported = selectedLanguages.filter((lang) =>
          lang.tools.includes(tool),
        );
        return {
          tool,
          supportedLanguages: supported.map((l) => l.name),
          supportCount: supported.length,
        };
      })
      .sort((a, b) => b.supportCount - a.supportCount);
  }, [selectedLanguages]);
};
