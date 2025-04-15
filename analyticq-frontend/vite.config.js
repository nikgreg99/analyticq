import react from "@vitejs/plugin-react"
import { defineConfig } from "vite"
import { createHtmlPlugin } from 'vite-plugin-html';
import tsconfigPaths from "vite-tsconfig-paths"

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [
    react(),
    tsconfigPaths(),
    createHtmlPlugin({
      minify: true,
      inject: {
        data: {
          SITE_NAME: 'AnalyticQ Frontend',
          AUTHOR: 'Nicolas Gregori',
          AUTHOR_EMAIL: "nicolas.gregori@student.supsi.ch",
          DESCRIPTION: 'A Vite React application with metadata management',
        }
      }
    })
  ],
})
