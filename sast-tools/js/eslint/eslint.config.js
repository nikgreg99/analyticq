module.exports = [
    {
        "root": true,
        files: ["/**/*.js"],
        "extends": ["eslint:recommended", "plugin:@typescript-eslint/recommended", "prettier"],
        "ignores": ["node_modules/**"], // Ignore node_modules
        "env": {
            "es6": true,
            "browser": true,
            "node": true
          },
        "rules": {
            "semi": "error",
            "prefer-const": "error",
        },
        "overrides": [
            {
              "files": ["**/*.js"],
            }
        ]
    },
];
