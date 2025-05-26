export const SEVERITY_COLOR = {
  CRITICAL: "red",
  HIGH: "orange",
  MEDIUM: "yellow",
  LOW: "green",
  INFO: "blue",
  WARNING: "teal",
  UNKNOWN: "gray",
};

export const CONFIDENCE_COLOR = {
  CRITICAL: "red",
  HIGH: "orange",
  MEDIUM: "yellow",
  LOW: "green",
  INFO: "blue",
  UNKNOWN: "gray",
};

/**
 * Calculates the count of issues by severity level from scan data.
 * @param {Object} scanData - The scan data object containing issues.
 * @param {Array} [scanData.issues] - Array of issue objects from the scan.
 * @param {string} [scanData.issues[].severity] - Severity level of each issue ('CRITICAL', 'HIGH', 'MEDIUM', 'LOW', 'INFO', or 'UNKNOWN').
 * @returns {Object} An object containing counts for each severity level:
 *                   {critical: number, high: number, medium: number, low: number, info: number, unknown: number}
 */
export const getIssueCounts = (scanData) => {
  if (!scanData || !scanData.issues)
    return {
      high: 0,
      medium: 0,
      low: 0,
      info: 0,
      critical: 0,
      warning: 0,
      unknown: 0,
    };

  return scanData.issues.reduce(
    (counts, issue) => {
      const severity = issue.severity || "UNKNOWN";
      switch (severity.toUpperCase()) {
        case "CRITICAL":
          counts.critical++;
          break;
        case "HIGH":
          counts.high++;
          break;
        case "MEDIUM":
          counts.medium++;
          break;
        case "LOW":
          counts.low++;
          break;
        case "INFO":
          counts.info++;
          break;
        case "WARNING":
          counts.warning++;
          break;
        default:
          counts.unknown++;
          break;
      }
      return counts;
    },
    {
      critical: 0,
      high: 0,
      medium: 0,
      low: 0,
      info: 0,
      warning: 0,
      unknown: 0,
    },
  );
};

/**
 * Filters an array of issues based on a search term
 * @param {Array} issues - The array of issue objects to filter
 * @param {string} searchTerm - The search term to filter issues by
 * @returns {Array} Filtered array of issues that match the search term in title or description
 */
export const filterIssues = (issues, searchTerm) => {
  if (!searchTerm) return issues;

  return issues.filter(
    (issue) =>
      (issue.title &&
        issue.title.toLowerCase().includes(searchTerm.toLowerCase())) ||
      (issue.message &&
        issue.message.toLowerCase().includes(searchTerm.toLowerCase())),
  );
};

// Sort issues based on selected order
/**
 * Sorts an array of issues based on the specified sort order.
 * @param {Array} issues - The array of issue objects to sort.
 * @param {string} sortOrder - The sorting criteria: "severity", "newest", or "oldest".
 * @returns {Array} A new sorted array of issues.
 *
 * @example
 * const issues = [
 *   { severity: "HIGH", createdAt: "2023-01-01" },
 *   { severity: "LOW", createdAt: "2023-02-01" }
 * ];
 * sortIssues(issues, "severity");
 *
 * @description
 * - "severity" order: CRITICAL > HIGH > MEDIUM > LOW > INFO
 * - "newest" order: Most recent date first
 * - "oldest" order: Oldest date first
 */
export const sortIssues = (issues, sortOrder, severityConfig) => {
  if (!issues) return [];

  const sortedIssues = [...issues];

  if (sortOrder === "severity") {
    sortedIssues.sort((a, b) => {
      const severityA = severityConfig[a.severity || "UNKNOWN"].order;
      const severityB = severityConfig[b.severity || "UNKNOWN"].order;
      return severityA - severityB;
    });
  } else if (sortOrder === "newest") {
    sortedIssues.sort(
      (a, b) => new Date(b.createdAt || 0) - new Date(a.createdAt || 0),
    );
  } else if (sortOrder === "oldest") {
    sortedIssues.sort(
      (a, b) => new Date(a.createdAt || 0) - new Date(b.createdAt || 0),
    );
  }

  return sortedIssues;
};

/**
 * Filters and sorts a list of issues based on search criteria and sorting preferences.
 *
 * @param {Array} issues - The array of issues to filter and sort
 * @param {string} searchTerm - The term to filter issues by
 * @param {Array} sortOrder - Array containing sorting criteria, where sortOrder[0] is the primary sort field
 * @param {Object} severityConfig - Configuration object defining severity levels and their order
 * @returns {Array} The filtered and sorted array of issues
 */
export function filterAndSortIssues(
  issues,
  searchTerm,
  sortOrder,
  severityConfig,
) {
  const filtered = filterIssues(issues, searchTerm);
  const sorted = sortIssues(filtered, sortOrder[0], severityConfig);
  return sorted;
}
