import React, { useState, useEffect, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import { getScansByRepoName } from "services/contextService";
import LoadingSpinner from "../general/LoadingSpinner";
import {
  Box,
  Text,
  HStack,
  Badge,
  Card,
  Heading,
  Select,
  Portal,
  createListCollection,
  Flex,
} from "@chakra-ui/react";
import { Tooltip } from "../general/Tooltip";
import { formatDate } from "components/utils/time";
import { PaginationFooter } from "../general/PaginationFooter";
import {
  calculatePagination,
  DEFAULT_PAGE_SIZE_OPTIONS,
} from "components/utils/pagination";
import { DataTable } from "../general/DataTable";

export const ScanResultList = ({ repoName }) => {
  const [scansData, setScanData] = useState([]);
  const [filters, setFilters] = useState({ toolName: ["all"] });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize, setPageSize] = useState(["5"]);

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

  const renderSeverityBadges = (issues) => {
    const severities = [
      { label: "Critical", color: "red", level: "CRITICAL" },
      { label: "High", color: "orange", level: "HIGH" },
      { label: "Medium", color: "yellow", level: "MEDIUM" },
      { label: "Low", color: "green", level: "LOW" },
      { label: "Info", color: "blue", level: "INFO" },
      { label: "Unknown", color: "blue", level: "UNKNOWN" },
    ];

    return (
      <HStack spacing={1}>
        {severities.map(({ label, color, level }) => {
          const count = getSeverityCount(issues, level);
          return count > 0 ? (
            <Tooltip key={level} content={`${count} ${label} issues`}>
              <Badge
                colorPalette={color}
                borderRadius="full"
                px={2}
                py={0.5}
                fontSize="xs"
                fontWeight="medium"
              >
                {label}: {count}
              </Badge>
            </Tooltip>
          ) : null;
        })}
      </HStack>
    );
  };

  const filteredData =
    filters.toolName[0] === "all"
      ? scansData
      : scansData.filter((scan) => scan.tool_name === filters.toolName[0]);

  const { currentPageData, totalPages } = calculatePagination(
    filteredData,
    currentPage,
    pageSize[0],
  );

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

  if (loading) return <LoadingSpinner />;

  return (
    <Card.Root shadow="sm" borderRadius="lg" variant="elevated">
      <Card.Header borderBottomWidth="1px" pb={3}>
        <Flex
          mt={4}
          gap={3}
          wrap="wrap"
          direction={{ base: "column", md: "row" }}
          align={{ base: "flex-start", md: "center" }}
        >
          <Heading size="md">Scan Results: {repoName}</Heading>
          <Box w={{ base: "100%", md: "30%" }} ml={{ base: 0, md: "auto" }}>
            <Select.Root
              size="sm"
              placeholder="Filter by tool name"
              collection={toolNameCollection}
              defaultValue={["all"]}
              value={filters.toolName}
              onValueChange={(e) =>
                setFilters({ ...filters, toolName: e.value })
              }
              width="auto"
            >
              <Select.HiddenSelect />
              <Select.Control>
                <Select.Trigger>
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
        </Flex>
      </Card.Header>

      <Card.Body>
        {error ? (
          <Box
            p={6}
            borderWidth="1px"
            borderRadius="md"
            textAlign="center"
            bg="red.50"
          >
            <Text color="red.500">{error}</Text>
          </Box>
        ) : scansData.length === 0 ? (
          <Box p={6} borderWidth="1px" borderRadius="md" textAlign="center">
            <Text>No scan results available for this context.</Text>
          </Box>
        ) : (
          <Box overflowX="auto">
            <DataTable
              ariaLabel="Scan results"
              data={currentPageData}
              rowKey={(row) => row.id}
              onRowClick={(row) =>
                navigate(`/contexts/${row.context_id}/scans/${row.id}`)
              }
              emptyText="No scan results available for this context."
              columns={[
                { header: "Scan ID", accessor: "scan_id" },
                {
                  header: "Created At",
                  accessor: "created_at",
                  render: (row) => formatDate(row.created_at),
                },
                { header: "Tool name", accessor: "tool_name" },
                {
                  header: "Issues",
                  accessor: "issues",
                  render: (row) => renderSeverityBadges(row.issues),
                },
              ]}
            />
          </Box>
        )}
      </Card.Body>

      {totalPages > 1 && (
        <Card.Footer borderTopWidth="1px" pt={4} pb={4}>
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
