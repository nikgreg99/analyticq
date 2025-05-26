import React, { useEffect, useCallback, useMemo } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { Box } from "@chakra-ui/react";
import LoadingSpinner from "components/ui/general/LoadingSpinner";
import ErrorDisplay from "components/layout/ErrorDisplay";
import BackButton from "components/ui/general/BackButton";
import { ScanHeader } from "components/ui/scan/ScanHeader";
import { ScanSummary } from "components/ui/scan/ScanSummary";
import { IssueTabs } from "components/ui/issue/IssueTabs";
import { updatePageMetadata } from "components/utils/metadata";
import { useScanDetails } from "hooks/useScanDetails";

/**
 * Component that displays detailed information about a specific scan.
 * Optimized for data fetching with better state management and error handling.
 *
 * @component
 * @example
 * ```jsx
 * <ScanDetailsPage />
 * ```
 *
 * @param {Object} props - Component props
 * @param {Object} [props.initialScanData=null] - Initial scan data to display before fetching
 * @returns {JSX.Element} A page displaying scan details or loading/error states
 */
export const ScanDetailsPage = ({ initialScanData = null }) => {
  const { contextId, scanId } = useParams();
  const navigate = useNavigate();
  const { scanData, status } = useScanDetails(scanId, initialScanData);

  const hasIssues = useMemo(
    () => Array.isArray(scanData?.issues) && scanData.issues.length > 0,
    [scanData],
  );

  // Update metadata when scan data changes
  useEffect(() => {
    if (status.loading) {
      updatePageMetadata(
        "Context stats...",
        "Loading stats information...",
        `/contexts/${contextId}/stats`,
      );
    } else if (scanData) {
      updatePageMetadata(
        `Scan ${scanId}`,
        scanId,
        `/contexts/${contextId}/scan/${scanId}`,
      );
    }
  }, [scanData, status.loading, contextId, scanId]);

  const handleBackClick = useCallback(() => {
    navigate(`/contexts/${contextId}`);
  }, [navigate, contextId]);

  // Render loading state
  if (status.loading) {
    return <LoadingSpinner />;
  }

  // Render error state
  if (status.error) {
    return (
      <ErrorDisplay
        title="Scan Details"
        error={status.error}
        backButton={
          <BackButton
            onClick={handleBackClick}
            label={`Back to Context ${contextId} page`}
          />
        }
      />
    );
  }

  // Render main content
  return (
    <Box p={6} mx="auto" maxWidth="1200px">
      <ScanHeader scanData={scanData} />
      <ScanSummary scanData={scanData} />
      {hasIssues && <IssueTabs scanData={scanData} />}
    </Box>
  );
};

ScanDetailsPage.displayName = "ScanDetailsPage";
