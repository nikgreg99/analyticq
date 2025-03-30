import React from "react";
import {
    Box,
    VStack,
    HStack,
    Heading,
    Text,
    Badge,
    IconButton,
} from  "@chakra-ui/react";
import { MdDelete } from "react-icons/md";
import { FaDeleteLeft } from "react-icons/fa6";


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

    const sortedFiles = [...files].sort((a,b) => a.name.localeCompare(b.name));

    const formatSize = (size) => {
        const units = ["Bytes", "KB", "MB", "GB", "TB"]
        let unitIndex = 0;
        let fileSize = size;
        while(fileSize >= 1024 &&  unitIndex < units.length - 1){
            fileSize /= 1024;
            unitIndex++;
        }
        return `${fileSize.toFixed(2)} ${units[unitIndex]}`;
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
                <IconButton
                    bg="blackAlpha.900"
                    color="whiteAlpha.900"
                    variant="solid"
                    size="xs"
                    onClick={onDeleteAllFiles}
                >
                    <MdDelete/>
                    Delete All
                </IconButton>
            )
            }</HStack>
            {sortedFiles.map((file) => (
                <Box
                    key={file.name} // Use file name as key if unique
                    color="gray.600"
                    display="flex"
                    justifyContent="space-between"
                    role="listitem"
                >
                    <Box flex="1" display="flex" justifyContent="space-between" alignItems="center">
                        <Text color="GrayText">{file.name}</Text>
                        <Text color="GrayText">{formatSize(file.size)}</Text>
                    </Box>
                    {onDeleteFile && (
                        <IconButton
                            bg="transparent"
                            marginLeft="1em"
                            aria-label={`Delete file ${file.name}`}
                            size="xs"
                            onClick={() => onDeleteFile(file)}
                        >
                            <FaDeleteLeft size={12}/>
                        </IconButton>
                    )}
                </Box>
            ))}
    </VStack>
    );
};
