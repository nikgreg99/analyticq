import React, {
  forwardRef,
  useImperativeHandle,
  useState,
  useEffect,
  useCallback,
} from "react";
import {
  Box,
  VStack,
  Text,
  VisuallyHidden,
  Flex,
  Icon,
} from "@chakra-ui/react";
import { useDropzone } from "react-dropzone";
import { FaCloudUploadAlt, FaExclamationTriangle } from "react-icons/fa";
import { AiOutlineFileZip } from "react-icons/ai";
import { useColorModeValue } from "../general/ColorMode"; // Maintaining custom colorMode
import { toaster, Toaster } from "components/ui/general/Toaster";

/**
 * A customizable file drop zone component that allows users to drag and drop files or click to select them.
 *
 * @component
 * @param {Object} props - The component props
 * @param {Function} props.onDrop - Callback function triggered when files are dropped or selected
 * @param {Object} [props.accept={}] - Object specifying accepted file types
 * @param {boolean} [props.multiple=false] - Whether to allow multiple file selection
 * @param {string} [props.placeholder="Drag and drop your codebase here, or click to select it"] - Custom placeholder text
 * @param {number} [props.maxSize=100] - Maximum file size in MB
 * @param {string|number} [props.height="auto"] - Height of the dropzone
 * @param {string|number} [props.width="100%"] - Width of the dropzone
 * @param {boolean} [props.disabled=false] - Whether the dropzone is disabled
 * @param {React.Ref} ref - Forwarded ref with reset and openFileDialog methods
 *
 * @returns A styled drop zone component with upload icon and customizable text
 *
 * @example
 * <FileDropZone
 *   onDrop={(files) => handleFiles(files)}
 *   accept={{ 'application/zip': ['.zip'], 'application/x-tar': ['.tar', '.gz'] }}
 *   multiple={true}
 *   placeholder="Custom drop zone text"
 * />
 */
export const FileDropZone = forwardRef(
  (
    {
      onDrop,
      accept = {},
      multiple = false,
      placeholder = "Drag your codebase here ",
      maxSize = 100,
      height = "auto",
      width = "100%",
      disabled = false,
    },
    ref,
  ) => {
    const [error, setError] = useState(null);
    const [isUploading, setIsUploading] = useState(false);
    const maxSizeInBytes = maxSize * 1024 * 1024; // Convert MB to bytes

    // Memoize callback functions to prevent unnecessary re-renders
    const handleDrop = useCallback(
      (acceptedFiles) => {
        setError(null);
        setIsUploading(true);
        // Simulate async operation (remove if not needed)
        setTimeout(() => {
          setIsUploading(false);
          onDrop(acceptedFiles);
        }, 300);
      },
      [onDrop]
    );

    const handleDropRejected = useCallback(
      (fileRejections) => {
        const errorMsg =
          fileRejections[0]?.errors[0]?.message || "File not accepted";
        setError(errorMsg);
        toaster.create({
          title: "Upload file rejected",
          description: errorMsg,
          type: "error",
          duration: 3000,
        });
      },
      []
    );

    const {
      getRootProps,
      getInputProps,
      isDragActive,
      isDragAccept,
      isDragReject,
      open,
    } = useDropzone({
      onDrop: handleDrop,
      onDropRejected: handleDropRejected,
      accept,
      multiple,
      maxSize: maxSizeInBytes,
      disabled,
      noClick: disabled,
      noKeyboard: disabled,
    });

    // Custom color mode values
    const dropzoneBackground = useColorModeValue("gray.100", "gray.700");
    const dropZoneBorder = useColorModeValue("gray.300", "gray.600");
    const hoverBackground = useColorModeValue("gray.200", "gray.600");
    const activeColor = useColorModeValue("blue.500", "blue.300");
    const errorColor = useColorModeValue("red.500", "red.300");
    const textColor = useColorModeValue("gray.800", "whiteAlpha.800");

    useEffect(() => {
      // Cleanup function
      return () => {
        setError(null);
        setIsUploading(false);
      };
    }, []);

    // Determine dropzone state colors
    const getBorderColor = () => {
      if (isDragReject || error) return errorColor;
      if (isDragAccept) return "green.400";
      if (isDragActive) return activeColor;
      return dropZoneBorder;
    };

    // Create a function to get background color based on state
    const getBackgroundColor = () => {
      if (isDragReject || error) return `${errorColor}10`;
      if (isDragAccept) return "green.50";
      if (isDragActive) return `${activeColor}10`;
      return dropzoneBackground;
    };

    // Expose methods via ref
    useImperativeHandle(
      ref,
      () => ({
        reset: () => {
          setError(null);
          setIsUploading(false);
          const fileInput = document.querySelector('input[type="file"]');
          if (fileInput) {
            fileInput.value = "";
            const event = new Event("input", { bubbles: true });
            fileInput.dispatchEvent(event);
            onDrop([]);
          }
        },
        openFileDialog: () => {
          if (!disabled && !isUploading) {
            open();
          }
        },
      }),
      [onDrop, open, disabled, isUploading]
    );

    const supportedExtensions = Object.values(accept).flat().join(", ");

    return (
      <Box
        position="relative"
        height={height}
        width={width}
        data-testid="file-dropzone"
      >
        <Box
          {...getRootProps()}
          border="2px dashed"
          borderColor={getBorderColor()}
          color={textColor}
          bg={getBackgroundColor()}
          textAlign="center"
          p={6}
          cursor={disabled || isUploading ? "not-allowed" : "pointer"}
          borderRadius="md"
          transition="all 0.3s ease"
          position="relative"
          height="100%"
          width="100%"
          display="flex"
          alignItems="center"
          justifyContent="center"
          _hover={disabled || isUploading ? {} : { bg: hoverBackground }}
          role="button"
          opacity={disabled ? 0.6 : 1}
          aria-label={
            disabled ? "File upload disabled" : "Drop zone for uploading files"
          }
          aria-disabled={disabled || isUploading}
          outline="none"
          _focus={{ boxShadow: "outline" }}
          data-state={
            error
              ? "error"
              : isUploading
              ? "uploading"
              : isDragActive
              ? "active"
              : "idle"
          }
        >
          <input
            {...getInputProps()}
            aria-label="File input"
            data-cy="dropzone-input"
          />
          <VStack spacing={4}>
            {error ? (
              <Icon
                as={FaExclamationTriangle}
                boxSize={12}
                color="red.800"
                aria-hidden="true"
              />
            ) : isUploading ? (
              <Box
                position="relative"
                width="48px"
                height="48px"
                aria-label="Uploading"
              >
                <Box
                  position="absolute"
                  top="0"
                  left="0"
                  width="100%"
                  height="100%"
                  borderRadius="50%"
                  border="3px solid"
                  borderColor={`${activeColor}40`}
                />
                <Box
                  position="absolute"
                  top="0"
                  left="0"
                  width="100%"
                  height="100%"
                  borderRadius="50%"
                  border="3px solid transparent"
                  borderTopColor={activeColor}
                  animation="spin 1s linear infinite"
                  sx={{
                    "@keyframes spin": {
                      "0%": { transform: "rotate(0deg)" },
                      "100%": { transform: "rotate(360deg)" },
                    },
                  }}
                />
              </Box>
            ) : (
              <Flex position="relative" justifyContent="center" width="100%">
                <Icon
                  as={FaCloudUploadAlt}
                  boxSize={isDragActive ? 16 : 12}
                  color={isDragActive ? activeColor : "currentColor"}
                  transition="all 0.3s ease"
                  aria-hidden="true"
                  animation={isDragActive ? "pulse 1.5s infinite" : "none"}
                  sx={{
                    "@keyframes pulse": {
                      "0%": { transform: "scale(1)" },
                      "50%": { transform: "scale(1.1)" },
                      "100%": { transform: "scale(1)" },
                    },
                  }}
                />

                {isDragActive && (
                  <Icon
                    as={AiOutlineFileZip}
                    boxSize={6}
                    position="absolute"
                    bottom="-10px"
                    right="calc(50% - 30px)"
                    color={activeColor}
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
              ) : isUploading ? (
                <Text fontWeight="medium">Processing your files...</Text>
              ) : isDragActive ? (
                <Text fontWeight="medium" color={activeColor}>
                  Release to upload files...
                  <VisuallyHidden>Drop your files here</VisuallyHidden>
                </Text>
              ) : (
                <>
                  <Text fontWeight="medium">{placeholder}</Text>
                  <Text fontSize="sm">
                    Supported formats: {supportedExtensions.replace(/\./g, "")}
                  </Text>
                  <Text fontSize="xs">
                    Maximum size: {maxSize} MB{" "}
                    {multiple
                      ? "(Multiple files allowed)"
                      : "(Single file only)"}
                  </Text>
                </>
              )}
            </VStack>
          </VStack>
          <Toaster />
        </Box>
      </Box>
    );
  }
);

FileDropZone.displayName = "FileDropZone";
