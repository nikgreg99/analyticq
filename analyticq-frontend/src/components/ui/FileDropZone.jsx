import React, { forwardRef, useImperativeHandle, useState, useCallback } from "react";
import {
    Box,
    VStack,
    Text,
    VisuallyHidden,
    Flex,
    Icon
} from "@chakra-ui/react";
import { useDropzone } from "react-dropzone";
import { FaCloudUploadAlt, FaExclamationTriangle } from "react-icons/fa";
import { AiOutlineFileZip } from "react-icons/ai";
import { useColorModeValue } from "./color-mode";
import { Toaster, toaster } from "./toaster";

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
export const FileDropZone = forwardRef(({
    onDrop,
    accept = {},
    multiple = false,
    placeholder = "Drag your codebase here ",
    maxSize = 100,
    height = "auto",
    width = "100%",
    disabled = false,
}, ref) => {

    const [error, setError] = useState(null);
    const maxSizeInBytes = maxSize * 1024 * 1024; // Convert MB to bytes


    const {
        getRootProps,
        getInputProps,
        isDragActive,
        isDragAccept,
        isDragReject,
        open
    } = useDropzone({
        onDrop,
        accept,
        multiple,
        maxSize: maxSizeInBytes,
        disabled
    });


    const dropzoneBackground = useColorModeValue("gray.100", "gray.700");
    const dropZoneBorder = useColorModeValue("gray.300", "gray.600");
    const hoverBackground = useColorModeValue("gray.200", "gray.600");
    const activeColor = useColorModeValue("blue.500", "blue.300");
    const errorColor = useColorModeValue("red.500", "red.300");


    // Determine dropzone state colors
    const getBorderColor = () => {
        if (isDragReject || error) return errorColor;
        if (isDragAccept) return "green.400";
        if (isDragActive) return activeColor;
        return dropZoneBorder;
    };

    useImperativeHandle(ref, () => ({

        reset: () => {
            setError(null);
            const fileInput = document.querySelector('input[type="file"]');
            if (fileInput) {
                fileInput.value = '';

                const event = new Event('input', { bubbles: true });
                fileInput.dispatchEvent(event);

                onDrop([]);
            }
        },
        openFileDialog: () => {
            if (!disabled) {
                open();
            }
        }

    }), [onDrop, open, disabled]);


    const supportedExtensions = Object.values(accept).flat().join(', ');

    return (
        <Box
            position="relative"
            height={height}
            widow={width}
            data-testid="file-dropzone"
        >
            <Box
                {...getRootProps()}
                border="2px dashed"
                borderColor={getBorderColor()}
                color="whiteAlpha.800"
                bg={dropzoneBackground}
                textAlign="center"
                p={6}
                cursor={disabled ? "not-allowed" : "pointer"}
                borderRadius="md"
                transition="all 0.3s"
                position="relative"
                height="100%"
                width="100%"
                display="flex"
                alignItems="center"
                justifyContent="center"
                _hover={disabled ? {} : { bg: hoverBackground }}
                role="button"
                opacity={disabled ? 0.6 : 1}
                aria-label={disabled ? "File upload disabled" : "Drop zone for uploading files"}
            >
                <input {...getInputProps()} aria-label="File input" />
                <VStack spacing={4}>
                    {error ? (
                        <Icon
                            as={FaExclamationTriangle}
                            boxSize={12}
                            color="red.800"
                            aria-hidden="true"
                        />
                    ) : (
                        <Flex
                            position="relative"
                            justifyContent="center"
                            width="100%"
                        >
                            <Icon
                                as={FaCloudUploadAlt}
                                boxSize={isDragActive ? 16 : 12}
                                transition="all 0.3s ease"
                                aria-hidden="true"
                            />

                            {isDragActive && (
                                <Icon
                                    as={AiOutlineFileZip}
                                    boxSize={6}
                                    position="absolute"
                                    bottom="-10px"
                                    right="calc(50% - 30px)"
                                    color="blue.500"
                                    aria-hidden="true"
                                />
                            )}
                        </Flex>
                    )}

                    <VStack spacing={2}>
                        {error ? (
                            <Text color="red.500" fontWeight="medium">
                                {error}
                            </Text>
                        ) : isDragActive ? (
                            <Text fontWeight="medium" >
                                Release to upload files...
                                <VisuallyHidden>Drop your files here</VisuallyHidden>
                            </Text>
                        ) : (
                            <>
                                <Text fontWeight="medium"  >{placeholder}</Text>
                                <Text fontSize="sm">
                                    Supported formats: {supportedExtensions.replace(/\./g, '')}
                                </Text>
                                <Text fontSize="xs">
                                    Maximum size: {maxSize} MB {multiple ? "(Multiple files allowed)" : "(Single file only)"}
                                </Text>
                            </>
                        )}
                    </VStack>
                </VStack>
                <Toaster />
            </Box>
        </Box >
    )

});
