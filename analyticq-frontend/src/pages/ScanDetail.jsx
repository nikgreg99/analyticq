import React, { useState, useEffect, useCallback } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { Box } from "@chakra-ui/react"
import { getScanById } from "services/scanService";
import LoadingSpinner from "components/ui/LoadingSpinner";
import ErrorDisplay from "components/layout/ErrorDisplay";
import BackButton from "components/ui/BackButton";
import { ScanHeader } from "components/ui/ScanHeader";
import { ScanSummary } from "components/ui/ScanSummary";
import { IssueTabs } from "components/ui/IssueTabs";
import { updatePageMetadata } from "components/utils/metadata";

/**
 * Component that displays detailed information about a specific scan.
 * Fetches and renders scan data including header, summary, issues, and metadata.
 *
 * @component
 * @example
 * ```jsx
 * <ScanDetailsPage />
 * ```
 *
 * @returns {JSX.Element} A page displaying scan details or loading/error states
 *
 * Uses URL parameters:
 * - contextId: ID of the context the scan belongs to
 * - scanId: ID of the specific scan to display
 *
 * State:
 * - scanData: Contains the fetched scan information
 * - loading: Boolean indicating if data is being fetched
 * - error: Contains error message if fetch fails
 *
 * Features:
 * - Automatic data fetching on component mount
 * - Loading spinner while fetching data
 * - Error handling with user-friendly display
 * - Navigation back to context page
 * - Displays scan header, summary, issues tabs and metadata
 */
export const ScanDetailsPage = ({ initialScanData = null }) => {

    const [scanData, setScanData] = useState([]);
    const [loading, setLoading] = useState(!initialScanData);
    const [error, setError] = useState(null);
    const { contextId, scanId } = useParams();
    const navigate = useNavigate();


    // Update metadata when product data changes
    useEffect(() => {
        // Set initial loading metadata
        updatePageMetadata(
            'Context stats...',
            'Loading stats information...',
            `/contexts/${contextId}/stats`
        );

        // Update with product data once loaded
        if (scanData) {
            updatePageMetadata(
                `Scan ${scanId}`,
                scanId,
                `/contexts/${contextId}/scan/${scanId}`
            );
        }
    }, [scanData, contextId, scanId]);


    // Fetch scan details from the API
    const fetchScanDetails = useCallback(async (id) => {
        try {
            setLoading(true);
            const data = await getScanById(id);
            console.log("Getting scan details: ", data);
            setScanData(data);
            setError(null);
        }
        catch (err) {
            console.error("Error fetching scan details:", err);
            setError("Failed to load scan details. Please try again later.");
        }
        finally {
            setLoading(false);
        }
    }, []);  // No dependencies needed as it doesn't use any external state

    // Effect to fetch scan details when component mounts or scanId changes
    useEffect(() => {
        if (!initialScanData || initialScanData.id !== parseInt(scanId)) {
            fetchScanDetails(scanId);
        }
    }, [fetchScanDetails, initialScanData, scanId]);

    const handleBackClick = () => {
        navigate(`/contexts/${contextId}`);
    };

    if (loading) {
        return <LoadingSpinner />
    }

    if (error) {
        return (
            <ErrorDisplay
                title="Scan Details"
                error={error}
                backButton={<BackButton onClick={handleBackClick} label={`Back to Context ${contextId} page`} />}
            />
        )
    }

    return (
        <Box
            p={6}
            mx="auto"
            maxWidth="1200px"
        >
            <ScanHeader scanData={scanData} />
            <ScanSummary scanData={scanData} />
            { scanData.issues.length > 0  &&
                <IssueTabs scanData={scanData} />
            }

        </Box>
    )
}
