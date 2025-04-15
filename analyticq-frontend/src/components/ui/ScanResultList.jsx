import React, { useState, useEffect, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import { getScansByRepoName } from "services/contextService";
import LoadingSpinner from "./LoadingSpinner";
import {
    Box,
    Text,
    HStack,
    Table,
    Badge,
    Card,
    Heading,
    Select,
    Portal,
    createListCollection,
    Flex
} from "@chakra-ui/react"
import { Tooltip } from "./tooltip";
import { formatDate } from "components/utils/time";
import PaginationControls from "./PaginationControls";

/**
 * A component that displays a list of scan results for a given context.
 *
 * @component
 * @param {Object} props - The component props
 * @param {string} props.contextId - The ID of the context for which to display scan results
 *
 * @returns {JSX.Element} A table displaying scan results, or loading/error/empty states
 *
 * The component features:
 * - Fetches and displays scan results sorted by creation date (newest first)
 * - Shows loading spinner while fetching data
 * - Displays error message if fetch fails
 * - Shows empty state message if no scans exist
 * - Renders a table with scan details including:
 *   - Scan ID
 *   - Creation date
 *   - Tool name
 *   - Issue severity counts (Critical, High, Medium, Low) as badges
 * - Clickable rows that navigate to detailed scan view
 */
export const ScanResultList = ({ repoName }) => {
    const [scansData, setScanData] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const navigate = useNavigate();

    const [currentPage, setCurrentPage] = useState(1);
    const [pageSize, setPageSize] = useState([5]);

    const currentItemPerPageList = createListCollection({
        items: [
            { label: "5 per page", value: '5' },
            { label: "10 per page", value: '10' },
            { label: "20 per page", value: "20" }
        ]
    });

    const fetchScansByRepoName = useCallback(async () => {
        try {
            setLoading(true);
            const scans = await getScansByRepoName(repoName);
            const sortedScans = scans.sort((a, b) =>
                new Date(b.created_at) - new Date(a.created_at)
            );
            setScanData(sortedScans);
            setError(null)
        }
        catch (err) {
            console.error("Error fetching scans:", err);
            setError("Failed to load scan results. Please try again later.");
        }
        finally {
            setLoading(false);
        }
    }, [repoName]);

    useEffect(() => {
        if (repoName) {
            fetchScansByRepoName(repoName)
        }
    }, [repoName, fetchScansByRepoName]);


    const handlePageChange = (page) => {
        setCurrentPage(page);
        console.log("Setting page:", page)
    };

    const handlePageSizeChange = (value) => {
        setPageSize(value);
        setCurrentPage(1);
    }


    const navigateToScanDetails = (contextId, scanId) => {
        navigate(`/contexts/${contextId}/scans/${scanId}`);
    }

    const getSeverityCount = (issues, severity) => {
        return issues.filter(issue => issue.severity === severity).length
    };

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
            <HStack
                borderSpacing={1}
            >
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
        )
    }

    const totalItems = scansData.length;
    const totalPages = Math.ceil(totalItems / pageSize[0]);
    const startIndex = (currentPage - 1) * pageSize[0];
    const endIndex = Math.min(startIndex + pageSize[0], totalItems);
    const currentPageData = scansData.slice(startIndex, endIndex);


    if (loading) {
        return <LoadingSpinner />
    }

    return (
        <Card.Root
            shadow="sm"
            borderRadius="lg"
            variant="elevated"
        >
            <Card.Header
                borderBottomWidth="1px"
                pb={3}>
                <Heading size="md">Scan Results: {repoName}</Heading>
            </Card.Header>
            <Card.Body>
                {error ? (
                    <Box p={6} borderWidth="1px" borderRadius="md" textAlign="center" bg="red.50">
                        <Text color="red.500">{error}</Text>
                    </Box>
                ) : scansData.length === 0 ? (
                    <Box
                        p={6}
                        borderWidth="1px"
                        borderRadius="md"
                        textAlign="center"
                    >
                        <Text>No scan results available for this context.</Text>
                    </Box>
                ) : (
                    <Box overflowX="auto">
                        <Table.Root
                            variant="line"
                            size="md"
                        >
                            <Table.Header>
                                <Table.Row>
                                    <Table.ColumnHeader>Scan ID</Table.ColumnHeader>
                                    <Table.ColumnHeader>Created At</Table.ColumnHeader>
                                    <Table.ColumnHeader>Tool name</Table.ColumnHeader>
                                    <Table.ColumnHeader>Issues</Table.ColumnHeader>
                                </Table.Row>
                            </Table.Header>
                            <Table.Body>
                                {currentPageData.map((scan) => (
                                    <Table.Row
                                        key={scan.id}
                                        _hover={{ bg: "blackAlpha.200" }}
                                        onClick={() => navigateToScanDetails(scan.context_id, scan.id)}
                                        cursor="pointer"
                                        fontFamily="mono"
                                        transition="background-color 0.2s"
                                    >
                                        <Table.Cell>{scan.scan_id}</Table.Cell>
                                        <Table.Cell>{formatDate(scan.created_at)}</Table.Cell>
                                        <Table.Cell>{scan.tool_name}</Table.Cell>
                                        <Table.Cell>{renderSeverityBadges(scan.issues)}</Table.Cell>
                                    </Table.Row>
                                ))}
                            </Table.Body>
                        </Table.Root>
                    </Box>
                )}
            </Card.Body>
            {totalPages > 1 && (
                <Card.Footer
                    justifyContent="center"
                    borderTopWidth="1px"
                    pt={4}
                    pb={4}
                >
                    <Flex
                        justifyContent="space-between"
                        alignItems="center"
                        width="100%"
                    >
                        <Flex alignItems="center">
                            <Select.Root
                                size="sm"
                                ml={1}
                                value={pageSize}
                                onValueChange={(e) => handlePageSizeChange(e.value)}
                                collection={currentItemPerPageList}
                                variant="subtle"
                                width="auto"
                            >
                                <Select.HiddenSelect />
                                <Select.Label>Rows Per Page</Select.Label>
                                <Select.Control>
                                    <Select.Trigger>
                                        <Select.ValueText placeholder="Select rows per page" />
                                    </Select.Trigger>
                                    <Select.IndicatorGroup>
                                        <Select.Indicator />
                                    </Select.IndicatorGroup>
                                </Select.Control>
                                <Portal>
                                    <Select.Positioner>
                                        <Select.Content>
                                            {currentItemPerPageList.items.map((itemPerPage) => (
                                                <Select.Item item={itemPerPage} key={itemPerPage.value}>
                                                    {itemPerPage.label}
                                                    <Select.ItemIndicator />
                                                </Select.Item>
                                            ))}
                                        </Select.Content>
                                    </Select.Positioner>
                                </Portal>
                            </Select.Root>
                        </Flex>


                        <PaginationControls
                            total={totalItems}
                            pageSize={pageSize[0]}
                            currentPage={currentPage}
                            onPageChange={handlePageChange}
                        />
                    </Flex>

                </Card.Footer>
            )}
        </Card.Root >
    )

}
