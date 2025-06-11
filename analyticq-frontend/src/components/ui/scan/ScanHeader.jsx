import React, { useRef } from "react";
import { formatDate, getTimeSince } from "components/utils/time";
import {
  Box,
  Text,
  Grid,
  GridItem,
  HStack,
  VStack,
  Heading,
  Badge,
  Stack,
  Flex,
  Separator,
} from "@chakra-ui/react";
import { Toaster } from "../general/Toaster";
import { FaCalendar, FaClock, FaInfoCircle, FaTag } from "react-icons/fa";
import { ScanExportReport } from "./ScanExportReport";
import { useDeleteScan } from "hooks/useDeleteScan";
import DeleteConfirmationDialog from "../general/DeleteConfirmationDialog";

/**
 * Component that displays the header section of a scan detail page
 * with improved layout and responsive design.
 *
 * @component
 * @param {Object} props - Component props
 * @param {Object} props.scanData - The scan data to display in the header
 * @returns {JSX.Element} A header section with scan information
 */
export const ScanHeader = ({ scanData }) => {
  const cancelRef = useRef();
  const {
    isDeleting,
    isDialogOpen: deleteDialogOpened,
    setIsDialogOpen: setDeleteDialogOpened,
    handleDelete,
  } = useDeleteScan(scanData);

  return (
    <Box
      as="section"
      aria-labelledby="scan-header-title"
      borderRadius="lg"
      borderWidth="1px"
      p={{ base: 3, md: 5 }}
      shadow="md"
      w="full"
    >
      <Stack
        direction={{ base: "column", md: "row" }}
        justify="space-between"
        spacing={{ base: 4, md: 6 }}
        align="start"
      >
        {/* Left Section - Scan Title and Metadata */}
        <VStack spacing={3} align="start" flex="1" width="full">
          <Flex
            width="full"
            direction={{ base: "column", sm: "row" }}
            justify="space-between"
            align={{ base: "start", sm: "center" }}
            gap={2}
          >
            <HStack spacing={2} wrap="wrap">
              <Heading
                id="scan-header-title"
                size="md"
                color="blackAlpha.800"
                wordBreak="break-word"
                fontWeight="600"
              >
                SAST Scan Results #{scanData.id}
              </Heading>
              <Badge
                colorScheme="blue"
                fontSize="xs"
                px={2}
                py={0.5}
                borderRadius="md"
              >
                <HStack spacing={1}>
                  <FaTag />
                  <Text>{scanData.tool_name}</Text>
                </HStack>
              </Badge>
            </HStack>
          </Flex>

          <HStack spacing={1}>
            <FaClock size={14} color="gray" />
            <Text fontSize="sm" color="gray.600">
              Last updated {getTimeSince(scanData.updated_at)}
            </Text>
          </HStack>

          <Text fontSize="sm" color="gray.600" mt={1}>
            {scanData.description || "No description provided for this scan."}
          </Text>
        </VStack>

        {/* Right Section - Scan Info Card */}
        <Box
          p={4}
          borderRadius="md"
          borderWidth="1px"
          minW={{ base: "100%", md: "280px" }}
          bg="gray.50"
          alignSelf="stretch"
        >
          <HStack spacing={2} mb={3}>
            <FaInfoCircle size={14} color="gray.600" aria-hidden="true" />
            <Text fontWeight="semibold" fontSize="sm" color="blackAlpha.800">
              Scan Information
            </Text>
          </HStack>

          <Separator mb={3} />

          <Grid
            templateColumns="auto 1fr"
            gap={2}
            alignItems="center"
            color="blackAlpha.800"
            fontSize="sm"
          >
            <GridItem fontWeight="medium">
              <HStack spacing={2} align="center">
                <FaCalendar size={12} />
                <Text>Created:</Text>
              </HStack>
            </GridItem>
            <GridItem>{formatDate(scanData.created_at)}</GridItem>

            <GridItem fontWeight="medium">
              <HStack spacing={2} align="center">
                <FaClock size={12} />
                <Text>Updated:</Text>
              </HStack>
            </GridItem>
            <GridItem>{formatDate(scanData.updated_at)}</GridItem>
          </Grid>

          <Box mt={4}>
            <HStack>
              <ScanExportReport scanId={scanData.scan_id} isCompact={true} />

              <DeleteConfirmationDialog
                isOpenModal={deleteDialogOpened}
                setIsOpenModal={setDeleteDialogOpened}
                itemName={scanData.id}
                itemType="scan"
                isLoading={isDeleting}
                onConfirm={handleDelete}
                cancelRef={cancelRef}
              />
            </HStack>
          </Box>
        </Box>
      </Stack>
      <Toaster />
    </Box>
  );
};

ScanHeader.displayName = "ScanHeader";
