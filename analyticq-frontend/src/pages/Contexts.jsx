import React, { useState, useEffect } from "react";
import {
    Box,
    Heading,
    Stack,
    Text
} from "@chakra-ui/react";
import { useDispatch, useSelector } from 'react-redux';
import { useNavigate } from "react-router-dom";
import { searchByRepoNamePrefix } from "redux/searchSlice";
import { getAllContexts } from "services/contextService";
import LoadingSpinner from "components/ui/LoadingSpinner";
import ContextList from "components/ui/ContextList";
import EmptyState from "components/layout/EmptyState";
import BackButton from "components/ui/BackButton";
import ErrorDisplay from "components/layout/ErrorDisplay";
import PaginationControls from "components/ui/PaginationControls";
import { updatePageMetadata } from "components/utils/metadata";
import { ImageOff } from "lucide-react";


/**
 * Renders the Contexts page component that displays a list of repository contexts.
 *
 * @component
 * @description
 * This component handles the display of repository contexts with the following features:
 * - Fetches and displays repository contexts with pagination
 * - Implements search functionality for filtering contexts by repository name
 * - Shows loading states and error messages
 * - Displays an empty state when no contexts are available
 * - Provides pagination controls for navigating through multiple pages of contexts
 *
 * @returns {JSX.Element} A component that renders either:
 *  - Loading spinner while fetching data
 *  - Error alert if there's an error
 *  - Empty state if no contexts exist
 *  - List of contexts with pagination controls
 *  - No results message for unsuccessful searches
 */
export const ContextsPage = () => {

    const PAGE_SIZE_DEFAULT = 10;
    const dispatch = useDispatch();
    const { searchResults, loading, error, searchQuery } = useSelector((state) => state.search);
    const [contextsData, setContextsData] = useState({
        items: [],
        total: 0,
        page: 1,
        page_size: PAGE_SIZE_DEFAULT,
        has_more: false
    });
    const navigate = useNavigate();

    useEffect(() => {
        updatePageMetadata(
            "Codebase Homepage",
            "All contexts analyzed",
            "/contexts"
        )
    });

    // Fetch contexts function
    const fetchContexts = async (page = 1, pageSize = PAGE_SIZE_DEFAULT) => {
        try {
            const data = await getAllContexts({ page, pageSize });
            setContextsData(data);
        } catch (error) {
            console.error("Error fetching contexts:", error);
        }
    };

    // Effect to fetch initial data
    useEffect(() => {
        fetchContexts();
    }, []);

    // Effect to handle search query change
    useEffect(() => {
        if (searchQuery.length > 3) {
            dispatch(searchByRepoNamePrefix(searchQuery)); // Fetch filtered contexts by prefix
        }
    }, [searchQuery, dispatch]);

    // Handle pagination change
    const handlePageChange = (newPage) => {
        fetchContexts(newPage, contextsData.page_size);
    };


    // If no contexts and not loading, show empty state
    if (!loading && contextsData.total === 0 && !error) {
        return (
            <EmptyState
                title="Repository Contexts"
                message="There are currently no repository contexts in the system.
                Please add a repository to get started."
            />
        );
    }

    const filteredContexts = searchQuery && searchQuery.length > 3 && searchResults.length > 0
        ? searchResults
        : contextsData.items;

    const isEmptySearchResult = searchQuery && searchQuery.length > 3 && searchResults.length === 0 && !loading;

    return (
        <Box p={6}>
            <Heading
                size="lg"
                mb={4}
                textAlign="center"
                color="blackAlpha.800"
                aria-label="Contexts page heading"
            >
                Codebase Analyzed
            </Heading>
            {error && (
                <ErrorDisplay
                    title="Contexts"
                    error={error}
                    backButton={<BackButton onClick={() => navigate("")} label="Back to Home" />}
               />
            )}
            {loading ? (
                <LoadingSpinner />
            ) : (
                <Stack width="full" gap="5">
                    {filteredContexts.length > 0 ? (
                        <>
                            <ContextList contexts={filteredContexts} />
                            {(!searchQuery || searchQuery.length <= 3) && (
                                <PaginationControls
                                    total={contextsData.total}
                                    pageSize={contextsData.page_size}
                                    currentPage={contextsData.page}
                                    onPageChange={handlePageChange}
                                />
                            )}
                        </>
                    ) : (
                        <Box mt={6} p={6} borderWidth="1px" borderRadius="lg">
                            <Text fontSize="lg" textAlign="center" color="gray.600">
                                No codebase found
                            </Text>
                            <Text fontSize="md" color="gray.500">
                                {isEmptySearchResult
                                    ? `No codebase match "${searchQuery}". Try a different search term.`
                                    : "No codebase available."}
                            </Text>
                        </Box>
                    )}
                </Stack>
            )}
        </Box>
    );
};

export default ContextsPage;
