import React, { useState, useEffect, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import { getScansByRepoName } from "services/contextService";
import LoadingSpinner from "../general/LoadingSpinner";
import {
  Box,
  Text,
  HStack,
  VStack,
  Badge,
  Card,
  Heading,
  Select,
  Portal,
  createListCollection,
  Flex,
  Button,
  Input,
  InputGroup,
  Alert,
} from "@chakra-ui/react";
import { Tooltip } from "../general/Tooltip";
import { formatDate } from "components/utils/time";
import { PaginationFooter } from "../general/PaginationFooter";
import {
  calculatePagination,
  DEFAULT_PAGE_SIZE_OPTIONS,
} from "components/utils/pagination";
import { DataTable } from "../general/DataTable";
import { IoIosRefresh, IoIosStats, IoIosSearch } from "react-icons/io";
import { capitalizeFirstLetter } from "components/utils/strings";

export const ScanResultList = ({ repoName }) => {
  const [scansData, setScanData] = useState([]);
  const [filters, setFilters] = useState({
    toolName: ["all"],
    searchQuery: ""
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize, setPageSize] = useState(["10"]);

  const fetchScansByRepoName = useCallback(async () => {
    try {
      setLoading(true);
      const scans = await getScansByRepoName(repoName);
      const sortedScans = scans.sort(
        (a, b) => new Date(b.created_at) - new Date(a.created_at),
      );
      setScanData(sortedScans);
      setError(null);
    } catch (err) {
      console.error("Error fetching scans:", err);
      setError("Failed to load scan results. Please try again later.");
    } finally {
      setLoading(false);
    }
  }, [repoName]);

  useEffect(() => {
    if (repoName) {
      fetchScansByRepoName(repoName);
    }
  }, [repoName, fetchScansByRepoName]);

  const getSeverityCount = (issues, severity) =>
    issues.filter((issue) => issue.severity === severity).length;

  const getTotalIssuesCount = (issues) => issues.length;

  const renderSeverityBadges = (issues) => {
    const severities = [
      { label: "Critical", color: "red", level: "CRITICAL" },
      { label: "High", color: "orange", level: "HIGH" },
      { label: "Medium", color: "yellow", level: "MEDIUM" },
      { label: "Low", color: "green", level: "LOW" },
      { label: "Warning", color: "teal", level: "WARNING" },
      { label: "Info", color: "blue", level: "INFO" },
      { label: "Unknown", color: "blue", level: "UNKNOWN" },
    ];

    const totalIssues = getTotalIssuesCount(issues);

    if (totalIssues === 0) {
      return (
        <Badge
          colorPalette="green"
          borderRadius="full"
          px={3}
          py={1.5}
          fontSize="xs"
          fontWeight="bold"
          variant="solid"
          boxShadow="sm"
          _hover={{ transform: "scale(1.05)", boxShadow: "md" }}
          transition="all 0.2s ease"
        >
          ✓ Clean
        </Badge>
      );
    }

    // Show only non-zero severity counts in order of priority
    const visibleSeverities = severities.filter(({ level }) => getSeverityCount(issues, level) > 0);

    return (
      <HStack spacing={1.5} wrap="wrap" align="center">
        {visibleSeverities.map(({ label, color, level }) => {
          const count = getSeverityCount(issues, level);
          return (
            <Tooltip key={level} content={`${count} ${label} severity issues`}>
              <Badge
                colorPalette={color}
                borderRadius="md"
                px={2.5}
                py={1}
                fontSize="xs"
                fontWeight="bold"
                variant="solid"
                cursor="help"
                boxShadow="sm"
                border="1px solid"
                borderColor="whiteAlpha.300"
                _hover={{
                  transform: "scale(1.08)",
                  boxShadow: "md",
                  borderColor: "whiteAlpha.500"
                }}
                transition="all 0.2s ease"
                minW="fit-content"
              >
                {label}: {count}
              </Badge>
            </Tooltip>
          );
        })}

        {/* Total issues summary badge */}
        <Badge
          colorPalette="gray"
          borderRadius="md"
          px={2.5}
          py={1}
          fontSize="xs"
          fontWeight="medium"
          variant="outline"
          borderWidth="1px"
          ml={1}
        >
          Total: {totalIssues}
        </Badge>
      </HStack>
    );
  };

  const filteredData = scansData.filter((scan) => {
    const matchesTool = filters.toolName[0] === "all" || scan.tool_name === filters.toolName[0];
    const matchesSearch = !filters.searchQuery ||
      scan.scan_id.toLowerCase().includes(filters.searchQuery.toLowerCase()) ||
      scan.tool_name.toLowerCase().includes(filters.searchQuery.toLowerCase());

    return matchesTool && matchesSearch;
  });

  const { currentPageData, totalPages } = calculatePagination(
    filteredData,
    currentPage,
    parseInt(pageSize[0]),
  );

  // Calculate the range of items being displayed
  const startIndex = (currentPage - 1) * parseInt(pageSize[0]) + 1;
  const endIndex = Math.min(currentPage * parseInt(pageSize[0]), filteredData.length);

  const createToolNameCollection = (data) => {
    const unique = [...new Set(data.map((scan) => scan.tool_name))];
    return createListCollection({
      items: [
        { label: "All Tools", value: "all" },
        ...unique.map((tool) => ({ label: tool, value: tool })),
      ],
    });
  };

  const toolNameCollection = createToolNameCollection(scansData);

  const handleRefresh = () => {
    fetchScansByRepoName();
  };

  const handleSearchChange = (e) => {
    setFilters({ ...filters, searchQuery: e.target.value });
    setCurrentPage(1); // Reset to first page when searching
  };

  const clearFilters = () => {
    setFilters({ toolName: ["all"], searchQuery: "" });
    setCurrentPage(1);
  };

  if (loading) return <LoadingSpinner />;

  return (
    <Card.Root
      shadow="lg"
      borderRadius="xl"
      variant="elevated"
      bg="gray.600"
    >
      <Card.Header borderBottomWidth="1px" pb={4}  _dark={{ bg: "gray.500" }}>
        <VStack spacing={4} align="stretch">
          <Flex
            justify="space-between"
            align="center"
            wrap="wrap"
            gap={3}
          >
            <HStack spacing={3}>
              <IoIosStats/>
              <Heading size="md" color="gray.800" _dark={{ color: "white" }}>
                Scan Results
              </Heading>
              <Badge
                colorPalette="blue"
                variant="subtle"
                px={3}
                py={1}
                borderRadius="full"
                fontSize="sm"
              >
                {repoName}
              </Badge>
            </HStack>

            <HStack spacing={2}>
              <Text fontSize="sm" color="gray.600" _dark={{ color: "gray.300" }}>
                {filteredData.length > 0 ? (
                  <>
                    Showing {startIndex}-{endIndex} of {filteredData.length} scans
                    {scansData.length !== filteredData.length && (
                      <Text as="span" color="gray.500" _dark={{ color: "gray.400" }}>
                        {" "}(filtered from {scansData.length} total)
                      </Text>
                    )}
                  </>
                ) : (
                  `0 of ${scansData.length} scans`
                )}
              </Text>
              <Button
                size="sm"
                variant="subtle"
                onClick={handleRefresh}
              >

                <IoIosRefresh/>
                Refresh
              </Button>
            </HStack>
          </Flex>

          {/* Enhanced Filters */}
          <Flex
            gap={4}
            wrap="wrap"
            direction={{ base: "column", md: "row" }}
            align={{ base: "stretch", md: "center" }}
          >
            <Box flex="1" minW="200px">
              <InputGroup size="sm">
                <Input
                  placeholder="Search scans by ID or tool name..."
                  value={filters.searchQuery}
                  onChange={handleSearchChange}
                  bg="gray.600"
                  borderRadius="md"
                />
              </InputGroup>
            </Box>

            <Box minW="200px">
              <Select.Root
                size="sm"
                collection={toolNameCollection}
                value={filters.toolName}
                onValueChange={(e) =>
                  setFilters({ ...filters, toolName: e.value })
                }
              >
                <Select.HiddenSelect />
                <Select.Control>
                  <Select.Trigger bg="white" _dark={{ bg: "gray.600" }}>
                    <Select.ValueText placeholder="Filter by tool" />
                  </Select.Trigger>
                  <Select.IndicatorGroup>
                    <Select.Indicator />
                    <Select.ClearTrigger />
                  </Select.IndicatorGroup>
                </Select.Control>
                <Portal>
                  <Select.Positioner>
                    <Select.Content>
                      {toolNameCollection.items.map((tool) => (
                        <Select.Item item={tool} key={tool.value}>
                          {tool.label}
                          <Select.ItemIndicator />
                        </Select.Item>
                      ))}
                    </Select.Content>
                  </Select.Positioner>
                </Portal>
              </Select.Root>
            </Box>

            {(filters.searchQuery || filters.toolName[0] !== "all") && (
              <Button
                size="sm"
                variant="ghost"
                onClick={clearFilters}
                colorPalette="gray"
              >
                Clear Filters
              </Button>
            )}
          </Flex>
        </VStack>
      </Card.Header>

      <Card.Body p={0}>
        {error ? (
          <Box p={6}>
            <Alert.Root status="error" borderRadius="md">
              <Alert.Indicator />
              <Alert.Title>Error Loading Scans</Alert.Title>
              <Alert.Description>{error}</Alert.Description>
            </Alert.Root>
          </Box>
        ) : scansData.length === 0 ? (
          <Box p={8} textAlign="center">
            <VStack spacing={4}>
              <IoIosStats/>
              <Heading size="md" color="gray.600" _dark={{ color: "gray.300" }}>
                No Scan Results Found
              </Heading>
              <Text color="gray.500" _dark={{ color: "gray.400" }}>
                No scan results are available for this repository yet.
              </Text>
              <Button
                colorPalette="teal"
                variant="outline"
                onClick={handleRefresh}
              >
                <IoIosRefresh/>
                Check Again
              </Button>
            </VStack>
          </Box>
        ) : filteredData.length === 0 ? (
          <Box p={8} textAlign="center">
            <VStack spacing={4}>
              <IoIosSearch/>
              <Heading size="md" color="gray.600" _dark={{ color: "gray.300" }}>
                No Results Match Your Filters
              </Heading>
              <Text color="gray.500" _dark={{ color: "gray.400" }}>
                Try adjusting your search terms or filters.
              </Text>
              <Button
                colorPalette="blue"
                variant="outline"
                onClick={clearFilters}
              >
                Clear Filters
              </Button>
            </VStack>
          </Box>
        ) : (
          <Box>
            <DataTable
              ariaLabel="Scan results table"
              data={currentPageData}
              rowKey={(row) => row.id}
              onRowClick={(row) =>
                navigate(`/contexts/${row.context_id}/scans/${row.id}/?reponame=${repoName}`)
              }
              emptyText="No scan results available for this context."
              columns={[
                {
                  header: "Scan ID",
                  accessor: "scan_id",
                  render: (row) => (
                    <Text fontFamily="mono" fontSize="sm" fontWeight="medium">
                      {row.scan_id}
                    </Text>
                  )
                },
                {
                  header: "Created",
                  accessor: "created_at",
                  render: (row) => (
                    <VStack spacing={1} align="start">
                      <Text fontSize="sm" fontWeight="medium">
                        {formatDate(row.created_at)}
                      </Text>
                      <Text fontSize="xs" color="gray.500" _dark={{ color: "gray.400" }}>
                        {new Date(row.created_at).toLocaleTimeString()}
                      </Text>
                    </VStack>
                  ),
                },
                {
                  header: "Tool",
                  accessor: "tool_name",
                  render: (row) => (
                    <Badge
                      colorPalette="purple"
                      variant="subtle"
                      borderRadius="md"
                      px={3}
                      py={1.5}
                      fontSize="xs"
                      fontWeight="semibold"
                      boxShadow="sm"
                    >
                      {capitalizeFirstLetter(row.tool_name)}
                    </Badge>
                  )
                },
                {
                  header: "Security Issues",
                  accessor: "issues",
                  render: (row) => renderSeverityBadges(row.issues),
                },
              ]}
              _hover={{
                bg: "gray.50",
                _dark: { bg: "gray.700" },
                cursor: "pointer",
                transform: "translateY(-1px)",
                shadow: "md",
              }}
              transition="all 0.2s ease"
            />
          </Box>
        )}
      </Card.Body>

      {totalPages > 1 && (
        <Card.Footer
          borderTopWidth="1px"
          pt={4}
          pb={4}
          bg="gray.500"
        >
          <PaginationFooter
            totalItems={filteredData.length}
            pageSize={pageSize}
            setPageSize={setPageSize}
            currentPage={currentPage}
            setCurrentPage={setCurrentPage}
            pageSizeOptions={DEFAULT_PAGE_SIZE_OPTIONS}
            responsive={true}
          />
        </Card.Footer>
      )}
    </Card.Root>
  );
};

ScanResultList.displayName = "ScanResultList";
