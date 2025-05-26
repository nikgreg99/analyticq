import { useState, useEffect, useCallback, useRef } from "react";
import {
  analyzeFiles,
  analyzeGitRepo,
  getAnalysisStatus,
} from "services/analyze";
import { toaster } from "components/ui/general/Toaster";

/**
 * Custom hook for managing code analysis operations.
 * Handles both local file and Git repository analysis with status tracking.
 *
 * @returns {Object} An object containing:
 *   @property {Object|null} scanStatus - Current scan status containing id and status
 *   @property {boolean} isSubmitting - Flag indicating if analysis is being submitted
 *   @property {string|null} error - Error message if any
 *   @property {Function} startAnalysis - Function to start analysis
 *     @param {Object} params - Analysis parameters
 *     @param {File[]} [params.files] - Array of files for local analysis
 *     @param {string} [params.gitUrl] - Git repository URL for remote analysis
 *     @param {string} [params.branch] - Git branch name
 *     @param {('local'|'git')} params.source - Source type of the analysis
 *   @property {Function} resetScan - Function to reset scan state
 */
export const useAnalysis = () => {
  const [scanStatus, setScanStatus] = useState(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState(null);
  const statusIntervalRef = useRef(null);

  const resetScan = useCallback(() => {
  setScanStatus(null);
  setError(null);
  setIsSubmitting(false);
  // Clear any other analysis state
}, []);

  const checkScanStatus = useCallback(async () => {
    if (!scanStatus?.id) return;

    try {
      const response = await getAnalysisStatus(scanStatus.id);
      const { status } = response.data;

      setScanStatus((prev) => ({ ...prev, status }));

      if (status === "completed") {
        toaster.create({
          title: "Analysis Complete",
          description: "Your scan completed successfully.",
          type: "success",
          duration: 3000,
          closable: true,
        });
        resetScan();
      } else if (status === "failed") {
        toaster.create({
          title: "Analysis Failed",
          description: "The scan could not be completed.",
          type: "error",
          duration: 5000,
          closable: true,
        });

        resetScan();
      }
    } catch {
      setError("Unable to check analysis status. Please try again later.");
    }
  }, [scanStatus, resetScan]);



  useEffect(() => {
    if (statusIntervalRef.current) clearInterval(statusIntervalRef.current);
    if (scanStatus?.id && ["pending", "running"].includes(scanStatus.status)) {
      statusIntervalRef.current = setInterval(checkScanStatus, 3000);
    }
    return () => clearInterval(statusIntervalRef.current);
  }, [scanStatus, checkScanStatus]);

  const startAnalysis = async ({ files, gitUrl, branch, source }) => {
    try {
      setIsSubmitting(true);
      setError(null);

      let response;
      if (source === "local") {
        if (!files?.length) throw new Error("Please select at least one file.");
        response = await analyzeFiles({ files, timeout: 600 });
      } else {
        if (!gitUrl) throw new Error("Please enter a Git repository URL");
        response = await analyzeGitRepo({
          git_url: gitUrl,
          branch,
          timeout: 600,
        });
      }

      if (response?.data?.analysis_id) {
        setScanStatus({
          id: response.data.analysis_id,
          status: response.data.status || "pending",
        });
        toaster.create({
          title: "Analysis Started",
          description: "Your scan has been successfully submitted.",
          status: "info",
          duration: 3000,
        });
      } else {
        throw new Error("Invalid response from server");
      }
    } catch (err) {
      setError(err.message);
      toaster.create({
        title: "Analysis Failed",
        description: err.message,
        status: "error",
        duration: 5000,
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  return {
    scanStatus,
    isSubmitting,
    error,
    startAnalysis,
    resetScan,
  };
};
