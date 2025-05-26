import { useState, useMemo } from "react";
import { filterAndSortIssues } from "components/utils/issues";

export const useIssueTabs = (issues, severityConfig) => {
  const [searchTerm, setSearchTerm] = useState("");
  const [sortOrder, setSortOrder] = useState(["severity"]);
  const [activeTab, setActiveTab] = useState("all");
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize, setPageSize] = useState([10]);

  const issueCounts = useMemo(() => {
    return issues.reduce(
      (acc, issue) => {
        const sev = issue.severity || "UNKNOWN";
        acc[sev.toLowerCase()] = (acc[sev.toLowerCase()] || 0) + 1;
        return acc;
      },
      Object.fromEntries(
        Object.keys(severityConfig).map((k) => [k.toLowerCase(), 0]),
      ),
    );
  }, [issues, severityConfig]);

  const tabsConfig = useMemo(() => {
    return [
      {
        id: "all",
        label: "All Issues",
        count: issues.length || 0,
        color: "blue",
        filter: () => issues,
      },
      ...Object.entries(severityConfig)
        .filter(([severity]) => issueCounts[severity.toLowerCase()] > 0)
        .sort(([, a], [, b]) => a.order - b.order)
        .map(([k, config]) => ({
          id: k,
          label: config.displayName,
          count: issueCounts[k.toLowerCase()],
          color: config.color,
          filter: () => issues.filter((i) => i.severity === k),
        })),
    ];
  }, [issues, issueCounts, severityConfig]);

  const filteredSortedTabIssues = useMemo(() => {
    const result = {};
    for (const tab of tabsConfig) {
      result[tab.id] = filterAndSortIssues(
        tab.filter(),
        searchTerm,
        sortOrder,
        severityConfig,
      );
    }
    return result;
  }, [tabsConfig, searchTerm, sortOrder, severityConfig]);

  return {
    searchTerm,
    setSearchTerm,
    sortOrder,
    setSortOrder,
    activeTab,
    setActiveTab,
    currentPage,
    setCurrentPage,
    pageSize,
    setPageSize,
    tabsConfig,
    filteredSortedTabIssues,
  };
};
