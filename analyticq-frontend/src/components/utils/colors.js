/**
 * Generates a color name from a string input using a hash function and a predefined color scheme.
 * @param {string} str - The input string to generate a color from
 * @param {number} index - An additional index to affect color selection
 * @returns {string} A color name from the predefined color schemes array
 * @example
 * generateColorFromString("test", 0) // returns a color like 'blue', 'green', etc.
 */
export const generateColorFromString = (str, index) => {
  const colorSchemes = [
    "blue",
    "green",
    "red",
    "purple",
    "orange",
    "teal",
    "pink",
    "cyan",
    "yellow",
    "gray",
  ];

  let hash = 0;
  for (let i = 0; i < str.length; i++) {
    hash = str.charCodeAt(i) + ((hash << 5) - hash);
  }

  const colorIndex = (Math.abs(hash) + index) % colorSchemes.length;
  return colorSchemes[colorIndex];
};
