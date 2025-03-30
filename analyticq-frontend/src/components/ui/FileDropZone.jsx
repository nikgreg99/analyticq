import React from "react";
import {
    Box,
    VStack,
    Text,
} from "@chakra-ui/react";
import { useDropzone } from "react-dropzone";
import { FaCloudUploadAlt } from "react-icons/fa";
import { useColorModeValue } from "./color-mode";

/**
 * A customizable file drop zone component that allows users to drag and drop files or click to select them.
 *
 * @component
 * @param {Object} props - The component props
 * @param {Function} props.onDrop - Callback function triggered when files are dropped or selected
 * @param {Object} [props.accept={}] - Object specifying accepted file types
 * @param {boolean} [props.multiple=false] - Whether to allow multiple file selection
 * @param {string} [props.placeholder="Drag and drop your codebase here, or click to select it"] - Custom placeholder text
 *
 * @returns {JSX.Element} A styled drop zone component with upload icon and customizable text
 *
 * @example
 * <FileDropZone
 *   onDrop={(files) => handleFiles(files)}
 *   accept={{ 'application/zip': ['.zip'], 'application/x-tar': ['.tar', '.gz'] }}
 *   multiple={true}
 *   placeholder="Custom drop zone text"
 * />
 */
export const FileDropZone = ({
    onDrop,
    accept={},
    multiple=false,
    placeholder="Drag your codebase here ",
}) => {
    const {
        getRootProps,
        getInputProps,
        isDragActive
    } = useDropzone({
        onDrop,
        accept,
        multiple
    });

    const dropzoneBackground = useColorModeValue("gray.100", "gray.700");
    const dropZoneBorder = useColorModeValue("gray.300", "gray.600");
    const hoverBackground = useColorModeValue("gray.200", "gray.600");
    return (
        <Box
         {...getRootProps()}
         border="2px dashed"
         borderColor={isDragActive ? "blue.500": dropZoneBorder}
         color="whiteAlpha.800"
         bg={dropzoneBackground}
         textAlign="center"
         p={6}
         cursor="pointer"
         borderRadius="md"
         transition="all 0.3s"
         _hover={{ bg: hoverBackground }}
        >
            <input {...getInputProps()} />
            <VStack spacing={4}>
                <FaCloudUploadAlt
                    size={48}
                    color={isDragActive? "blue.500" : "gray.500" }
                />
                {isDragActive ? (
                    <Text>Drag you codebase here ...</Text>
                    ) : (
                        <>
                            <Text>{placeholder}</Text>
                            <Text fontSize="sm" color="whiteAlpha.800">
                                (Supports  .zip, .tar, .gz)
                            </Text>
                        </>
                )}
            </VStack>
        </Box>
    )
};
