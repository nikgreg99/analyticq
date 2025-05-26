const LANGUAGE_DISPLAY_NAMES = {
  javascript: "JavaScript",
  js: "JS",
  typescript: "TypeScript",
  php: "PHP",
  html: "HTML",
  css: "CSS",
  json: "JSON",
  xml: "XML",
  sql: "SQL",
};

/**
 * Capitalizes the first letter of a given string.
 * @param {string} string - The input string to capitalize.
 * @returns {string} The input string with its first letter capitalized.
 */
export const capitalizeFirstLetter = (string) => {
  return string.charAt(0).toUpperCase() + string.slice(1);
};

/**
 * Formats a language name to its display form using predefined mappings or capitalization.
 * @param {string} lang - The language identifier to format.
 * @returns {string} The formatted language name. If the language exists in LANGUAGE_DISPLAY_NAMES,
 * returns the mapped display name, otherwise returns the input with its first letter capitalized.
 */
export const formatLanguageName = (lang) => {
  const key = lang.toLowerCase();
  return LANGUAGE_DISPLAY_NAMES[key] || capitalizeFirstLetter(lang);
};
