
/**
 * Formats a number of bytes into a human-readable string with units
 * @param {number} bytes - The number of bytes to format
 * @param {number} [decimals=1] - Number of decimal places to show in the formatted output
 * @returns {string} Formatted string with appropriate unit (e.g., "1.5 MB")
 * @example
 * formatBytes(1234); // returns "1.2 KB"
 * formatBytes(1234567); // returns "1.2 MB"
 * formatBytes(0); // returns "0 Bytes"
 */
export function formatBytes(bytes, decimals = 1) {
  if (bytes === 0) return '0 Bytes';

  const k = 1024;
  const dm = decimals < 0 ? 0 : decimals;
  const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];

  const i = Math.floor(Math.log(bytes) / Math.log(k));

  return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
}

/**
 * Extracts the file name from a file path string.
 * @param {string} path - The full file path string using Windows-style backslashes
 * @returns {string} The extracted file name without the path
 * @example
 * getFileName("c:\\folder\\file.txt") // returns "file.txt"
 */
export function getFileName(path) {
  return path.split('\\').pop();
}

/**
 * Extracts the file name with extension from a full file path.
 *
 * @param {string} path - Full file path (e.g., "/src/components/MyFile.test.jsx")
 * @returns {string} The file name with extension (e.g., "MyFile.test.jsx")
 */
export function getFileNameFromPath(path){
  if (typeof path !== "string") return "";
  return path.split("/").pop();
}

/**
 * Extracts and returns the file extension from a given filename.
 * @param {string} file - The filename to extract the extension from
 * @returns {string} The lowercase file extension without the dot, or an empty string if no extension is found or if input is not a string
/** */
export function getFileExtension(file){
  if (typeof file !== 'string') return '';

  const parts = file.split('.');
  return parts.length > 1 ? parts.pop().toLowerCase() : '';
}
