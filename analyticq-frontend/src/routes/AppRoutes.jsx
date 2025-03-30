import React from "react";
import {
    BrowserRouter as Router,
    Routes,
    Route,
    Navigate
} from "react-router-dom";
import { MainLayout } from "components/layout/MainLayout";
import { HomePage } from "pages/Home"
import { AboutPage } from "pages/About"
import { NotFoundPage } from "pages/NotFound";

export const AppRoutes = () => {
    return (
        <Router>
            <MainLayout>
                <Routes>
                    <Route path="/" index element={<HomePage />} />
                    <Route path="/about" element={<AboutPage/>} />
                    {/* Catch-all route for 404 */}
                    <Route path="/404" element={<NotFoundPage />} />
                    <Route path="*" element={<Navigate to="/404" replace />} />
                </Routes>
            </MainLayout>
        </Router>
    )
}
