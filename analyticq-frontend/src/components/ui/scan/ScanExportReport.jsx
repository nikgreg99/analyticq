import React, { useState, useMemo, useCallback, useRef } from "react";
import { useDownloadScanReport } from "hooks/useDownloadScanReport";
import {
  Box,
  Button,
  DownloadTrigger,
  Menu,
  Portal,
  Icon,
  Spinner,
  useBreakpointValue,
  HStack,
} from "@chakra-ui/react";
import {
  FaFileDownload,
  FaFilePdf,
  FaFileCode,
  FaFileAlt,
  FaFileCsv,
} from "react-icons/fa";
import { FiChevronDown, FiChevronUp } from "react-icons/fi";
import { Toaster, toaster } from "../general/Toaster";


const EXPORT_FORMATS = [
  {
    id: "pdf",
    label: "PDF Document",
    icon: FaFilePdf,
    color: "red.500",
    description: "Portable Document Format"
  },
  {
    id: "html",
    label: "HTML Document",
    icon: FaFileCode,
    color: "orange.500",
    description: "Web page format"
  },
  {
    id: "json",
    label: "JSON Data",
    icon: FaFileAlt,
    color: "blue.500",
    description: "Structured data format"
  },
  {
    id: "csv",
    label: "CSV Spreadsheet",
    icon: FaFileCsv,
    color: "green.500",
    description: "Comma-separated values"
  },
];

/**
 * A component that provides export functionality for scan reports in various formats
 */
export const ScanExportReport = ({
  scanId,
  isCompact = false,
  enabledFormats = EXPORT_FORMATS.map(f => f.id)
 }) => {
  const [menuOpened, setMenuOpened] = useState(false);
  const [activeFormat, setActiveFormat] = useState(null);
  const { downloadReport, isDownloading } = useDownloadScanReport();
  const menuTriggerRef = useRef(null);

  const exportFormats = useMemo(
    () => EXPORT_FORMATS.filter(format => enabledFormats.includes(format.id)),
    [enabledFormats]
  );

  const handleExport = useCallback(
    async (format) => {
      if (isDownloading) return;

      setActiveFormat(format);

      try {
        await downloadReport(scanId, format);
        toaster.create({
          title: "Export successful",
          description: `Report exported in ${format.toUpperCase()} format`,
          type: "success",
          closable: true,
          placement: "top-end",
          max: 4,
        });
      } catch (error) {
        console.error("Export error", error);
        const errorMessage =
          error.response?.data?.message ||
          "Could not download the report. Please try again.";
        toaster.create({
          title: "Export failed",
          description: errorMessage,
          type: "error",
          placement: "top-end",
          closable: true,
          max: 4,
        });
      }
      finally {
        setActiveFormat(null);
      }
    },
    [downloadReport, isDownloading, scanId],
  );

  const handleMenuDown = useCallback((event) => {
    if(event.key === 'Escape'){
       setMenuOpened(false);
       menuTriggerRef.current?.focus();
    }
  },[])

  // Responsive settings
  const buttonSize = useBreakpointValue({
    base: "sm",
    md: isCompact ? "sm" : "md",
  });
  const showLabel = useBreakpointValue({ base: false, sm: true });

  const isLoading = isDownloading || activeFormat !== null;
  const loadingText = activeFormat ? `Exporting ${activeFormat.toUpperCase()}...` : "Exporting...";

  // Validation
  if (!scanId) {
    console.warn("ScanExportReport: scanId is required");
    return null;
  }

  if (exportFormats.length === 0) {
    console.warn("ScanExportReport: No valid export formats available");
    return null;
  }

  return (
    <Box alignSelf="center" position="relative">
      <Menu.Root
        positioning="bottom-end"
        lazyMount
        open={menuOpened}
        onOpenChange={() => setMenuOpened(!menuOpened)}
        closeOnSelect
        onEscapeKeyDown={handleMenuDown}
      >
        <Menu.Trigger asChild>
          <DownloadTrigger
            asChild
          >
            <Button
              ref={menuTriggerRef}
              variant="subtle"
              size={buttonSize}
              loading={isLoading}
              loadingText={loadingText}
              disabled={isDownloading}
              aria-label={isCompact ? "Export scan report" : "Export scan report in various formats"}
              aria-haspopup="menu"
              aria-expanded={menuOpened}
              spinnerPlacement="start"
              spinner={<Spinner size="sm" color="current" />}
              data-testid="export-report-button"
              _focus={{
                outline: "2px solid",
                outlineColor: "blue.500",
                outlineOffset: "2px",
              }}
            >
              <FaFileDownload />
              {showLabel && (isCompact ? "Export" : "Export Report")}
              {menuOpened ? <FiChevronUp /> : <FiChevronDown />}
            </Button>
          </DownloadTrigger>
        </Menu.Trigger>
        <Portal>
          <Menu.Positioner>
            <Menu.Content
              data-testid="export-menu"
              borderRadius="md"
              width={{ base: "full", sm: "auto" }}
              maxW="240px"
            >
              {exportFormats.map((exportFormat) => (
                <Menu.Item
                  key={exportFormat.id}
                  value={exportFormat.id}
                  cursor="pointer"
                  onClick={() => handleExport(exportFormat.id)}
                  disabled={isLoading}
                  aria-label={`Export as ${exportFormat.label}`}
                  data-testid={`export-${exportFormat.id}`}
                  role="menuitem"
                  _hover={{ bg: "gray.100" }}
                  px={4}
                  closeOnSelect
                >
                  <HStack spacing={3}>
                    <Icon
                      as={exportFormat.icon}
                      color={exportFormat.color}
                      boxSize={4}
                      aria-hidden="true"
                      flexShrink={0}
                    />
                    <Box flex="1">{exportFormat.label}</Box>
                    {activeFormat === exportFormat.id && <Spinner size="sm" ml="auto" />}
                  </HStack>
                </Menu.Item>
              ))}
            </Menu.Content>
          </Menu.Positioner>
        </Portal>
      </Menu.Root>
      <Toaster />
    </Box>
  );
};

ScanExportReport.displayName = "ScanExportReport";
