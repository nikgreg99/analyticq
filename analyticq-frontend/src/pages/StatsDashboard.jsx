import React, { useEffect, useCallback, useMemo } from "react";
import { useParams, useSearchParams, useNavigate } from "react-router-dom";
import { Box, Heading, SimpleGrid } from "@chakra-ui/react";
import { FiFile, FiHardDrive, FiCode, FiFolder } from "react-icons/fi";
import { SummaryStatsCard } from "components/ui/stats/SummaryStatsCard";
import { formatBytes } from "components/utils/files";
import LoadingSpinner from "components/ui/general/LoadingSpinner";
import BackButton from "components/ui/general/BackButton";
import ErrorDisplay from "components/layout/ErrorDisplay";
import { FileSizeDistribution } from "components/ui/stats/FileSizeDistribution";
import { LanguageStatsDistribution } from "components/ui/stats/LanguageStatsDistribution";
import { LanguageStatsCard } from "components/ui/stats/LanguageStatsCard";
import { ExclusionSummary } from "../components/ui/stats/ExclusionStatsSummary";
import { updatePageMetadata } from "components/utils/metadata";
import { capitalizeFirstLetter } from "components/utils/strings";
import { useContextStats } from "hooks/useContextStats";
import { useSortedLanguages } from "hooks/useSortedLanguages";
import { useLanguageColorMap } from "hooks/useLanguageColorMap";

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
  const [searchParams] = useSearchParams();
  const { contextId } = useParams();
  const repoName = searchParams.get("repo");
  const navigate = useNavigate();

  const { statsData, loading, error } = useContextStats({
    contextId,
    initStatsData,
  });
  const colorMap = useLanguageColorMap(statsData?.language_statistics);
  const sortedLanguages = useSortedLanguages(statsData?.language_statistics);

  // Update metadata when product data changes
  useEffect(() => {
    // Set initial loading metadata
    updatePageMetadata(
      "Context stats...",
      "Loading stats information...",
      `/contexts/${contextId}/stats`,
    );

    // Update with product data once loaded
    if (statsData) {
      updatePageMetadata(
        `${capitalizeFirstLetter(repoName)} Stats`,
        repoName,
        `/contexts/${contextId}/stats`,
      );
    }
  }, [statsData, repoName, contextId]);

  const summaryCards = useMemo(
    () => [
      {
        title: "Total files",
        value: statsData?.total_files_scanned ?? 0,
        icon: FiFile,
        colorScheme: "blue",
        ariaDesc: "total-files-description",
      },
      {
        title: "Total Size",
        value: formatBytes(statsData?.total_size_scanned ?? 0),
        icon: FiHardDrive,
        colorScheme: "green",
        ariaDesc: "total-files-scanned",
      },
      {
        title: "Languages",
        value: Object.keys(statsData?.language_statistics ?? {}).length,
        icon: FiCode,
        colorScheme: "purple",
        ariaDesc: "languages-statistics-cards",
      },
      {
        title: "Excluded Files",
        value: statsData?.excluded_files?.count ?? 0,
        icon: FiFolder,
        colorScheme: "red",
        ariaDesc: "excluded-files-count",
      },
    ],
    [statsData],
  );

  const handleBackClick = useCallback(() => {
    navigate(`/context/${contextId}`);
  }, [navigate, contextId]);

  if (loading) {
    return <LoadingSpinner />;
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
        {summaryCards.map(({ title, value, icon, colorScheme, ariaDesc }) => (
          <SummaryStatsCard
            key={title}
            title={title}
            value={value}
            icon={icon}
            colorScheme={colorScheme}
            aria-describedby={ariaDesc}
          />
        ))}
      </SimpleGrid>
      <SimpleGrid
        columns={{ base: 1, lg: 2 }}
        spacing={6}
        mb={8}
        aria-live="polite"
      >
        <LanguageStatsDistribution
          languageStats={statsData?.language_statistics}
          colorMap={colorMap}
          aria-live="polite"
        />

        <FileSizeDistribution
          languageStats={statsData?.language_statistics}
          colorMap={colorMap}
          aria-live="polite"
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
        {sortedLanguages.map(([language, stats]) => (
          <LanguageStatsCard
            key={language}
            language={language}
            stats={stats}
            colorScheme={colorMap[language]}
          />
        ))}
      </SimpleGrid>

      {/* Exclusion Summary */}
      <Heading textAlign="center" color="blackAlpha.800" id="exclusion-summary">
        Exclusion Summary
      </Heading>
      <ExclusionSummary
        excludedFiles={statsData?.excluded_files}
        totalScanned={statsData?.total_size_scanned}
        repoName={repoName}
      />
    </Box>
  );
};

StatsDashboard.displayName = "StastDashboard";
