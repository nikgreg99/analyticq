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
  const mountedRef = useRef(true);

  const { scanStatus, isSubmitting, error, startAnalysis, resetScan } = useAnalysis();
  const { redirectToContext } = useAnalysisRedirect();
  const navigate = useNavigate();

  // Responsive adjustments
  const headingSize = useBreakpointValue({ base: "lg", md: "xl" });
  const containerPadding = useBreakpointValue({ base: 3, md: 7 });
  const tabsOrientation = useBreakpointValue({ base: "column", md: "row" });
  const buttonSize = useBreakpointValue({ base: "md", md: "md" });
  const boxPadding = useBreakpointValue({ base: 3, sm: 4, md: 6 });

  // Cleanup on unmount
  useEffect(() => {
    mountedRef.current = true;
    return () => {
      mountedRef.current = false;
    };
  }, []);

  useEffect(() => {
    updatePageMetadata("Welcome to AnalyticQ", "AnalyticQ Home", "/home");
  }, []);

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

  // Safe repository name extraction
  const getRepositoryName = useCallback(() => {
    try {
      if (tabIndex === 'git' && gitUrl) {
        // Try to parse as URL first
        try {
          const url = new URL(gitUrl);
          const pathParts = url.pathname.split('/').filter(Boolean);
          return pathParts[pathParts.length - 1]?.replace('.git', '') || '';
        } catch {
          // Fallback for non-URL formats
          const parts = gitUrl.split('/').filter(Boolean);
          return parts[parts.length - 1]?.replace('.git', '') || '';
        }
      } else if (tabIndex === 'local' && selectedFiles.length > 0) {
        const fileName = selectedFiles[0]?.name || '';
        return fileName.replace(/\.[^/.]+$/, "");
      }
    } catch (error) {
      console.error('Error extracting repository name:', error);
    }
    return '';
  }, [tabIndex, gitUrl, selectedFiles]);

  // Safe redirect function with proper error handling
  const performRedirect = useCallback(async (repoName) => {
    if (!mountedRef.current) return;

    try {
      if (repoName) {
        console.log('Redirecting to context:', repoName);
        await redirectToContext(repoName, {
          replace: true,
          fallbackPath: '/contexts'
        });
      } else {
        console.log('No repo name, redirecting to contexts page');
        if (mountedRef.current) {
          toaster.create({
            title: "Analysis Complete",
            description: "Analysis finished successfully. Redirecting to contexts page.",
            type: "success",
            duration: 3000,
          });

          setTimeout(() => {
            if (mountedRef.current) {
              navigate('/contexts', { replace: true });
            }
          }, 1500);
        }
      }
    } catch (error) {
      console.error('Error during redirect:', error);
      // Always provide fallback
      if (mountedRef.current) {
        navigate('/contexts', { replace: true });
      }
    }
  }, [redirectToContext, navigate]);

  // Handle successful analysis completion and redirect
  useEffect(() => {
    // Reset redirect flag when scan status changes away from completed
    if (scanStatus?.status !== 'completed') {
      redirectHandledRef.current = false;
      return;
    }

    // Only handle redirect once per completed scan
    if (
      scanStatus?.status === 'completed' &&
      scanStatus?.success &&
      !redirectHandledRef.current &&
      mountedRef.current
    ) {
      redirectHandledRef.current = true;

      console.log('Analysis completed successfully, initiating redirect');

      const repoName = getRepositoryName();
      performRedirect(repoName);
    }
  }, [scanStatus?.status, scanStatus?.success, getRepositoryName, performRedirect]);

  const handleSubmit = () => {
    // Reset redirect flag before starting new analysis
    redirectHandledRef.current = false;

    // Use the branch value directly without checking isCustomBranchSelected
    const success = startAnalysis({
      source: tabIndex,
      files: selectedFiles,
      gitUrl,
      branch: branch.trim() || "main", // Default to "main" if branch is empty
    });

    if (success) {
      resetForm();
    }
  };

  const resetForm = () => {
    if (tabIndex === "local") {
      setSelectedFiles([]);
      dropzoneRef.current?.reset();
    } else {
      setGitUrl("");
      setBranch("");
      setIsCustomBranchSelected(false);
    }
  };

  const resetAllState = () => {
    // Reset redirect flag
    redirectHandledRef.current = false;

    // Reset form fields
    setSelectedFiles([]);
    setGitUrl("");
    setBranch("");
    setIsCustomBranchSelected(false);

    // Reset dropzone if it exists
    if (dropzoneRef.current?.reset) {
      dropzoneRef.current.reset();
    }

    // Reset scan status
    resetScan();

    // Clear any existing toasts
    toaster.dismiss();
  };

  // Handle branch changes from GitRepoInput
  const handleBranchChange = (newBranch) => {
    setBranch(newBranch);
  };

  const handleTabChange = (newTab) => {
    if (error) {
      resetScan();
    }

    setTabIndex(newTab);

    if (newTab === "local") {
      setGitUrl("");
      setBranch("");
      setIsCustomBranchSelected(false);
    } else {
      setSelectedFiles([]);
      if (dropzoneRef.current?.reset) {
        dropzoneRef.current.reset();
      }
    }
  };

  const isSubmitDisabled = useMemo(() => {
    if (isSubmitting) return true;

    if (tabIndex === "local") {
      return selectedFiles.length === 0;
    }

    // For Git tab, require URL and branch
    // If custom branch is selected, ensure it has a value
    return !gitUrl || (isCustomBranchSelected && !branch.trim());
  }, [
    isSubmitting,
    tabIndex,
    selectedFiles,
    gitUrl,
    isCustomBranchSelected,
    branch,
  ]);

  const handleKeyDown = useCallback((event) => {
    // Only trigger on Enter key, and ensure we're not in a textarea or other input that should handle Enter normally
    if (event.key === 'Enter' && !event.shiftKey && !event.ctrlKey && !event.altKey) {
      const target = event.target;

      // Don't interfere with Enter in textareas, contenteditable, or form inputs that might need Enter
      if (
        target.tagName === 'TEXTAREA' ||
        target.contentEditable === 'true' ||
        (target.tagName === 'INPUT' && target.type === 'text' && target.getAttribute('role') !== 'combobox')
      ) {
        return;
      }

      // Check if submit button is available and not disabled
      if (!isSubmitDisabled && !isSubmitting) {
        event.preventDefault();
        handleSubmit();
      }
    }
  }, [isSubmitDisabled, isSubmitting, handleSubmit]);


  useEffect(() => {
    document.addEventListener('keydown', handleKeyDown);
    return () => {
      document.removeEventListener('keydown', handleKeyDown);
    };
  }, [handleKeyDown])


  const fileTypeAccepted = useMemo(
    () => ({
      "application/zip": [".zip"],
      "application/x-tar": [".tar"],
      "application/gzip": [".gz"],
    }),
    [],
  );

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
                  _focus={{ boxShadow: "outline" }}
                  aria-label="Analyze a Git Repository"
                  value="git"
                >
                  <Flex align="center" justify={{ base: "center", md: "flex-start" }}>
                    <FaGit style={{ marginRight: "8px" }} aria-hidden="true" />
                    <Text>Git Repository</Text>
                  </Flex>
                </Tabs.Trigger>
                <Tabs.Trigger
                  flex={{ base: "1", md: "auto" }}
                  p={{ base: 2, md: 3 }}
                  _focus={{ boxShadow: "outline" }}
                  value="local"
                  aria-label="Analyze Local Files"
                >
                  <Flex align="center" justify={{ base: "center", md: "flex-start" }}>
                    <FaFileArchive
                      style={{ marginRight: "8px" }}
                      aria-hidden="true"
                    />
                    <Text>Local File/Directory</Text>
                  </Flex>
                </Tabs.Trigger>
                <Tabs.Indicator />
              </Tabs.List>
              <Tabs.Content
                key="local"
                value="local"
              >
                <FileDropZone
                  ref={dropzoneRef}
                  onDrop={setSelectedFiles}
                  accept={fileTypeAccepted}
                />
                <FileList
                  files={selectedFiles}
                  onDeleteFile={(f) =>
                    setSelectedFiles((prev) =>
                      prev.filter((file) => file !== f),
                    )
                  }
                  onDeleteAllFiles={() => setSelectedFiles([])}
                />
              </Tabs.Content>
              <Tabs.Content value="git">
                <GitRepoInput
                  onUrlChange={setGitUrl}
                  onBranchChange={handleBranchChange}
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
                aria-label="Start the analysis"
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
