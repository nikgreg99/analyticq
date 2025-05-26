import React, { useState, useRef, useMemo, useEffect } from "react";
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
import { FaFileArchive, FaGit, FaPlay } from "react-icons/fa";

import { Toaster, toaster } from "components/ui/general/Toaster";
import { FileDropZone } from "components/ui/input/FileDropZone";
import { FileList } from "components/ui/input/FileList";
import { GitRepoInput } from "components/ui/input/GitRepoInput";
import { updatePageMetadata } from "components/utils/metadata";
import { useAnalysis } from "../hooks/useAnalysis";
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
  const { scanStatus, isSubmitting, error, startAnalysis, resetScan } =
    useAnalysis();

  // Responsive adjustments
  const headingSize = useBreakpointValue({ base: "lg", md: "xl" });
  const containerPadding = useBreakpointValue({ base: 3, md: 7 });
  const tabsOrientation = useBreakpointValue({ base: "column", md: "row" });
  const buttonSize = useBreakpointValue({ base: "md", md: "md" });
  const boxPadding = useBreakpointValue({ base: 3, sm: 4, md: 6 });

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

  const handleSubmit = () => {
    // Use the branch value directly without checking isCustomBranchSelected
    // This ensures we always send the current branch value regardless of how it was selected
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
    if(error){
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
  }

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
