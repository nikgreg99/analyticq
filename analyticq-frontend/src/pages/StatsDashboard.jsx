import React, { useState, useEffect, useCallback, useMemo } from "react";
import { useParams, useSearchParams, useNavigate } from "react-router-dom";
import { getStatsByContextId } from "services/contextService";
import {
    Box,
    Heading,
    SimpleGrid
} from "@chakra-ui/react"
import {
    FiFile,
    FiHardDrive,
    FiCode,
    FiFolder
} from 'react-icons/fi';
import { SummaryStatsCard } from "components/ui/SummaryStatsCard";
import { formatBytes } from "components/utils/files";
import { generateColorFromString } from "components/utils/colors";
import LoadingSpinner from "components/ui/LoadingSpinner";
import BackButton from "components/ui/BackButton";
import ErrorDisplay from "components/layout/ErrorDisplay";
import { FileSizeDistribution } from "components/ui/FileSizeDistribution";
import { LanguageStatsDistribution } from "components/ui/LanguageStatsDistribution";
import { LanguageStatsCard } from "components/ui/LanguageStatsCard";
import { ExclusionSummary } from "components/ui/ExclusionStatsSummary";
import { updatePageMetadata } from "components/utils/metadata";
import { capitalizeFirstLetter } from "components/utils/strings";


/**
 * A dashboard component that displays various statistics about a codebase.
 *
 * @component
 * @param {Object} props - Component props
 * @param {Object|null} props.initStatsData - Initial statistics data. If null, data will be fetched from API
 * @returns {JSX.Element} A dashboard displaying codebase statistics including:
 *  - Summary statistics (total files, size, languages, excluded files)
 *  - Language distribution charts
 *  - File size distribution
 *  - Detailed language cards
 *  - Exclusion summary
 *
 * @example
 * return (
 *   <StatsDashboard initStatsData={statsData} />
 * )
 *
 * @requires react-router-dom - For navigation and URL parameters
 * @requires chakra-ui - For UI components and styling
 * @requires react-icons/fi - For icon components
 */
export const StatsDashboard = ({ initStatsData = null }) => {

    const [statsData, setStatsData] = useState(initStatsData);
    const [searchParams] = useSearchParams();
    const [loading, setLoading] = useState(!initStatsData);
    const [error, setError] = useState(null);
    const { contextId } = useParams();
    const repoName = searchParams.get('repo');
    const navigate = useNavigate();


    // Update metadata when product data changes
    useEffect(() => {
        // Set initial loading metadata
        updatePageMetadata(
            'Context stats...',
            'Loading stats information...',
            `/contexts/${contextId}/stats`
        );

        // Update with product data once loaded
        if (statsData) {
            updatePageMetadata(
                `${capitalizeFirstLetter(repoName)} Stats`,
                repoName,
                `/contexts/${contextId}/stats`
            );
        }
    }, [statsData, repoName, contextId]);


    const colorMap = useMemo(() => {

        if (statsData?.language_statistics) {
            return {};
        }

        return Object.keys(statsData.language_statistics).reduce((acc, language, index, array) => {
            acc[language] = generateColorFromString(language, index, array.length);
            return acc;
        }, {});

    }, [statsData?.language_statistics]);


    const fetchStatsByContextsId = useCallback(async () => {
        try {
            setLoading(true);
            const data = await getStatsByContextId(contextId);
            console.log("Getting stats details: ", data);
            setStatsData(data);
            setError(null);
        } catch (error) {
            console.error("Error fetching stat details:", error);
            setError(`Failed to load context stats details related to context with id ${contextId}. Please try again later.`);
        }
        finally {
            setLoading(false);
        }
    }, [contextId]);

    const handleBackClick = () => {
        navigate(`/context/${contextId}`);
    }

    useEffect(() => {
        if (!initStatsData || initStatsData.context_id !== parseInt(contextId)) {
            fetchStatsByContextsId(contextId);
        }
    }, [contextId, initStatsData, fetchStatsByContextsId]);

    if (loading) {
        return <LoadingSpinner />
    }

    if (error) {
        return (
            <ErrorDisplay
                title=" Code Statistics Dashboard"
                error={error}
                backButton={
                    <BackButton onClick={handleBackClick} label="Back to Contexts" />
                }
            />
        );
    }

    return (
        <Box
            p={6}
            maxW="7xl"
            mx="auto"
            minH="100vh"
            role="main"
            aria-labelledby="stats-dashboard-title"
        >
            <Heading
                as="h1"
                id="stats-dashboard-title"
                size="xl"
                mb={8}
                textAlign="center"
                color="blackAlpha.800"
                aria-live="polite"
            >
                Codebase Statistics: {repoName}
            </Heading>
            <SimpleGrid
                columns={{ base: 1, md: 4 }}
                spacing={6}
                mb={8}
                color="blackAlpha.800"
                aria-live="polite"
                aria-labelledby="language-details-heading"
            >
                <SummaryStatsCard
                    title="Total files"
                    value={statsData.total_files_scanned ?? 0}
                    icon={FiFile}
                    colorScheme="blue"
                />
                <SummaryStatsCard
                    title="Total Size"
                    value={formatBytes(statsData.total_size_scanned) ?? 0}
                    icon={FiHardDrive}
                    colorScheme="green"
                />
                <SummaryStatsCard
                    title="Languages"
                    value={Object.keys(statsData?.language_statistics ?? {}).length}
                    icon={FiCode}
                    colorScheme="purple"
                />
                <SummaryStatsCard
                    title="Excluded Files"
                    value={statsData.excluded_files.count ?? 0}
                    icon={FiFolder}
                    colorScheme="red"
                />
            </SimpleGrid>

            {/* Language Distribution */}
            <SimpleGrid
                columns={{ base: 1, lg: 2 }}
                spacing={6}
                mb={8}
            >
                <LanguageStatsDistribution
                    languageStats={statsData.language_statistics}
                    colorMap={colorMap}
                />

                <FileSizeDistribution
                    languageStats={statsData.language_statistics}
                    colorMap={colorMap}
                />
            </SimpleGrid>

            <Heading
                as="h2"
                size="lg"
                mb={4}
                color="blackAlpha.800"
                textAlign="center"
                id="language-details-heading"
            >
                Language Details
            </Heading>
            <SimpleGrid
                columns={{ base: 1, md: 2, lg: 3 }}
                spacing={6}
                mb={8}
                aria-live="polite"
            >
                {Object.entries(statsData.language_statistics || {})
                    .sort((a, b) => b[1].file_count - a[1].file_count)
                    .map(([language, stats]) => (
                        <LanguageStatsCard
                            key={language}
                            language={language}
                            stats={stats}
                            colorScheme={colorMap[language]}
                        />

                    ))
                }
            </SimpleGrid>


            {/* Exclusion Summary */}
            <Heading textAlign="center" color="blackAlpha.800" id="exclusion-summary">
                Exclusion Summary
            </Heading>
            <ExclusionSummary
                excludedFiles={statsData.excluded_files}
                totalScanned={statsData.total_size_scanned}
                repoName={repoName}
            />
        </Box>
    )
};
