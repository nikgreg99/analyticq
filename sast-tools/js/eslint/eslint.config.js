// eslint.config.cjs
module.exports = [
    {
      // Basic linting for all JavaScript files
      files: ["**/*.{js,mjs,cjs}"],
      languageOptions: {
        ecmaVersion: 2022,
        sourceType: "module"
      },
      rules: {
        // Essential rules that most projects would want
        "semi": ["error", "always"],
        "prefer-const": "error",
        "no-unused-vars": "warn",
        "no-console": "warn",
        "no-eval": "error"
      }
    },
    {
      // CommonJS specific settings
      files: ["**/*.cjs"],
      languageOptions: {
        sourceType: "commonjs"
      }
    },
    {
      // Module specific settings
      files: ["**/*.mjs"],
      languageOptions: {
        sourceType: "module"
      }
    }
  ];
