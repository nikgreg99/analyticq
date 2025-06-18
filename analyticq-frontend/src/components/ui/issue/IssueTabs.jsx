import React, { useState, useMemo, useEffect, useCallback } from "react";
import {
  Box,
  Badge,
  Flex,
  Text,
  HStack,
  IconButton,
  Collapsible,
  Input,
  InputGroup,
  Select,
  Portal,
  Tabs,
  createListCollection,
  useBreakpointValue,
} from "@chakra-ui/react";
import { IssueListTab } from "./IssueListTab";
import { Tooltip } from "../general/Tooltip";
import { IoIosSearch } from "react-icons/io";
import { FaChevronUp, FaChevronDown } from "react-icons/fa6";
import { useIssueTabs } from "hooks/useIssueTabs";
import { useDebounce } from "use-debounce";

/**
 * A component that displays security issues in a tabbed interface with filtering and sorting capabilities.
 *
 * @component
 * @param {Object} props
 * @param {Object} props.scanData - The scan data containing security issues
 * @param {Array} props.scanData.issues - Array of security issues to display
 * @param {string} props.scanData.issues[].id - Unique identifier for each issue
 * @param {string} props.scanData.issues[].severity - Severity level of the issue (CRITICAL, HIGH, MEDIUM, LOW, INFO)
 *
 * @returns {JSX.Element} A tabbed interface showing filtered and sorted security issues with search and ordering capabilities
 *
 * @example
 * ```jsx
 * const scanData = {
 *   issues: [{
 *     id: "issue-1",
 *     severity: "HIGH",
 *     // ... other issue properties
 *   }]
 * };
 *
 * <IssueTabs scanData={scanData} />
 * ```
 */
export const IssueTabs = ({ scanData = { issues: [] } }) => {
  // Memoize static collections to prevent recreating on every render
  const orderingOptions = useMemo(() => createListCollection({
    items: [
      { label: "Severity", value: "severity" },
      { label: "Newest", value: "newest" },
      { label: "Oldest", value: "oldest" },
    ],
  }), []);

  const pageSizeOptions = useMemo(() => createListCollection({
    items: [
      { label: "5 per page", value: 5 },
      { label: "10 per page", value: 10 },
      { label: "25 per page", value: 25 },
      { label: "50 per page", value: 50 },
    ],
  }), []);

  const [filterOpen, setFilterOpen] = useState(false);
  const isMobile = useBreakpointValue({ base: true, md: false });

  // Add local state for immediate input feedback
  const [inputValue, setInputValue] = useState("");
  const [debouncedSearchTerm] = useDebounce(inputValue, 300);

  const severityConfig = useMemo(() => ({
    CRITICAL: { displayName: "Critical", color: "red", order: 1 },
    HIGH: { displayName: "High", color: "orange", order: 2 },
    MEDIUM: { displayName: "Medium", color: "yellow", order: 3 },
    LOW: { displayName: "Low", color: "green", order: 4 },
    INFO: { displayName: "Info", color: "blue", order: 5 },
    WARNING: { displayName: "Warning", color: "teal", order: 6 },
    UNKNOWN: { displayName: "Unknown", color: "gray", order: 7 },
  }), []);

  const {
    searchTerm,
    setSearchTerm,
    sortOrder,
    setSortOrder,
    activeTab,
    setActiveTab,
    currentPage,
    setCurrentPage,
    pageSize,
    setPageSize,
    tabsConfig,
    filteredSortedTabIssues,
  } = useIssueTabs(scanData.issues, severityConfig);

  // Initialize inputValue with searchTerm once
  useEffect(() => {
    setInputValue(searchTerm);
  }, [searchTerm]);

  // Update the actual search term when debounced value changes
  useEffect(() => {
    setSearchTerm(debouncedSearchTerm);
    setCurrentPage(1);
  }, [debouncedSearchTerm, setSearchTerm, setCurrentPage]);

  // Memoize event handlers to prevent child re-renders
  const handleFilterToggle = useCallback(() => {
    setFilterOpen(prev => !prev);
  }, []);

  const handleInputChange = useCallback((e) => {
    setInputValue(e.target.value);
  }, []);

  const handleSortOrderChange = useCallback((e) => {
    setSortOrder(e.value);
    setCurrentPage(1);
  }, [setSortOrder, setCurrentPage]);

  const handleTabChange = useCallback((e) => {
    setActiveTab(e.value);
    setCurrentPage(1);
  }, [setActiveTab, setCurrentPage]);

  const handleFilterOpenChange = useCallback((open) => {
    setFilterOpen(open);
  }, []);

  // Memoize filtered tabs to prevent unnecessary recalculations
  const visibleTabs = useMemo(() =>
    tabsConfig.filter((tab) => tab.count > 0),
    [tabsConfig]
  );

  // Memoize scrollbar styles to prevent object recreation
  const scrollbarStyles = useMemo(() => ({
    scrollbarWidth: "thin",
    "&::-webkit-scrollbar": {
      height: "6px",
    },
    "&::-webkit-scrollbar-thumb": {
      background: "#CBD5E0",
      borderRadius: "8px",
    },
  }), []);

  // Memoize animation styles
  const tabContentOpenStyles = useMemo(() => ({
    animationName: "fade-in, scale-in",
    animationDuration: "300ms",
  }), []);

  const tabContentClosedStyles = useMemo(() => ({
    animationName: "fade-out, scale-out",
    animationDuration: "120ms",
  }), []);

  return (
    <Box mb={8} borderWidth={1} borderRadius="lg" overflow="hidden">
      <Flex
        justify="space-between"
        align="center"
        p={4}
        borderBottomWidth="1px"
      >
        <Text fontWeight="medium" color="blackAlpha.800">
          Issue Explorer
        </Text>

        <HStack>
          <Tooltip content="Toggle filters">
            <IconButton
              size="sm"
              onClick={handleFilterToggle}
              aria-label={`${filterOpen ? "Collapse" : "Expand"} filters`}
              aria-expanded={filterOpen}
              variant="subtle"
            >
              {filterOpen ? <FaChevronUp /> : <FaChevronDown />}
            </IconButton>
          </Tooltip>
        </HStack>
      </Flex>

      <Collapsible.Root open={filterOpen} onOpenChange={handleFilterOpenChange}>
        <Collapsible.Content>
          <Box p={4} borderBottomWidth="1px">
            <Flex
              flexDir={{ base: "column", md: "row" }}
              gap={4}
              align="center"
              justify="space-between"
              flexWrap="wrap"
            >
              <InputGroup
                maxW={{ base: "100%", md: "300px" }}
                flex="1"
                endElement={
                  <IoIosSearch
                    style={{ position: "absolute", right: "8px", top: "10px" }}
                  />
                }
              >
                <Input
                  placeholder="Search issues..."
                  value={inputValue}
                  onChange={handleInputChange}
                  aria-label="Search issues..."
                  color="blackAlpha.800"
                />
              </InputGroup>

              <Select.Root
                collection={orderingOptions}
                value={sortOrder}
                onValueChange={handleSortOrderChange}
                maxW={{ base: "100%", md: "200px" }}
                width={isMobile ? "100%" : "150px"}
              >
                <Select.Control>
                  <Select.Trigger>
                    <Select.ValueText
                      placeholder="Select ordering"
                      aria-placeholder="Select ordering"
                      color="blackAlpha.900"
                    />
                  </Select.Trigger>
                  <Select.IndicatorGroup>
                    <Select.ClearTrigger />
                    <Select.Indicator />
                  </Select.IndicatorGroup>
                </Select.Control>
                <Portal>
                  <Select.Positioner>
                    <Select.Content>
                      {orderingOptions.items.map((order) => (
                        <Select.Item item={order} key={order.value}>
                          {order.label}
                          <Select.ItemIndicator />
                        </Select.Item>
                      ))}
                    </Select.Content>
                  </Select.Positioner>
                </Portal>
              </Select.Root>
            </Flex>

            <Tabs.Root
              variant="enclosed"
              lazyMount
              unmountOnExit
              value={activeTab}
              onValueChange={handleTabChange}
              defaultValue={["all"]}
              mt={4}
            >
              <Tabs.List
                overflowX="auto"
                overflowY="hidden"
                whiteSpace="nowrap"
                px={2}
                py={1}
                sx={scrollbarStyles}
              >
                {visibleTabs.map((tab) => (
                  <Tabs.Trigger key={tab.id} value={tab.id}>
                    {tab.label}
                    <Badge ml={2} colorPalette={tab.color}>
                      {tab.count}
                    </Badge>
                  </Tabs.Trigger>
                ))}
              </Tabs.List>
              <Tabs.Indicator rounded="lg" />
              {tabsConfig.map((tab) => (
                <Tabs.Content
                  key={tab.id}
                  value={tab.id}
                  p={4}
                  _open={tabContentOpenStyles}
                  _closed={tabContentClosedStyles}
                >
                  <IssueListTab
                    issues={filteredSortedTabIssues[tab.id]}
                    sortOrder={sortOrder}
                    pageSizeOptions={pageSizeOptions}
                    pageSize={pageSize}
                    setPageSize={setPageSize}
                    currentPage={currentPage}
                    setCurrentPage={setCurrentPage}
                  />
                </Tabs.Content>
              ))}
            </Tabs.Root>
          </Box>
        </Collapsible.Content>
      </Collapsible.Root>
    </Box>
  );
};

IssueTabs.displayName = "IssueTabs";
