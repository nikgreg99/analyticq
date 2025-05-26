import React, { useMemo, useCallback, useState } from "react";
import {
  Box,
  VStack,
  HStack,
  Heading,
  Text,
  Badge,
  Button,
  IconButton,
  Flex,
  Collapsible,
  useBreakpointValue,
} from "@chakra-ui/react";
import { MdDelete, MdInfo } from "react-icons/md";
import { FaDeleteLeft } from "react-icons/fa6";
import { formatBytes } from "components/utils/files";
import { Toaster, toaster } from "../general/Toaster";
import { Tooltip } from "../general/Tooltip";
import { formatDate } from "components/utils/time";

/**
 * A component that displays a list of files with their names and sizes.
 * Allows for individual file deletion and bulk deletion of all files if handlers are provided.
 *
 * @component
 * @param {Object} props - The component props
 * @param {Array<{name: string, size: number}>} props.files - Array of file objects to display
 * @param {function(Object): void} [props.onDeleteFile] - Optional callback function to handle single file deletion
 * @param {function(): void} [props.onDeleteAllFiles] - Optional callback function to handle deletion of all files
 *
 * @returns {JSX.Element|null} Returns the file list component or null if no files are provided
 *
 * @example
 * <FileList
 *   files={[{name: "example.txt", size: 1024}]}
 *   onDeleteFile={(file) => handleDelete(file)}
 *   onDeleteAllFiles={() => handleDeleteAll()}
/>
 */
export const FileList = React.memo(
  ({ files, onDeleteFile, onDeleteAllFiles }) => {
    // Responsive styling for heading size and button size
    const headingSize = useBreakpointValue({ base: "md", md: "sm" });
    const buttonSize = useBreakpointValue({ base: "sm", md: "xs" });
    const textSize = useBreakpointValue({ base: "sm", md: "md" });
    const isMobile = useBreakpointValue({ base: true, md: false });

    const sortedFiles = useMemo(
      () => [...(files || [])].sort((a, b) => a.name.localeCompare(b.name)),
      [files],
    );

    // Track which file preview is currently expanded
    const [expandedFileIndex, setExpandedFileIndex] = useState(null);

    const handleDeleteFile = useCallback(
      (file) => {
        if (!onDeleteFile) return;

        if (onDeleteFile) {
          toaster.create({
            title: `Deleted ${file.name}`,
            type: "success",
            duration: 2500,
          });
        }
        onDeleteFile(file);
      },
      [onDeleteFile],
    );

    const toggleFilePreview = useCallback((index) => {
      setExpandedFileIndex(expandedFileIndex === index ? null : index);
    }, [expandedFileIndex]);

    if (!files || files.length === 0) {
      return (
        <Text color="blackAlpha.500" mt={4} textAlign="center">
          No files selected.
        </Text>
      );
    }

    return (
      <VStack
        align="stretch"
        mt={4}
        spacing={2}
        role="list"
        aria-label="Selected files"
        width="auto"
      >
        <Flex
          justifyContent="space-between"
          alignItems={isMobile ? "center" : "flex-start"}
          mb={2}
          direction={{ base: "column", md: "row" }}
          spacing={{ base: 2, md: 4 }}
        >
          <Heading
            size={headingSize}
            display="flex"
            alignItems="center"
            color="blackAlpha.800"
            textAlign={{ base: "center", md: "left" }}
          >
            Selected files
            <Badge
              ml={2}
              colorPalette="blue"
              fontSize={{ base: "xs", md: "sm" }}
            >
              {files.length}
            </Badge>
          </Heading>
          {onDeleteAllFiles && files.length > 0 && (
            <Button
              aria-label="Delete all files"
              colorPalette="red"
              size={buttonSize}
              onClick={onDeleteAllFiles}
              _hover={{ bg: "red.100" }}
              _active={{ bg: "red.200" }}
              cursor="pointer"
            >
              <MdDelete />
              Delete All
            </Button>
          )}
        </Flex>

        <Box maxH="500px" overflowY="auto" borderRadius="md">
          {sortedFiles.map((file, index) => (
            <Box key={`${file.name}-${file.size}-${index}`}>
              <Flex
                key={`${file.name}-${file.size}-${index}`}
                color="gray.600"
                justifyContent="space-between"
                role="listitem"
                p={2}
                transition="all 0.2s"
                direction={{ base: "column", md: "row" }}
                alignItems="center"
                w="full"
                mb={2}
                borderRadius="md"
                boxShadow="sm"
                _hover={{ boxShadow: "md" }}
                data-testid={`file-item-${index}`}
              >
                <Flex
                  flex="1"
                  justifyContent="space-between"
                  alignItems="center"
                  direction={{ base: "column", md: "row" }}
                  w="full"
                  gap={isMobile ? 2 : 0}
                >
                  <Text
                    color="blackAlpha.800"
                    fontSize={textSize}
                    fontWeight="medium"
                    noOfLines
                    maxW={{ base: "100%", md: "60%" }}
                  >
                    {file.name}
                  </Text>
                  <HStack spacing={1}>
                    <Tooltip
                      content={`Size: ${formatBytes(file.size)}`}
                      showArrow
                      aria-label="File size"
                    >
                      <Text
                        color="blackAlpha.800"
                        fontSize={{ base: "xs", md: "sm" }}
                        fontFamily="mono"
                      >
                        {formatBytes(file.size)}
                      </Text>
                    </Tooltip>

                    <Collapsible.Root
                      unmountOnExit
                    >
                      <Collapsible.Trigger>
                        <IconButton
                          bg="transparent"
                          aria-label={`Show file details for ${file.name}`}
                          size={buttonSize}
                          onClick={() => toggleFilePreview(index)}
                          _hover={{ bg: "blue.100", color: "blue.700" }}
                          _active={{ bg: "blue.200" }}
                        >
                          <MdInfo />
                        </IconButton>
                      </Collapsible.Trigger>
                      <Collapsible.Content>
                        <Box
                          p={3}
                          mb={2}
                          bg="gray.100"
                          borderRadius="md"
                          fontSize="sm"
                        >
                          <VStack align="start" wordSpacing={1} color="black">
                            <Text><strong>Type:</strong> {file.type || "Unknown"}</Text>
                            <Text><strong>Last Modified:</strong> {formatDate(file.lastModified)}</Text>
                            <Text><strong>Size:</strong> {formatBytes(file.size)}</Text>
                          </VStack>
                        </Box>
                      </Collapsible.Content>
                    </Collapsible.Root>
                  </HStack>
                </Flex>
                <HStack>

                  {onDeleteFile && (
                    <Tooltip
                      aria-label={`Delete ${file.name}`}
                      content={`Delete ${file.name}`}
                      showArrow
                    >
                      <IconButton
                        bg="transparent"
                        marginLeft="1em"
                        aria-label={`Delete file ${file.name}`}
                        size={buttonSize}
                        onClick={(e) => {
                          e.stopPropagation();
                          handleDeleteFile(file);
                        }}
                        _hover={{ bg: "red.100", color: "red.700" }}
                        _active={{ bg: "red.200" }}
                      >
                        <FaDeleteLeft size={12} />
                      </IconButton>
                    </Tooltip>
                  )}
                  <Toaster />
                </HStack>
              </Flex>
            </Box>
          ))}
        </Box>
      </VStack >
    );
  },
);

FileList.displayName = "FileList";
