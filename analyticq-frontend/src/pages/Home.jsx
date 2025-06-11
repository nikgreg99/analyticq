import React, { useState, useRef, useMemo, useEffect, useCallback } from "react";
import {
  Box,
  VStack,
  Heading,
  Button,
  Container,
  Flex,
  useBreakpointValue,
  Text,
  Stack,
  Tabs
} from "@chakra-ui/react";
import { useNavigate } from "react-router-dom";
import { FaFileArchive, FaGit, FaPlay } from "react-icons/fa";

import { Toaster, toaster } from "components/ui/general/Toaster";
import { FileDropZone } from "components/ui/input/FileDropZone";
import { FileList } from "components/ui/input/FileList";
import { GitRepoInput } from "components/ui/input/GitRepoInput";
import { updatePageMetadata } from "components/utils/metadata";
import { useAnalysis } from "../hooks/useAnalysis";
import { useAnalysisRedirect } from "hooks/useAnalysisRedirect";
import InfoUsageGuide from "components/ui/input/InfoUsageGuide";
import { ScanStatusIndicator } from "components/ui/input/ScanStatusIndicator";
import { Home } from "lucide-react";

export const HomePage = () => {
  const [tabIndex, setTabIndex] = useState("git");
  const [selectedFiles, setSelectedFiles] = useState([]);
  const [gitUrl, setGitUrl] = useState("");
  const [branch, setBranch] = useState("");
  const [isCustomBranchSelected, setIsCustomBranchSelected] = useState(false);

  const dropzoneRef = useRef(null);
  const redirectHandledRef = useRef(false);

  const { scanStatus, isSubmitting, error, startAnalysis, resetScan } = useAnalysis();
  const { redirectToContext } = useAnalysisRedirect();
  const navigate = useNavigate();

  // Responsive adjustments
  const headingSize = useBreakpointValue({ base: "lg", md: "xl" });
  const containerPadding = useBreakpointValue({ base: 3, md: 7 });
  const tabsOrientation = useBreakpointValue({ base: "column", md: "row" });
  const buttonSize = useBreakpointValue({ base: "md", md: "md" });
  const boxPadding = useBreakpointValue({ base: 3, sm: 4, md: 6 });

  // Initialize page metadata
  useEffect(() => {
    updatePageMetadata("Welcome to AnalyticQ", "AnalyticQ Home", "/home");
  }, []);

  // Show error toasts
  useEffect(() => {
    if (error) {
      toaster.create({
        title: "Analysis Error",
        description: error.message || "An error occurred during analysis.",
        type: "error",
        duration: 6000,
        closable: true,
      });
    }
  }, [error]);

  // Extract repository name for redirect
  const getRepositoryName = useCallback(() => {
    if (tabIndex === 'git' && gitUrl) {
      // Extract repo name from Git URL
      const parts = gitUrl.split('/').filter(Boolean);
      return parts[parts.length - 1]?.replace('.git', '') || '';
    } else if (tabIndex === 'local' && selectedFiles.length > 0) {
      // Extract name from first file
      const fileName = selectedFiles[0]?.name || '';
      return fileName.replace(/\.[^/.]+$/, "");
    }
    return '';
  }, [tabIndex, gitUrl, selectedFiles]);

  // Handle successful analysis completion
  useEffect(() => {
    const isCompleted = scanStatus?.status === 'completed' && scanStatus?.success;

    if (isCompleted && !redirectHandledRef.current) {
      redirectHandledRef.current = true;

      const repoName = getRepositoryName();
      console.log("Redirecting to context for repo:", repoName);

      if (repoName) {
        redirectToContext(repoName, { replace: true });
      } else {
        // No repo name, show success message and redirect to contexts
        toaster.create({
          title: "Analysis Complete",
          description: "Analysis finished successfully.",
          type: "success",
          duration: 3000,
        });
        setTimeout(() => navigate('/contexts', { replace: true }), 1500);
      }
    }

    // Reset redirect flag when status changes
    if (scanStatus?.status !== 'completed') {
      redirectHandledRef.current = false;
    }
  }, [scanStatus, getRepositoryName, redirectToContext, navigate]);

  // Reset form fields
  const resetForm = useCallback(() => {
    if (tabIndex === "local") {
      setSelectedFiles([]);
      dropzoneRef.current?.reset();
    } else {
      setGitUrl("");
      setBranch("");
      setIsCustomBranchSelected(false);
    }
  }, [tabIndex]);

  // Handle form submission
  const handleSubmit = useCallback(() => {
    redirectHandledRef.current = false;

    const success = startAnalysis({
      source: tabIndex,
      files: selectedFiles,
      gitUrl,
      branch: branch.trim() || "main",
    });

    if (success) {
      resetForm();
    }
  }, [startAnalysis, tabIndex, selectedFiles, gitUrl, branch, resetForm]);

  // Reset all state
  const resetAllState = useCallback(() => {
    redirectHandledRef.current = false;
    setSelectedFiles([]);
    setGitUrl("");
    setBranch("");
    setIsCustomBranchSelected(false);
    dropzoneRef.current?.reset();
    resetScan();
    toaster.dismiss();
  }, [resetScan]);

  // Handle tab changes
  const handleTabChange = useCallback((newTab) => {
    if (error) resetScan();

    setTabIndex(newTab);

    // Clear other tab's data
    if (newTab === "local") {
      setGitUrl("");
      setBranch("");
      setIsCustomBranchSelected(false);
    } else {
      setSelectedFiles([]);
      dropzoneRef.current?.reset();
    }
  }, [error, resetScan]);

  // Check if submit should be disabled
  const isSubmitDisabled = useMemo(() => {
    if (isSubmitting) return true;

    if (tabIndex === "local") {
      return selectedFiles.length === 0;
    }

    // For Git: require URL, and if custom branch is selected, require branch value
    return !gitUrl || (isCustomBranchSelected && !branch.trim());
  }, [isSubmitting, tabIndex, selectedFiles, gitUrl, isCustomBranchSelected, branch]);

  // Handle Enter key submission
  const handleKeyDown = useCallback((event) => {
    if (event.key === 'Enter' && !event.shiftKey && !isSubmitDisabled && !isSubmitting) {
      const target = event.target;

      // Don't interfere with textareas or text inputs
      if (target.tagName === 'TEXTAREA' ||
          (target.tagName === 'INPUT' && target.type === 'text')) {
        return;
      }

      event.preventDefault();
      handleSubmit();
    }
  }, [isSubmitDisabled, isSubmitting, handleSubmit]);

  useEffect(() => {
    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [handleKeyDown]);

  const fileTypeAccepted = useMemo(() => ({
    "application/zip": [".zip"],
    "application/x-tar": [".tar"],
    "application/gzip": [".gz"],
  }), []);

  return (
    <Container maxW="container.md" p={containerPadding}>
      <VStack spacing={{ base: 4, md: 6 }} align="stretch">
        <Heading
          as="h1"
          size={headingSize}
          color="GrayText"
          textAlign="center"
          px={{ base: 2, md: 0 }}
        >
          Analyze Your Codebase for Security and Quality!
        </Heading>

        <InfoUsageGuide />

        {scanStatus && (
          <ScanStatusIndicator scanStatus={scanStatus} resetScan={resetAllState} />
        )}

        <Box p={{ base: 2, md: boxPadding }}>
          <Box
            p={{ base: 3, md: boxPadding }}
            borderRadius={{ base: "lg", md: "xl" }}
            borderWidth="1px"
            boxShadow="md"
            as="section"
            aria-labelledby="analysis-section"
          >
            <Tabs.Root
              variant="enclosed"
              value={tabIndex}
              defaultValue="git"
              onValueChange={(e) => handleTabChange(e.value)}
              lazyMount
              unmountOnExit
            >
              <Tabs.List
                mb={4}
                display="flex"
                flexDirection={tabsOrientation}
                width={{ base: "100%", md: "auto" }}
              >
                <Tabs.Trigger
                  flex={{ base: "1", md: "auto" }}
                  p={{ base: 2, md: 3 }}
                  value="git"
                >
                  <Flex align="center" justify={{ base: "center", md: "flex-start" }}>
                    <FaGit style={{ marginRight: "8px" }} />
                    <Text>Git Repository</Text>
                  </Flex>
                </Tabs.Trigger>
                <Tabs.Trigger
                  flex={{ base: "1", md: "auto" }}
                  p={{ base: 2, md: 3 }}
                  value="local"
                >
                  <Flex align="center" justify={{ base: "center", md: "flex-start" }}>
                    <FaFileArchive style={{ marginRight: "8px" }} />
                    <Text>Local File/Directory</Text>
                  </Flex>
                </Tabs.Trigger>
                <Tabs.Indicator />
              </Tabs.List>

              <Tabs.Content value="local">
                <FileDropZone
                  ref={dropzoneRef}
                  onDrop={setSelectedFiles}
                  accept={fileTypeAccepted}
                />
                <FileList
                  files={selectedFiles}
                  onDeleteFile={(f) =>
                    setSelectedFiles((prev) => prev.filter((file) => file !== f))
                  }
                  onDeleteAllFiles={() => setSelectedFiles([])}
                />
              </Tabs.Content>

              <Tabs.Content value="git">
                <GitRepoInput
                  onUrlChange={setGitUrl}
                  onBranchChange={setBranch}
                  onCustomBranchToggle={setIsCustomBranchSelected}
                  isCustomBranchSelected={isCustomBranchSelected}
                  customBranchValue={branch}
                  gitUrl={gitUrl}
                  branch={branch}
                />
              </Tabs.Content>
            </Tabs.Root>

            <Flex justify="center">
              <Button
                mt={6}
                bg="blackAlpha.900"
                color="whiteAlpha.900"
                variant="solid"
                size={buttonSize}
                isLoading={isSubmitting}
                loadingText="Submitting"
                onClick={handleSubmit}
                isDisabled={isSubmitDisabled}
                width={{ base: "100%", sm: "auto" }}
                px={{ base: 4, sm: 6 }}
              >
                <Stack direction="row" spacing={2} align="center">
                  {!isSubmitting && <FaPlay />}
                  <Text>{isSubmitting ? "Submitting..." : "Start Analysis"}</Text>
                </Stack>
              </Button>
            </Flex>
          </Box>
        </Box>
      </VStack>
      <Toaster />
    </Container>
  );
};

Home.displayName = "Home";
