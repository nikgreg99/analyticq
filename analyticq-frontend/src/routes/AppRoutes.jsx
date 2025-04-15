import React from "react";
import {
    BrowserRouter as Router,
    Routes,
    Route,
    Navigate
} from "react-router-dom";
import { MainLayout } from "components/layout/MainLayout";
import { ToolsPage } from "pages/Tools";
import { LanguagesPage } from "pages/Languages";
import { HomePage } from "pages/Home";
import { AboutPage } from "pages/About";
import { ContextsPage } from "pages/Contexts";
import { ContextDetailPage } from "pages/ContextDetail";
import { StatsDashboard } from "pages/StatsDashboard";
import { ScanDetailsPage } from "pages/ScanDetail";
import { IssueDetailPage } from "pages/IssueDetail";
import { NotFoundPage } from "pages/NotFound";

/**
 * AppRoutes component handles the routing configuration for the application.
 * It sets up the main routing structure using React Router, defining paths
 * for various pages within the MainLayout component.
 *
 * Routes include:
 * - "/" - Home page
 * - "/contexts" - Contexts listing page
 * - "/contexts/:contextId" - Individual context details
 * - "/contexts/:contextId/stats" - Statistics dashboard for specific context
 * - "/tools" - Tools page
 * - "/language-supported" - Supported languages page
 * - "/about" - About page
 * - "/404" - Not found page
 *
 * Also includes a catch-all route that redirects undefined paths to 404 page.
 *
 * @component
 * @returns {JSX.Element} The router configuration wrapped in Router component
 */
export const AppRoutes = () => {
    return (
        <Router>
            <MainLayout>
                <Routes>
                    <Route path="/" index element={<HomePage />} />
                    <Route path="/contexts" element={<ContextsPage />} />
                    <Route path="/contexts/:contextId"
                        element={<ContextDetailPage />}
                    />
                    <Route path="/contexts/:contextId/stats"
                        element={<StatsDashboard />}
                    />
                    <Route path="/contexts/:contextId/scans/:scanId"
                        element={<ScanDetailsPage/>} />
                    <Route path="issues/:issueId"
                        element={<IssueDetailPage/>}
                    />
                    <Route path="/tools" element={ <ToolsPage/> } />
                    <Route path="/language-supported" element={<LanguagesPage/>}/>
                    <Route path="/about" element={<AboutPage />} />
                    {/* Catch-all route for 404 */}
                    <Route path="/404" element={<NotFoundPage />} />
                    <Route path="*" element={<Navigate to="/404" replace />} />
                </Routes>
            </MainLayout>
        </Router>
    )
}
