import React, { useState, useCallback, useRef } from "react";
import { formatDate, getTimeSince } from "components/utils/time";
import { useNavigate } from "react-router-dom";
import {
  Box,
  Flex,
  Text,
  Grid,
  GridItem,
  HStack,
  VStack,
  Heading,
  IconButton,
  Separator,
  Badge
} from "@chakra-ui/react";
import { Tooltip } from "./Tooltip";
import { toaster, Toaster } from "./Toaster";
import { deleteScanById } from "services/scanService";
import { FaCalendar, FaCode, FaClock, FaEye, FaEyeSlash, FaInfoCircle } from "react-icons/fa";
import { ExportScanReport } from "./ExportScanReport";
import DeleteConfirmationDialog from "./DeleteConfirmationDialog";

/**
 * Header component for displaying SAST scan information
 * @component
 * @param {Object} props - Component props
 * @param {Object} props.scanData - Data object containing scan information
 * @param {string} props.scanData.scan_id - Unique identifier for the scan
 * @param {string} props.scanData.tool_name - Name of the SAST tool used
 * @param {string} props.scanData.created_at - Timestamp of scan creation
 * @param {string} props.scanData.updated_at - Timestamp of last scan update
 * @returns {JSX.Element} A header component displaying scan information with collapsible scan ID,
 *                       timestamps, and additional scan details in a responsive layout
 */
export const ScanHeader = ({ scanData }) => {

  const [showFullScanId, setShowFullScanId] = useState(false);
  const [deleteDialogOpened, setDeleteDialogOpened] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);
  const navigate = useNavigate();
  const cancelRef = useRef();


  const infoToast = {
    title: "Scan ID copied succesfully",
    type: "info",
    placement: "top-end",
    max: 4,
  }


  /**
   * Formats and returns the scan ID based on the showFullScanId flag.
   * If showFullScanId is true, returns the complete scan ID.
   * Otherwise, returns a truncated version showing first 6 and last 4 characters separated by ellipsis.
   *
   * @returns {string} The formatted scan ID string
   */
  const displayScanId = () => {
    if (showFullScanId) {
      return scanData.scan_id;
    }
    // Show first 6 and last 4 characters
    return `${scanData.scan_id.substring(0, 6)}...${scanData.scan_id.substring(scanData.scan_id.length - 4)}`;
  };

  /**
   * Handles the copy operation of a scan ID to the system clipboard.
   * When triggered, it copies the scan_id from scanData to the clipboard
   * and displays a toast notification using the infoToast configuration.
   *
   * @function
   * @returns {void}
   */
  const handleCopy = () => {
    navigator.clipboard.writeText(scanData.scan_id)
    toaster.create(infoToast);
  }

  const handleDeleteScan = useCallback(async () => {
    try {
      const contextId = scanData.context_id;
      await deleteScanById(scanData.id);
      setIsDeleting(true);
      toaster.create({
        title: "Scan deleted successfully",
        type: "success",
        placement: "top-end",
      });

      navigate(`/contexts/${contextId}`)


    }
    catch (error) {
      toaster.create({
        title: "Failed to delete scan",
        description: error.message,
        type: "error",
        placement: "top-end",
      });
    }
    finally {
      setIsDeleting(false);
      setDeleteDialogOpened(false);
    }

  }, [scanData, navigate]);


  return (
    <Box
      as="section"
      aria-labelledby="scan-header-title"
      borderRadius="md"
      borderWidth="1px"
      p={3}
      shadow="sm"
      w="full"
    >
      <Flex
        justify="space-between"
        align="center"
        direction={{ base: "column", md: "row" }}
        gap={2}
        mb={2}
      >
        <Flex
          direction="column"
          flex="1"
          width={{ base: "100%", md: "auto" }}
        >
          <HStack spacing={2} mb={2}>
            <Heading
              id="scan-header-title"
              size="md"
              color="blackAlpha.800"
            >SAST Scan Results {scanData.id}</Heading>
            <Badge colorScheme="blue" fontSize="xs">
              {scanData.tool_name}
            </Badge>
          </HStack>

          <VStack
            align="flex-start"
            spacing={2}
            width="100%"
          >
            <HStack spacing={1} width="100%">
              <FaCode size={14} color="black" />
              <Text fontSize="xs" fontFamily="mono" color="blackAlpha.800" aria-label="Scan ID">
                {displayScanId()}
              </Text>
              <IconButton
                size="xs"
                bg="transparent"
                aria-label={showFullScanId ? "Hide scan ID" : "Show full scan ID"}
                onClick={() => setShowFullScanId(!showFullScanId)}
                ml={1}
              >
                {showFullScanId ? <FaEyeSlash size={12} /> : <FaEye size={12} />}
              </IconButton>
              <Tooltip
                content="Copy scan ID"
                placement="top"
                showArrow
              >
                <IconButton
                  size="xs"
                  bg="transparent"
                  aria-label="Copy scan ID"
                  onClick={() => handleCopy(scanData.scan_id)}
                >
                  <FaCode color="black" size={12} />
                </IconButton>
              </Tooltip>
            </HStack>

            <HStack spacing={1}>
              <FaClock color="black" size={14} co="gray.600" aria-hidden="true" />
              <Text fontSize="xs" color="blackAlpha.800">
                Last updated {getTimeSince(scanData.updated_at)}
              </Text>
            </HStack>

            {/* Delete button positioned on the left side */}
            <DeleteConfirmationDialog
              isOpenModal={deleteDialogOpened}
              setIsOpenModal={setDeleteDialogOpened}
              itemName={displayScanId()}
              itemType="scan"
              isLoading={isDeleting}
              onConfirm={handleDeleteScan}
              cancelRef={cancelRef}
            />
          </VStack>
        </Flex>

        <Separator display={{ base: "none", md: "block" }} />

        <Box
          p={2}
          borderRadius="md"
          borderWidth="1px"
          minW={{ md: "200px" }}
          fontSize="xs"
          alignSelf={{ base: "stretch", md: "flex-start" }}
          width={{ base: "100%", md: "auto" }}
          mt={{ base: 2, md: 0 }}
          bg="gray.50"
        >
          <HStack spacing={1} mb={1}>
            <FaInfoCircle size={12} color="gray.600" aria-hidden="true" />
            <Text
              fontWeight="bold"
              fontSize="xs"
              color="blackAlpha.800"
            >
              Scan Info
            </Text>
          </HStack>

          <Separator my={1} />

          <Grid
            templateColumns="auto 1fr"
            gap={1}
            fontSize="xs"
            color="blackAlpha.800"
          >
            <GridItem fontWeight="medium">
              <HStack spacing={1} align="center">
                <FaCalendar size={12} aria-hidden="true" />
                <Text>Created:</Text>
              </HStack>
            </GridItem>
            <GridItem>{formatDate(scanData.created_at)}</GridItem>

            <GridItem fontWeight="medium">
              <HStack spacing={1} align="center">
                <FaClock size={12} aria-hidden="true" />
                <Text>Updated:</Text>
              </HStack>
            </GridItem>
            <GridItem>{formatDate(scanData.updated_at)}</GridItem>
          </Grid>

          <HStack
            mt={3}
            wordSpacing={2}
            width="auto"
          >
            <ExportScanReport
              scanId={scanData.scan_id}
              isCompact={true}
            />
          </HStack>
        </Box>
      </Flex>
      <Toaster />
    </Box>
  );
}
