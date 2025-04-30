import React, { useState, useEffect, useMemo, useRef, useCallback } from 'react';
import {
  Box,
  VStack,
  Heading,
  Button,
  Container,
  Tabs,
  Flex,
  Progress,
  Text,
  SimpleGrid,
  HStack,
} from '@chakra-ui/react';
import { Toaster, toaster } from 'components/ui/Toaster';
import { FileDropZone } from 'components/ui/FileDropZone';
import { FileList } from 'components/ui/FileList';
import { GitRepoInput } from 'components/ui/GitRepoInput';
import { FaFileArchive, FaGit, FaInfoCircle } from 'react-icons/fa';
import { updatePageMetadata } from 'components/utils/metadata';
import { analyzeFiles, analyzeGitRepo, getAnalysisStatus } from 'services/analyze';

/**
 * HomePage component that provides a user interface for analyzing code from different sources.
 * Users can either analyze code from a Git repository or upload local files.
 */
export const HomePage = () => {

  const [tabIndex, setTabIndex] = useState('git');
  const [selectedFiles, setSelectedFiles] = useState([]);
  const [gitUrl, setGitUrl] = useState('');
  const [branch, setBranch] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [scanStatus, setScanStatus] = useState(null);

  const dropzoneRef = useRef(null);

  useEffect(() => {
    updatePageMetadata(
      'Welcome to AnalyticQ',
      'AnalyticQ Home',
      '/home'
    );
  }, []);

  const checkScanStatus = useCallback(async () => {
    if (!scanStatus?.id) return;

    try {
      const response = await getAnalysisStatus(scanStatus.id);
      const { status, results, error } = response.data;

      setScanStatus(prev => ({ ...prev, status }));

      if (status == "completed") {
        toaster.create({
          title: 'Analysis Complete',
          description: 'Your scan completed successfully. Redirecting to results...',
          status: 'success',
          duration: 3000,
        })
        resetScan();
      }
      else if (status == "failed") {
        toaster.create({
          title: 'Analysis Failed',
          description: 'The scan could not be completed.',
          status: 'error',
          duration: 5000,
        });
        resetScan();
      }
    } catch (error) {
      // Silent failure of status check - we'll try again on next interval
      console.log('Status check failed, will retry', error);
    }
  }, [scanStatus]);

  useEffect(() => {
    let intervalId;

    if (scanStatus?.id && ['pending', 'running'].includes(scanStatus.status)) {
      // Poll every 3 seconds
      intervalId = setInterval(checkScanStatus, 3000);
    }

    return () => {
      if (intervalId) clearInterval(intervalId);
    };

  }, [scanStatus, checkScanStatus]);


  const resetScan = () => {
    setScanStatus(null);
  };

  const handleFileDrop = (acceptedFiles) => {
    setSelectedFiles(prevFiles => {
      const newFiles = acceptedFiles.filter(
        newFile => !prevFiles.some(
          existingFile => existingFile.name === newFile.name
        )
      );
      return [...prevFiles, ...newFiles];
    });
  };

  const handleDeleteFile = (fileToDelete) => {
    setSelectedFiles(prevFiles =>
      prevFiles.filter(file => file.name !== fileToDelete.name)
    );
  };

  const handleDeleteAllFiles = () => {
    setSelectedFiles([]);
  };

  const handleAnalysis = async () => {
    setIsSubmitting(true);
    try {
      let response;
      if (tabIndex === 'local') { // Local files tab
        if (selectedFiles.length > 0) {
          console.log('Analyzing local files:', selectedFiles);

          response = await analyzeFiles({
            files: selectedFiles,
            timeout: 600 // 10 minutes timeout
          });
        }
      } else { // Git repo tab
        if (gitUrl) {
          console.log('Analyzing GitHub repository:', {
            url: gitUrl,
            branch: branch
          });

          response = await analyzeGitRepo({
            git_url: gitUrl,
            branch: branch || undefined, // Only send if branch is specified
            timeout: 600 // 10 minutes timeout
          });
        }

        if (response?.data?.analysis_id) {
          setScanStatus({
            id: response.data.analysis_id,
            status: response.data.status || 'pending'
          });

          toaster.create({
            title: 'Analysis Started',
            description: 'Your scan has been successfully submitted.',
            status: 'info',
            duration: 3000,
          });

          resetFormAfterAnalyis();
        }
      }
    } catch (error) {
      console.error('Analysis error:', error);
    } finally {
      setIsSubmitting(false);
    }
  };

  const getStatusColor = () => {
    switch (scanStatus?.status) {
      case 'running': return 'blue.500';
      case 'completed': return 'green.500';
      case 'failed': return 'red.500';
      default: return 'gray.500';
    }
  };

  const getStatusText = () => {
    switch (scanStatus?.status) {
      case 'pending': return 'Preparing scan...';
      case 'running': return 'Analyzing your code...';
      case 'completed': return 'Analysis complete!';
      case 'failed': return 'Analysis failed';
      default: return 'Waiting for status...';
    }
  };

  const fileTypeAccepted = useMemo(() => ({
    'application/zip': ['.zip'],
    'application/x-tar': ['.tar'],
    'application/gzip': ['.gz'],
  }), []);

  const resetFormAfterAnalyis = () => {
    setSelectedFiles([]);

    if (dropzoneRef.current) {
      dropzoneRef.current.reset();
    }

  }

  return (
    <Container as="main" maxW="container.md" p={7}>
      <VStack spacing={6} align="stretch">
        <Heading as="h1" size="xl" color="GrayText" textAlign="center" mb={4}>
          Analyze Your Codebase for Security and Quality!
        </Heading>

        {/* Subtle Usage Guide */}
        <Box
          as="section"
          p={4}
          borderRadius="md"
          borderWidth="1px"
          borderColor="gray.200"
          mb={2}
          aria-labelledby="usage-guide"
        >
          <Heading id="usage-guide" as="h2" size="md" mb={3} visibility="hidden">
            Usage Guide
          </Heading>
          <SimpleGrid columns={{ base: 1, md: 2 }} spacing={4} mt={3}>
            <Box>
              <HStack spacing={2} mb={1}>
                <FaGit aria-hidden="true" color="#718096" size={12} />
                <Text fontSize="md" fontWeight="medium" color="gray.700">Git Repository</Text>
              </HStack>
              <Text fontSize="md" color="gray.600" pl={5}>
                Enter Git URL, specify branch (optional), click Start Analysis
              </Text>
            </Box>

            <Box>
              <HStack spacing={2} mb={1}>
                <FaFileArchive aria-hidden="true" color="#718096" size={12} />
                <Text fontSize="md" fontWeight="medium" color="gray.700">Local Files</Text>
              </HStack>
              <Text fontSize="md" color="gray.600" pl={5}>
                Upload compressed files (.zip, .tar, .gz), click Start Analysis
              </Text>
            </Box>
          </SimpleGrid>
        </Box>

        {/* Scan Status Indicator */}
        {scanStatus ? (
          <Box
            p={6}
            borderRadius="lg"
            bordderWidth="1px"
            aria-live='polite'
            aria-atomic='true'
          >
            <VStack align="stretch">
              <Progress.Root
                size="sm"
                colorPalette={getStatusColor}
                color="blackAlpha.800"
                value={scanStatus.status === 'completed' ? 100 : null}
                striped
                animated
              >
                <Progress.Label color="blackAlpha.800">
                  Scan in progress
                </Progress.Label>
                <Progress.Track>
                  <Progress.Range />
                </Progress.Track>
              </Progress.Root>
            </VStack>

            <Text fontWeight="medium" >{getStatusText()}</Text>

            {scanStatus.status === 'pending' || scanStatus.status === 'running' ? (
              <Text fontSize="sm" color="blackAlpha.800" textAlign="center">
                This may take several minutes depending on the size of your codebase.
              </Text>
            ) : null}
          </Box>
        ) : null}

        {/* Main Analysis Interface */}
        <Box
          p={6}
          borderRadius='4xl'
          borderWidth="4xl"
          as="section"
        aria-labelledby="analysis-section"
        >
          <Tabs.Root
            variant="enclosed"
            value={tabIndex}
            defaultValue='git'
            onValueChange={(e) => setTabIndex(e.value)}
          >
            <Tabs.List mb={4}>
              <Tabs.Trigger
                  _focus={{ boxShadow: "outline" }}
                  aria-label="Analyze a Git Repository"
                  value='git'
              >
                <FaGit style={{ marginRight: "8px" }} />
                Git Repository
              </Tabs.Trigger>
              <Tabs.Trigger
                  _focus={{ boxShadow: "outline" }}
                  value='local'
                  aria-label="Analyze Local Files"
                >
                <FaFileArchive style={{ marginRight: "8px" }} />
                Local File/Directory
              </Tabs.Trigger>
            </Tabs.List>
            <Tabs.Content value='local'>
              <FileDropZone
                ref={dropzoneRef}
                onDrop={handleFileDrop}
                accept={fileTypeAccepted}
              />
              <FileList
                files={selectedFiles}
                onDeleteFile={handleDeleteFile}
                onDeleteAllFiles={handleDeleteAllFiles}
              />
            </Tabs.Content>
            <Tabs.Content value='git'>
              <GitRepoInput
                onUrlChange={setGitUrl}
                onBranchChange={setBranch}
              />
            </Tabs.Content>
          </Tabs.Root>
          <Flex justify="center">
            <Button
              mt={6}
              bg="blackAlpha.900"
              color="whiteAlpha.900"
              variant="solid"
              size="sm"
              isLoading={isSubmitting}
              loadingText="Submitting"
              onClick={handleAnalysis}
              aria-label="Start the analysis"
              isDisabled={
                (tabIndex === 'local' && selectedFiles.length === 0) ||
                (tabIndex === 'git' && !gitUrl)
              }
            >
              Start Analysis
            </Button>
          </Flex>
        </Box>
      </VStack>
      <Toaster />
    </Container>
  )
};

export default HomePage;
