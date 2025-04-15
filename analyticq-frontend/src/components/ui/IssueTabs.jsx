import React, { useState } from "react";
import {
    Box,
    Badge,
    VStack,
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
    createListCollection
} from "@chakra-ui/react";
import { IssueCard } from "./IssueCard";
import { Tooltip } from "./tooltip";
import { filterIssues, sortIssues } from "components/utils/issues";
import { IoIosSearch } from "react-icons/io";
import { FaChevronUp, FaChevronDown } from "react-icons/fa6";
import EmptyState from "components/layout/EmptyState";
import PaginationControls from "./PaginationControls";

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
    const [searchTerm, setSearchTerm] = useState("");
    const [filterOpen, setFilterOpen] = useState(false);
    const [sortOrder, setSortOrder] = useState([]);
    const [activeTab, setActiveTab] = useState("all");
    const [currentPage, setCurrentPage] = useState(1);
    const [pageSize, setPageSize] = useState([10]);

    const orderingOptions = createListCollection({
        items: [
            { label: "Severity", value: "severity" },
            { label: "Newest", value: "newest" },
            { label: "Oldest", value: "oldest" },
        ],
    });


    const pageSizeOptions = createListCollection({
        items: [
            { label: "5 per page", value: 5 },
            { label: "10 per page", value: 10 },
            { label: "25 per page", value: 25 },
            { label: "50 per page", value: 50 },
        ],
    });

    const severityConfig = {
        "CRITICAL": { displayName: "Critical", color: "red", order: 1 },
        "HIGH": { displayName: "High", color: "orange", order: 2 },
        "MEDIUM": { displayName: "Medium", color: "yellow", order: 3 },
        "LOW": { displayName: "Low", color: "green", order: 4 },
        "INFO": { displayName: "Info", color: "blue", order: 5 }
    };

    const getIssueCounts = () => {
        if (!scanData || !scanData.issues)
            return Object.keys(severityConfig).reduce((acc, key) => {
                acc[key.toLowerCase()] = 0;
                return acc;
            }, {});

        return scanData.issues.reduce((counts, issue) => {
            const severity = issue.severity || "UNKNOWN";
            counts[severity.toLowerCase()] = (counts[severity.toLowerCase()] || 0) + 1;
            return counts;
        }, Object.keys(severityConfig).reduce((acc, key) => {
            acc[key.toLowerCase()] = 0;
            return acc;
        }, {}));
    };

    const issueCounts = getIssueCounts();

    const renderIssueList = (issues) => {
        if (!issues) return null;

        const filteredIssues = filterIssues(issues, searchTerm);
        const sortedIssues = sortIssues(filteredIssues, sortOrder, severityConfig);

        if (!sortedIssues || sortedIssues.length === 0) {
            return (
                <>
                    <EmptyState
                        title="No issues found"
                        message="No issues found fot the following scan"
                    />
                </>

            );
        }

        const totalItems = sortedIssues.length;
        const totalPages = Math.ceil(totalItems / pageSize[0]);
        const startIndex = (currentPage - 1) * pageSize[0];
        const endIndex = Math.min(startIndex + pageSize[0], totalItems);
        const currentPageData = sortedIssues.slice(startIndex, endIndex);

        const shouldShowPagination =  totalItems >= 5;

        return (
            <>
            <VStack
                spacing={4}
                align="stretch"
                mt={4}
            >
                {currentPageData.map((issue) => (
                    <IssueCard key={issue.id} issue={issue} />
                ))}

            </VStack>
             {shouldShowPagination > 0 && (
                <Flex
                    justifyContent="space-between"
                    alignItems="center"
                    mt={6}
                    borderTopWidth="1px"
                    pt={4}
                >

                    <Select.Root
                        collection={pageSizeOptions}
                        value={pageSize}
                        onValueChange={(e) => {
                            setPageSize(e.value);
                            setCurrentPage(1); // Reset to first page when changing page size
                        }}
                        size="sm"
                        width="150px"
                    >
                        <Select.Control>
                            <Select.Trigger>
                                <Select.ValueText
                                    placeholder="Items per page"
                                    aria-label="Select items per page"
                                    color="blackAlpha.900"
                                />
                            </Select.Trigger>
                            <Select.IndicatorGroup>
                                <Select.Indicator />
                            </Select.IndicatorGroup>
                        </Select.Control>
                        <Portal>
                            <Select.Positioner>
                                <Select.Content>
                                    {pageSizeOptions.items.map((option) => (
                                        <Select.Item
                                            item={option}
                                            key={option.value}
                                        >
                                            {option.label}
                                            <Select.ItemIndicator />
                                        </Select.Item>
                                    ))}
                                </Select.Content>
                            </Select.Positioner>
                        </Portal>
                    </Select.Root>

                    {totalPages > 1 && (
                        <PaginationControls
                            total={totalItems}
                            pageSize={pageSize[0]}
                            currentPage={currentPage}
                            onPageChange={(page) => setCurrentPage(page)}
                        />
                    )}
                </Flex>
            )}
            </>
        );
    };

    const tabsConfig = [
        {
            id: "all",
            label: "All Issues",
            count: scanData.issues?.length || 0,
            color: "blue",
            filter: () => scanData.issues || [],
        },
        ...Object.entries(severityConfig)
            .filter(([severity]) => issueCounts[severity.toLowerCase()] > 0)
            .sort(([, configA], [, configB]) => configA.order - configB.order)
            .map(([severity, config]) => ({
                id: severity,
                label: config.displayName,
                count: issueCounts[severity.toLowerCase()],
                color: config.color,
                filter: () => scanData.issues?.filter(issue => issue.severity === severity) || []
            }))
    ];

    const handleTabChange = (tabId) => {
        setActiveTab(tabId);
        setCurrentPage(1); // Reset to first page when changing tabs
    };


    const handleSearchChange = (e) => {
        setSearchTerm(e.target.value);
        setCurrentPage(1); // Reset to first page when searching
    };

    const handleSortChange = (value) => {
        setSortOrder(value);
        setCurrentPage(1); // Reset to first page when changing sort order
    };

    return (
        <Box
            mb={8}
            borderWidth={1}
            borderRadius="lg"
            overflow="hidden"
        >
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
                            onClick={() => setFilterOpen(!filterOpen)}
                            aria-label="Toggle filters"
                            aria-expanded={filterOpen}
                            variant="subtle"
                        >
                            {filterOpen ? <FaChevronUp /> : <FaChevronDown />}
                        </IconButton>
                    </Tooltip>
                </HStack>
            </Flex>

            <Collapsible.Root
                open={filterOpen}
                onOpenChange={setFilterOpen}

            >
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
                                endElement={<IoIosSearch />}
                            >
                                <Input
                                    placeholder="Search issues..."
                                    value={searchTerm}
                                    onChange={handleSearchChange}
                                    aria-label="Search issues..."
                                    color="blackAlpha.800"
                                />
                            </InputGroup>

                            <Select.Root
                                collection={orderingOptions}
                                value={sortOrder}
                                onValueChange={(e) => handleSortChange(e.value)}
                                maxW={{ base: "100%", md: "200px" }}
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
                                                <Select.Item
                                                    item={order}
                                                    key={order.value}
                                                >
                                                    {order.label}
                                                    <Select.ItemIndicator />
                                                </Select.Item>
                                            ))}
                                        </Select.Content>
                                    </Select.Positioner>
                                </Portal>
                            </Select.Root>
                        </Flex>

                        {/* Tabs moved to a second row, just below filter controls */}
                        <Tabs.Root
                            variant="enclosed"
                            lazyMount
                            unmountOnExit
                            value={activeTab}
                            onValueChange={(e) => handleTabChange(e.value)}
                            defaultValue="all"
                            mt={4}
                        >
                            <Tabs.List overflowX="auto" whiteSpace="nowrap">
                                {tabsConfig.map((tab) => (
                                    <Tabs.Trigger key={tab.id} value={tab.id}>
                                        {tab.label}{" "}
                                        <Badge ml={2} colorScheme={tab.color}>
                                            {tab.count}
                                        </Badge>
                                    </Tabs.Trigger>
                                ))}
                            </Tabs.List>
                            <Tabs.Indicator rounded="lg" />
                            {tabsConfig.map((tab) => (
                                <Tabs.Content key={tab.id} value={tab.id} p={4}>
                                    {renderIssueList(tab.filter())}
                                </Tabs.Content>
                            ))}
                        </Tabs.Root>
                    </Box>
                </Collapsible.Content>
            </Collapsible.Root>
        </Box>
    );
};
