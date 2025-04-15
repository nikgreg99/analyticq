
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
