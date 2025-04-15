import React, { useState, useEffect, useCallback, useRef } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { toaster } from "components/ui/toaster";
import { getContextById, deleteContext } from "services/contextService";
import {
    Box,
    Flex,
    Heading,
    Spacer,
    Button,
    HStack
} from "@chakra-ui/react";
import LoadingSpinner from "components/ui/LoadingSpinner";
import ErrorDisplay from "components/layout/ErrorDisplay";
import RepositoryInfoCard from "components/ui/RepositoryInfoCard";
import BackButton from "components/ui/BackButton";
import DeleteConfirmationDialog from "components/ui/DeleteConfirmationDialog";
import { ChartNoAxesColumnIncreasing } from "lucide-react";
import { capitalizeFirstLetter } from "components/utils/strings";
import { updatePageMetadata } from "components/utils/metadata";
import { ScanResultList } from "components/ui/ScanResultList";

export const ContextDetailPage = ({ initialContextData = null }) => {
    const [contextData, setContextData] = useState(initialContextData);
    const [loading, setLoading] = useState(!initialContextData)
    const [error, setError] = useState(null);
    const [deleteLoading, setDeleteLoading] = useState(false);
    const [isOpenModal, setIsOpenModal] = useState(false);
    const { contextId } = useParams();
    const navigate = useNavigate();
    const cancelRef = useRef();


    // Update metadata when product data changes
    useEffect(() => {
        // Set initial loading metadata
        updatePageMetadata(
            'Context loading...',
            'Loading context information...',
            `/contexts/${contextId}`
        );

        // Update with product data once loaded
        if (contextData) {
            updatePageMetadata(
                `${capitalizeFirstLetter(contextData.repo_name)} - Overview`,
                 contextData.repo_name,
                `/contexts/${contextId}`
            );
        }
    }, [contextData, contextId]);

    const fetchContextDetails = useCallback(async (id) => {

        try {
            setLoading(true);
            const data = await getContextById(id);
            console.log("Getting context details: ", data);
            setContextData(data);
            setError(null);
        }
        catch {
            console.error("Error fetching context details:", error);
            setError("Failed to load context details. Please try again later.");
        }
        finally {
            setLoading(false);
        }
    }, [error]);

    const handleDeleteConfirm = async () => {
        try {
            setDeleteLoading(true);
            await deleteContext(contextId);

            toaster.success({
                title: "Update successful",
                description: "File saved successfully to the server",
            })

            navigate("/");
        }
        catch (err) {
            console.error("Error deleting context:", err);
        }
        finally {
            setDeleteLoading(false);
        }
    }

    useEffect(() => {
        if (!initialContextData || initialContextData.id !== parseInt(contextId)) {
            fetchContextDetails(contextId);
        }
    }, [contextId, initialContextData, fetchContextDetails]);

    const handleBackClick = () => {
        navigate(-1);
    }

    // New function to navigate to the stats page
    const navigateToStats = () => {
        navigate(`/contexts/${contextId}/stats?repo=${encodeURIComponent(contextData.repo_name)}`);
    };



    if (loading) {
        return (
            <LoadingSpinner />
        )
    }

    if (error) {
        return (
            <ErrorDisplay
                title="Context Details"
                error={error}
                backButton={
                    <BackButton onClick={handleBackClick} label="Back to Contexts" />
                }
            />
        );
    }

    return (
        <Box p={6} mx="auto" maxWidth="1200px">
            <Flex justify="space-between" align="center" mb={6}>
                <Heading
                    size="lg"
                    textAlign="center"
                    color="blackAlpha.800"
                    flex="1"
                >
                    Codebase {contextData.id} Details
                </Heading>
            </Flex>

            <RepositoryInfoCard contextData={contextData} />


            <ScanResultList
                repoName={contextData.repo_name}
            />

            <Flex
                mt={10}
                justifyContent="space-between"
                gap={4}
                flexWrap="wrap"
                alignItems="center"
            >

                <BackButton onClick={handleBackClick} label="Back to Contexts" />

                <Spacer />

                <HStack>
                    <Button
                        onClick={navigateToStats}
                        bg="blackAlpha.900"
                        color="whiteAlpha.900"
                        variant="solid"
                        size="sm"
                    >
                        <ChartNoAxesColumnIncreasing size={18} />
                        View Statistics
                    </Button>

                    <DeleteConfirmationDialog
                        isOpenModal={isOpenModal}
                        setIsOpenModal={setIsOpenModal}
                        repoName={contextData.repo_name}
                        isLoading={deleteLoading}
                        onConfirm={handleDeleteConfirm}
                        cancelRef={cancelRef}
                    />
                </HStack>
            </Flex>
        </Box>
    )
};

export default ContextDetailPage;
