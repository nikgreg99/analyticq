import React, { useState, useMemo } from 'react';
import {
    Box,
    VStack,
    Heading,
    Button,
    Container,
    Tabs,
    Flex,
  } from '@chakra-ui/react';

import { FileDropZone} from "components/ui/FileDropZone";
import { FileList } from 'components/ui/FileList';
import { GitRepoInput } from 'components/ui/GitRepoInput';
import { FaFileArchive , FaGit} from 'react-icons/fa'
import { useColorModeValue } from 'components/ui/color-mode';

export const HomePage = () => {
    const [tab, setTab] = useState('git')
    const [selectedFiles, setSelectedFiles] = useState([]);
    const [gitUrl, setGitUrl] = useState('');
    const [branch, setBranch] = useState('');


    const handleFileDrop = (acceptedFiles) => {
        setSelectedFiles(prevFiles => {
            const newFiles = acceptedFiles.filter(
                newFile => !prevFiles.some(
                    exiistingFile => exiistingFile == newFile.name
                )
            );
            return [...prevFiles, ...newFiles];
        });
      };


    const handleDeleteFile = (fileToDelete) => {
        setSelectedFiles(prevFiles =>
            prevFiles.filter(file => file !==fileToDelete)
        );
    };

    const handleDeleteAllFiles = () => {
        setSelectedFiles([]);
      };

    const handleAnalysis = (tabIndex) => {

        const analysisType = tabIndex === 0 ? 'git' : 'local';

        if(analysisType == "local" && selectedFiles.length > 0){
            console.log('Analyzing local files:', selectedFiles);
            // TODO: Start local analysis here
        }
        else if(analysisType == "git" && gitUrl){
            console.log('Analyzing GitHub repository:', {
                url: gitUrl,
                branch: branch
              });
              // TODO: Start analysis her
        }
    }

    const fileTypeAccepted = useMemo(() => ({
        'application/zip': ['.zip'],
        'application/x-tar': ['.tar'],
        'application/gzip': ['.gz'],
    }),  []);


    const cardBg = useColorModeValue("white", "gray.200");
    const borderColor = useColorModeValue("gray.200", "gray.600");

    return(
        <Container maxW="container.md" p={7}>
            <VStack spacing={6} align="stretch">
                <Heading as="h1" size="xl" color="GrayText" textAlign="center" mb={6}>
                    Analyze Your Codebase for Security and Quality!
                </Heading>

                <Box
                    bg={cardBg}
                    p={6}
                    borderRadius='4xl'
                    borderWidth="4xl"
                    borderColor={borderColor}
                >
                    <Tabs.Root
                        variant="enclosed"
                        colorScheme="blue"
                        value={tab}
                        onValueChange={(e) => setTab(e.value)}
                    >
                        <Tabs.List mb={4}>
                            <Tabs.Trigger value='git'>
                                <FaGit  style={{ marginRight: "8px" }}/>
                                Git Repository
                            </Tabs.Trigger>
                            <Tabs.Trigger value='local'>
                                <FaFileArchive style={{ marginRight: "8px" }}/>
                                Local File/Directory
                            </Tabs.Trigger>
                        </Tabs.List>
                        <Tabs.Content value='local'>
                            <FileDropZone
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
                            onClick={handleAnalysis}
                            isDisabled={
                                (tab === 'local' && selectedFiles.length === 0) ||
                                (tab === 'git' && !gitUrl)
                            }
                         >
                        Start Analysis
                        </Button>
                    </Flex>
                </Box>
            </VStack>
        </Container>
    )
};

export default HomePage;
