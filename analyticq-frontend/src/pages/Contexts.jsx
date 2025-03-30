import React, { useState, useEffect } from "react";
import {
    Table,
    TableContainer,
    Button,
    Spinner,
    Box,
    Heading,
    Flex,
    Alert,
    Alert
} from "@chakra-ui/react";
import { getAllContexts } from "services/contextService";


export const ContextsPage = () => {
    const [contextsData, setContextsData] = useState({
        items: [],
        total: 0,
        page: 1,
        page_size: 5,
        has_more: false
    });
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    const fetchContexts = async (page = 1, pageSize = 5) => {
        try {
            setLoading(true);
            const data = await getAllContexts({ page, pageSize });
            setContextsData(data);
            setError(null);
        } catch (error) {
            console.error("Error fetching contexts:", error);
            setError("Failed to load contexts. Please try again later.");
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchContexts();
    }, []);

    const handlePrevPage = async () => {
        if(contextsData.page > 1){
            await fetchContexts(contextsData.page - 1, contextsData.page_size);
        }
    };

    const handleNextPage = async () => {
        if(contextsData.has_more) {
            await fetchContexts(contextsData.page + 1, contextsData.page_size)
        }
    }

    if(!loading && contextsData.total === 0 && !error){
        return (
            <Box  p={6}>
                <Heading size="lg" mb={4}>Repository Contexts</Heading>
                <Alert.Root>
                    <Alert.Title mt={4} mb={1} fontSize="lg">
                        No Repository Contexts Found
                    </Alert.Title>
                    <Alert.Description maxWidth="md">
                        There are currently no repository contexts in the system.
                        Please add a repository to get started.
                    </Alert.Description>
                </Alert.Root>
            </Box>

        );
    }

    return (
        <>
        </>
    )
};

export default ContextsPage;
