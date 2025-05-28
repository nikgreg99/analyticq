import React, { useState, useMemo, useCallback, useRef, useEffect } from "react";
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
  Text,
  Kbd,
  VStack
} from "@chakra-ui/react";
import {
  FaFileDownload,
  FaFilePdf,
  FaFileCode,
  FaFileAlt,
  FaFileCsv,
  FaKeyboard,
} from "react-icons/fa";
import { FiChevronDown, FiChevronUp } from "react-icons/fi";
import { Toaster, toaster } from "../general/Toaster";

const EXPORT_FORMATS = [
  {
    id: "pdf",
    label: "PDF Document",
    icon: FaFilePdf,
    color: "red.500",
    description: "Portable Document Format",
    shortcut: "P"
  },
  {
    id: "html",
    label: "HTML Document",
    icon: FaFileCode,
    color: "orange.500",
    description: "Web page format",
    shortcut: "H"
  },
  {
    id: "json",
    label: "JSON Data",
    icon: FaFileAlt,
    color: "blue.500",
    description: "Structured data format",
    shortcut: "J"
  },
  {
    id: "csv",
    label: "CSV Spreadsheet",
    icon: FaFileCsv,
    color: "green.500",
    description: "Comma-separated values",
    shortcut: "C"
  },
];

// Global shortcut combinations
const SHORTCUT_COMBINATIONS = {
  // Ctrl/Cmd + Shift + [Letter] for each format
  pdf: { key: "P", ctrl: true, shift: true },
  html: { key: "H", ctrl: true, shift: true },
  json: { key: "J", ctrl: true, shift: true },
  csv: { key: "C", ctrl: true, shift: true },
  // Quick menu toggle
  menu: { key: "E", ctrl: true, shift: true }, // Ctrl/Cmd + Shift + E to open menu
};

// Helper function to detect Mac platform
const isMacPlatform = () => {
  // Modern approach using User-Agent Client Hints API
  if (navigator.userAgentData) {
    return navigator.userAgentData.platform.toLowerCase().includes('mac');
  }

  // Fallback to user agent string parsing
  return /Mac|iPhone|iPad|iPod/.test(navigator.userAgent);
};

/**
 * A component that provides export functionality for scan reports in various formats
 * Enhanced with keyboard shortcuts for quick access and arrow key navigation
 */
export const ScanExportReport = ({
  scanId,
  isCompact = false,
  enabledFormats = EXPORT_FORMATS.map(f => f.id),
  enableKeyboardShortcuts = true,
  showShortcutHints = true
}) => {
  const [menuOpened, setMenuOpened] = useState(false);
  const [activeFormat, setActiveFormat] = useState(null);
  const [shortcutPressed, setShortcutPressed] = useState(null);
  const [focusedIndex, setFocusedIndex] = useState(-1);
  const { downloadReport, isDownloading } = useDownloadScanReport();
  const menuTriggerRef = useRef(null);
  const menuItemRefs = useRef({});

  const exportFormats = useMemo(
    () => EXPORT_FORMATS.filter(format => enabledFormats.includes(format.id)),
    [enabledFormats]
  );

  // Initialize menu item refs
  useEffect(() => {
    exportFormats.forEach(format => {
      if (!menuItemRefs.current[format.id]) {
        menuItemRefs.current[format.id] = React.createRef();
      }
    });
  }, [exportFormats]);

  const handleExport = useCallback(
    async (formatId, triggeredBy = 'click') => {
      if (isDownloading) return;

      const format = exportFormats.find(f => f.id === formatId);
      if (!format) return;

      setActiveFormat(formatId);

      // Show visual feedback for keyboard shortcuts
      if (triggeredBy === 'keyboard') {
        setShortcutPressed(formatId);
        setTimeout(() => setShortcutPressed(null), 200);
      }

      try {
        await downloadReport(scanId, formatId);
        toaster.create({
          title: "Export successful",
          description: `Report exported in ${format.label} format${triggeredBy === 'keyboard' ? ' (via shortcut)' : ''}`,
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
      } finally {
        setActiveFormat(null);
        setMenuOpened(false);
        setFocusedIndex(-1);
      }
    },
    [downloadReport, isDownloading, scanId, exportFormats],
  );

  const handleMenuDown = useCallback((event) => {
    if (event.key === 'Escape') {
      setMenuOpened(false);
      setFocusedIndex(-1);
      menuTriggerRef.current?.focus();
    }
  }, []);

  // Focus management helper
  const focusMenuItem = useCallback((index) => {
    if (index >= 0 && index < exportFormats.length) {
      const formatId = exportFormats[index].id;
      const itemRef = menuItemRefs.current[formatId];
      if (itemRef && itemRef.current) {
        itemRef.current.focus();
        setFocusedIndex(index);
      }
    }
  }, [exportFormats]);

  // Keyboard shortcut handler
  const handleKeyboardShortcut = useCallback((event) => {
    if (!enableKeyboardShortcuts || isDownloading) return;

    const isMac = isMacPlatform();
    const ctrlKey = isMac ? event.metaKey : event.ctrlKey;

    // Check if the correct modifier keys are pressed
    if (!ctrlKey || !event.shiftKey) return;

    const pressedKey = event.key.toLowerCase();

    // Handle menu toggle shortcut
    if (pressedKey === SHORTCUT_COMBINATIONS.menu.key.toLowerCase()) {
      event.preventDefault();
      setMenuOpened(prev => {
        const newState = !prev;
        if (newState) {
          // Focus first item when opening menu
          setTimeout(() => focusMenuItem(0), 100);
        } else {
          setFocusedIndex(-1);
        }
        return newState;
      });
      return;
    }

    // Handle format-specific shortcuts
    const formatShortcut = Object.entries(SHORTCUT_COMBINATIONS).find(([_, combo]) =>
      combo.key.toLowerCase() === pressedKey && combo.ctrl && combo.shift
    );

    if (formatShortcut) {
      const [formatId] = formatShortcut;
      const format = exportFormats.find(f => f.id === formatId);

      if (format) {
        event.preventDefault();
        handleExport(formatId, 'keyboard');
      }
    }
  }, [enableKeyboardShortcuts, isDownloading, exportFormats, handleExport, focusMenuItem]);

  // Menu navigation with arrow keys
  const handleMenuKeyDown = useCallback((event) => {
    if (!menuOpened) return;

    const menuItems = exportFormats;
    let newIndex = focusedIndex;

    switch (event.key) {
      case 'ArrowDown':
        event.preventDefault();
        newIndex = focusedIndex < menuItems.length - 1 ? focusedIndex + 1 : 0;
        focusMenuItem(newIndex);
        break;
      case 'ArrowUp':
        event.preventDefault();
        newIndex = focusedIndex > 0 ? focusedIndex - 1 : menuItems.length - 1;
        focusMenuItem(newIndex);
        break;
      case 'Enter':
      case ' ':
        event.preventDefault();
        if (focusedIndex >= 0 && focusedIndex < menuItems.length) {
          handleExport(menuItems[focusedIndex].id, 'keyboard');
        }
        break;
      case 'Home':
        event.preventDefault();
        focusMenuItem(0);
        break;
      case 'End':
        event.preventDefault();
        focusMenuItem(menuItems.length - 1);
        break;
    }
  }, [menuOpened, exportFormats, focusedIndex, handleExport, focusMenuItem]);

  // Set up global keyboard event listeners
  useEffect(() => {
    if (!enableKeyboardShortcuts) return;

    document.addEventListener('keydown', handleKeyboardShortcut);
    return () => document.removeEventListener('keydown', handleKeyboardShortcut);
  }, [handleKeyboardShortcut, enableKeyboardShortcuts]);

  // Reset focused index when menu closes
  useEffect(() => {
    if (!menuOpened) {
      setFocusedIndex(-1);
    }
  }, [menuOpened]);

  // Responsive settings
  const buttonSize = useBreakpointValue({
    base: "sm",
    md: isCompact ? "sm" : "md",
  });
  const showLabel = useBreakpointValue({ base: false, sm: true });

  const isLoading = isDownloading || activeFormat !== null;
  const loadingText = activeFormat ? `Exporting ${activeFormat.toUpperCase()}...` : "Exporting...";

  // Get shortcut display text
  const getShortcutText = (formatId) => {
    const isMac = isMacPlatform();
    const ctrlText = isMac ? '⌘' : 'Ctrl';
    const combo = SHORTCUT_COMBINATIONS[formatId];
    return combo ? `${ctrlText}+Shift+${combo.key}` : '';
  };

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
        onOpenChange={(details) => {
          setMenuOpened(details.open);
          if (details.open) {
            // Focus first item when menu opens
            setTimeout(() => focusMenuItem(0), 100);
          }
        }}
        closeOnSelect={false}
        onEscapeKeyDown={handleMenuDown}
      >
        <Menu.Trigger asChild>
          <DownloadTrigger asChild>
            <Button
              ref={menuTriggerRef}
              variant="subtle"
              size={buttonSize}
              loading={isLoading}
              loadingText={loadingText}
              disabled={isDownloading}
              aria-label={
                isCompact
                  ? "Export scan report"
                  : enableKeyboardShortcuts
                    ? "Export scan report in various formats (Ctrl+Shift+E for menu)"
                    : "Export scan report in various formats"
              }
              aria-haspopup="menu"
              aria-expanded={menuOpened}
              spinnerPlacement="start"
              spinner={<Spinner size="sm" color="current" />}
              data-testid="export-report-button"
              onKeyDown={handleMenuKeyDown}
              _focus={{
                outline: "2px solid",
                outlineColor: "blue.500",
                outlineOffset: "2px",
              }}
            >
              <FaFileDownload />
              {showLabel && (isCompact ? "Export" : "Export Report")}
              {enableKeyboardShortcuts && !isCompact && <FaKeyboard size="12px" opacity={0.6} />}
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
              maxW="280px"
              onKeyDown={handleMenuKeyDown}
            >
              {exportFormats.map((exportFormat, index) => (
                <Menu.Item
                  key={exportFormat.id}
                  ref={menuItemRefs.current[exportFormat.id]}
                  value={exportFormat.id}
                  cursor="pointer"
                  onClick={() => handleExport(exportFormat.id, 'click')}
                  disabled={isLoading}
                  aria-label={`Export as ${exportFormat.label}${enableKeyboardShortcuts ? ` (${getShortcutText(exportFormat.id)})` : ''}`}
                  data-testid={`export-${exportFormat.id}`}
                  role="menuitem"
                  tabIndex={focusedIndex === index ? 0 : -1}
                  _focus={{ outline: "2px solid blue.500" }}
                  bg={
                    shortcutPressed === exportFormat.id
                      ? "Highlight"
                      : focusedIndex === index
                        ? "Highlight"
                        : "transparent"
                  }
                  px={4}
                  py={3}
                  onMouseEnter={() => setFocusedIndex(index)}
                  onFocus={() => setFocusedIndex(index)}
                >
                  <HStack spacing={3} justify="space-between" width="auto">
                    <HStack spacing={3} flex={1}>
                      <Icon
                        as={exportFormat.icon}
                        color={exportFormat.color}
                        aria-hidden="true"
                        flexShrink={0}
                      />
                      <VStack align="start" spacing={0} flex="1">
                        <Text fontSize="sm" fontWeight="medium">
                          {exportFormat.label}
                        </Text>
                        {!isCompact && (
                          <Text fontSize="xs" color="gray.600">
                            {exportFormat.description}
                          </Text>
                        )}
                      </VStack>
                    </HStack>
                    <HStack spacing={2}>
                      {activeFormat === exportFormat.id && (
                        <Spinner size="sm" />
                      )}
                      {enableKeyboardShortcuts && showShortcutHints && (
                        <Kbd fontSize="xs" py={0.5} px={1}>
                          {getShortcutText(exportFormat.id)}
                        </Kbd>
                      )}
                    </HStack>
                  </HStack>
                </Menu.Item>
              ))}

              {enableKeyboardShortcuts && showShortcutHints && (
                <Box px={4} py={2} borderTop="1px solid" borderColor="gray.200">
                  <VStack spacing={1}>
                    <HStack spacing={2} justify="center">
                      <Icon as={FaKeyboard} size="sm" color="gray.500" />
                      <Text fontSize="xs" color="gray.600">
                        Use shortcuts for quick export
                      </Text>
                    </HStack>
                    <Text fontSize="xs" color="gray.500" textAlign="center">
                      ↑↓ Navigate • Enter/Space Select • Esc Close
                    </Text>
                  </VStack>
                </Box>
              )}
            </Menu.Content>
          </Menu.Positioner>
        </Portal>
      </Menu.Root>
      <Toaster />
    </Box>
  );
};

ScanExportReport.displayName = "ScanExportReport";
