import React from "react";
import {
    VStack,
    HStack,
    Heading,
    Text,
    Badge,
    IconButton,
    Flex,
} from "@chakra-ui/react";
import { MdDelete } from "react-icons/md";
import { FaDeleteLeft } from "react-icons/fa6";
import { formatBytes } from "components/utils/files";
import { Toaster, toaster } from "./Toaster";
import { Tooltip } from "./Tooltip";

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
 * />
 */
export const FileList = ({
    files,
    onDeleteFile,
    onDeleteAllFiles
}) => {

    if (!files || files.length === 0) return null;

    const sortedFiles = [...files].sort((a, b) => a.name.localeCompare(b.name));


    const confirmDelete = (file) => {
        if (onDeleteFile) {
            toaster.create({
                title: `Deleted ${file.name}`,
                type: "success",
                duration: 2500,
            })
        }
        onDeleteFile(file)
    }

    return (
        <VStack
            align="stretch"
            mt={4} spacing={2}
            role="list"
            aria-label="Selected files"
        >
            <HStack
                justifyContent="space-between"
                alignItems="center"
                mb="2"
            >
                <Heading
                    size="sm"
                    display="flex"
                    alignItems="center"
                    color="GrayText"
                >
                    Selected files
                    <Badge ml={2} colorScheme="blue">{files.length}</Badge>
                </Heading>
                {onDeleteAllFiles && (
                    <Tooltip
                        content="Delete all files   "
                        aria-label="Delete all files"
                        showArrow
                    >
                        <IconButton
                            aria-label="Delete all files"
                            bg="red.500"
                            color="whiteAlpha.900"
                            variant="solid"
                            size="xs"
                            onClick={onDeleteAllFiles}
                            _hover={{ bg: "red.100" }}
                            _active={{ bg: "red.200" }}
                        >
                            <MdDelete color="black" />
                            Delete All
                        </IconButton>
                    </Tooltip>
                )
                }</HStack>
            {sortedFiles.map((file) => (
                <Flex
                    key={file.name} // Use file name as key if unique
                    color="gray.600"
                    justifyContent="space-between"
                    role="listitem"
                    p={2}
                    transition="all 0.2s"
                >
                    <Flex flex="1" justifyContent="space-between" alignItems="center">
                        <Text color="GrayText">{file.name}</Text>
                        <HStack>
                            <Tooltip
                                content={`Size: ${formatBytes(file.size)}`}
                                showArrow
                                 aria-label="File size"
                            >
                                <Text
                                    color="gray.500"
                                    fontSize="sm"
                                >
                                    {formatBytes(file.size)}
                                </Text>
                            </Tooltip>
                        </HStack>
                    </Flex>
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
                                size="xs"
                                onClick={(e) => {
                                    e.stopPropagation();
                                    confirmDelete(file);
                                }}
                                _hover={{ bg: "red.100" }}
                                _active={{ bg: "red.200" }}
                            >
                                <FaDeleteLeft size={12} />
                            </IconButton>
                        </Tooltip>
                    )
                    }
                    <Toaster />
                </Flex >
            ))}
        </VStack >
    );
};
