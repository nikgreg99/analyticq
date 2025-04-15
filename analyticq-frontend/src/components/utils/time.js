import { format } from "date-fns";

/**
 * Formats a date string into a human-readable format.
 * @param {string} dateString - The date string to format
 * @returns {string} The formatted date string in the format "MMM dd, yyyy HH:mm" or "N/A" if the input is falsy
 * @example
 * // returns "Jan 01, 2024 13:45"
 * formatDate("2024-01-01T13:45:00")
 * // returns "N/A"
 * formatDate(null)
 */
export const formatDate = (dateString) => {
        if (!dateString) return "N/A";
        return format(new Date(dateString), "MMM dd, yyyy HH:mm");
    };

  // Calculate time since scan
  /**
   * Calculates the time elapsed since a given date and returns it in a human-readable format
   * @param {string} dateString - The date string to calculate time since
   * @returns {string} A string describing the elapsed time in days or hours (e.g., "2 days ago" or "5 hours ago")
   * @example
   * getTimeSince("2024-01-01T12:00:00") // returns "5 days ago"
   * getTimeSince("2024-01-06T10:00:00") // returns "2 hours ago"
   */
  export const getTimeSince = (dateString) => {
    console.log(dateString);
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now - date;
    const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));
    const diffHours = Math.floor((diffMs % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));

    if (diffDays > 0) {
      return `${diffDays} day${diffDays > 1 ? 's' : ''} ago`;
    } else {
      return `${diffHours} hour${diffHours > 1 ? 's' : ''} ago`;
    }
  };
