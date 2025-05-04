import React, { useState, useMemo, useCallback } from "react";
import { useDownloadScanReport } from "hooks/useDownloadScanReport";
import {
    Box,
    Button,
    Menu,
    Portal,
    Icon,
    Spinner
} from "@chakra-ui/react";
import { FaFileDownload, FaFilePdf, FaFileCode, FaFileAlt, FaFileCsv } from "react-icons/fa";
import { FiChevronDown, FiChevronUp } from "react-icons/fi";
import { Toaster, toaster } from "./toaster";

/**
 * A component that provides export functionality for scan reports in various formats
 * @component
 * @param {Object} props - Component props
 * @param {string} props.scanId - The ID of the scan to be exported
 * @param {boolean} [props.isCompact=false] - Whether to display the component in compact mode
 * @returns {JSX.Element} A menu button component with export options for PDF, HTML, JSON and CSV formats
 *
 * @example
 * <ExportScanReport scanId="123" isCompact={false} />
 */
export const ExportScanReport = ({ scanId, isCompact = false }) => {

    const [menuOpened, setMenuOpened] = useState(false);
    const {downloadReport, isDownloading } = useDownloadScanReport();

    const exportFormats = useMemo(() => [
        {
            id: "pdf",
            label: "PDF Document",
            icon: FaFilePdf,
            color: "red.500"
        },
        {
            id: "html",
            label: "HTML Document",
            icon: FaFileCode,
            color: "orange.500"
        },
        {
            id: "json",
            label: "JSON Data",
            icon: FaFileAlt,
            color: "blue.500"
        },
        {
            id: "csv",
            label: "CSV Spreadsheet",
            icon: FaFileCsv,
            color: "green.500"
        }
    ], []);

    const handleExport = useCallback(async (format) => {

        if (isDownloading) return;

        try {
            await downloadReport(scanId, format);
            toaster.create({
                title: "Export successful",
                description: `Report exported in ${format.toUpperCase()} format`,
                type: "success",
                placement: "top-end",
                max: 4
            });
        }
        catch (error) {
            console.error("Export error", error);
            const errorMessage = error.response?.data?.message || "Could not download the report. Please try again.";
            toaster.create({
                title: "Export failed",
                description: errorMessage,
                type: "error",
                placement: "top-end",
                max: 4
            })
        }
    }, [downloadReport, isDownloading, scanId]);

    return (
        <Box
            alignSelf="center"
            position="relative"
        >
            <Menu.Root
                positioning="center"
                lazyMount
                open={menuOpened}
                onOpenChange={() => setMenuOpened(!menuOpened)}

            >
                <Menu.Trigger asChild>
                    <Button
                        variant="subtle"
                        size={isCompact ? "sm" : "md"}
                        loadingText="Exporting..."
                        loading={isDownloading}
                        disabled={isDownloading}
                        aria-label="Export report"
                        aria-haspopup="menu"
                        aria-expanded={menuOpened}
                        spinnerPlacement="start"
                        spinner={<Spinner size="sm"/>}
                        data-testid="export-report-button"
                    >
                        {menuOpened ? <FiChevronUp /> : <FiChevronDown />}
                        {isCompact ? "Export" : "Export Report"}
                        <FaFileDownload />
                    </Button>
                </Menu.Trigger>
                <Portal>
                    <Menu.Positioner>
                        <Menu.Content
                              data-testid="export-menu"
                              borderRadius="md"
                        >
                            {exportFormats.map((exportFormat) => (
                                <Menu.Item
                                    key={exportFormat.id}
                                    value={exportFormat.id}
                                    onClick={() => handleExport(exportFormat.id)}
                                    disabled={isDownloading}
                                    aria-label={`Export as ${exportFormat.label}`}
                                    data-testid={`export-${exportFormat.id}`}
                                    role="menuitem"
                                >
                                    <Icon
                                        as={exportFormat.icon}
                                        color={exportFormat.color}
                                        boxSize={4}
                                        mr={2}
                                        aria-hidden="true"
                                    />
                                    <Box flex={1}>{exportFormat.label}</Box>
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
