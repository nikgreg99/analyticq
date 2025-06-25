import React, {
  useState,
  useEffect,
  useCallback,
  useMemo,
  useRef,
} from "react";
import { useNavigate } from "react-router-dom";
import {
  Container,
  Flex,
  Heading,
  Text,
  SimpleGrid,
  Stack,
  InputGroup,
  Input,
  Portal,
  Spinner,
  Box,
  Button,
  Badge,
  CloseButton,
  Select
} from "@chakra-ui/react";
import { Tooltip } from "components/ui/general/Tooltip";
import { Toaster, toaster } from "components/ui/general/Toaster";
import { HiX } from "react-icons/hi";
import { MdCompareArrows, MdClear } from "react-icons/md";
import LoadingSpinner from "components/ui/general/LoadingSpinner";
import ErrorDisplay from "components/layout/ErrorDisplay";
import BackButton from "components/ui/general/BackButton";
import { LanguageToolTile } from "components/ui/tool/LanguageToolTile";
import { updatePageMetadata } from "components/utils/metadata";
import { useToolExplorer } from "hooks/useToolsExplorer";
import { useToolComparisonData } from "hooks/useToolComparison";
import useToolOptions from "hooks/useToolOptions";
import { useLanguageFilter } from "hooks/useLanguageFilter";
import LanguageToolComparisonDialog from "components/ui/tool/LanguageToolComparisonDialog";

/**
 * A page component for exploring and comparing SAST (Static Application Security Testing) tools and programming languages.
 *
 * @component
 * @param {Object} props - Component props
 * @param {Array|null} props.initialLanguagesData - Optional initial data for languages and their associated tools
 *
 * @returns {JSX.Element} A responsive page layout with search, filter, and comparison capabilities
 */
export const ToolsPage = ({ initialLanguagesData = null }) => {
  const { languages, loading, error } = useToolExplorer(initialLanguagesData);
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedTool, setSelectedTool] = useState(["all"]);
  const [selectedLanguages, setSelectedLanguages] = useState([]);
  const [comparisonDialogOpened, setComparisonDialogOpened] = useState(false);
  const searchInputRef = useRef(null);
  const cancelRef = useRef(null);
  const navigate = useNavigate();

  // Selected languages lookup map for O(1) checking if a language is selected
  const selectedLanguagesMap = useMemo(() => {
    const map = new Map();
    selectedLanguages.forEach(lang => map.set(lang.name, true));
    return map;
  }, [selectedLanguages]);

  // Page metadata effect
  useEffect(() => {
    updatePageMetadata(
      "Tool Explorer",
      "Discover programming languages and their associated SAST tools",
      "/tools",
    );
  }, []);

  // Keyboard shortcuts effect
  useEffect(() => {
    const handleKeyDown = (e) => {
      if ((e.ctrlKey || e.metaKey) && e.key === "/") {
        e.preventDefault();
        searchInputRef.current?.focus();
      }
    };

    document.addEventListener("keydown", handleKeyDown);
    return () => document.removeEventListener("keydown", handleKeyDown);
  }, []);

  // Memoized navigation callback
  const handleClickBack = useCallback(() => navigate(-1), [navigate]);

  // Tool options for dropdown
  const toolOptions = useToolOptions(languages);

  // Filtered languages based on search and tool selection
  const filteredLanguages = useLanguageFilter(
    languages,
    searchTerm,
    selectedTool
  );

  // Language selection toggle with optimization
  const toggleLanguageSelection = useCallback((language) => {
    setSelectedLanguages(prev => {
      const exists = prev.some(l => l.name === language.name);
      return exists
        ? prev.filter(l => l.name !== language.name)
        : [...prev, language];
    });
  }, []);

  // Clear selections with toast notification
  const clearAllSelections = useCallback(() => {
    setSelectedLanguages([]);
    toaster.create({
      title: "Selections cleared",
      type: "info",
      duration: 2000,
      closable: true,
    });
  }, []);

  // Optimized language selection check using the map
  const isLanguageSelected = useCallback(
    (languageName) => selectedLanguagesMap.has(languageName),
    [selectedLanguagesMap]
  );

  // Memoized comparison data - handle different data formats
  const languagesForComparison = useMemo(() => {
    if (selectedLanguages.length > 0) {
      return selectedLanguages;
    }
    // If no languages selected, use all languages
    // Make sure they have the same format as selectedLanguages
    return languages || [];
  }, [selectedLanguages, languages]);

  const toolComparisonData = useToolComparisonData(languagesForComparison);

  if (loading) return <LoadingSpinner />;
  if (error)
    return (
      <ErrorDisplay
        title="Tool Explorer"
        error={error}
        backButton={
          <BackButton onClick={handleClickBack} label="Back to Contexts" />
        }
      />
    );

  return (
    <Container maxW="full" py={8} px={{ base: 4, md: 8 }}>
      <Flex direction="column" align="center" mb={10}>
        <Heading mb={4} size="2xl" color="blackAlpha.800">
          SAST Tools Explorer
        </Heading>
        <Text fontSize="lg" textAlign="center" color="blackAlpha.700">
          Discover programming languages and their associated SAST tools
        </Text>
      </Flex>

      <Stack
        direction={{ base: "column", md: "row" }}
        spacing={4}
        mb={8}
        maxW="800px"
        mx="auto"
        w="100%"
      >
        <InputGroup size="lg" flex={1}>
          <Input
            ref={searchInputRef}
            placeholder="Search language... (Ctrl + /)"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            borderRadius="lg"
            pr="4.5rem"
            color="blackAlpha.800"
            aria-label="Search for a programming language"
          />
        </InputGroup>

        <InputGroup flex={1} maxW={{ base: "full", md: "250px" }}>
          <Select.Root
            value={selectedTool}
            onValueChange={(e) => setSelectedTool(e.value)}
            defaultValue={["all"]}
            collection={toolOptions}
            borderRadius="lg"
            aria-label="Filter tools"
          >
            <Select.HiddenSelect />
            <Select.Control>
              <Select.Trigger>
                <Select.ValueText
                  placeholder="Select tool..."
                  color="blackAlpha.800"
                />
              </Select.Trigger>
              <Select.IndicatorGroup>
                {loading && <Spinner />}
                <Select.ClearTrigger />
                <Select.Indicator />
              </Select.IndicatorGroup>
            </Select.Control>
            <Portal>
              <Select.Positioner>
                <Select.Content>
                  {toolOptions.items.map((tool) => (
                    <Select.Item key={tool.value} item={tool}>
                      {tool.label}
                      <Select.ItemIndicator />
                    </Select.Item>
                  ))}
                </Select.Content>
              </Select.Positioner>
            </Portal>
          </Select.Root>
        </InputGroup>
      </Stack>

      <Flex justify="space-between" align="center" mb={6}>
        <Text color="blackAlpha.800" fontWeight="medium">
          {selectedLanguages.length > 0
            ? `${selectedLanguages.length} language${selectedLanguages.length !== 1 ? "s" : ""} selected`
            : "Select languages to compare tools or compare all"}
        </Text>
        <Button
          colorPalette="blue"
          onClick={() => setComparisonDialogOpened(true)}
          size="md"
        >
          <MdCompareArrows />
          {selectedLanguages.length === 0
            ? "Compare All"
            : `Compare (${selectedLanguages.length})`
          }
        </Button>
      </Flex>

      {selectedLanguages.length > 0 && (
        <Flex
          wrap="wrap"
          gap={2}
          mb={6}
          p={3}
          bg="blue.50"
          borderRadius="md"
          border="1px solid"
          borderColor="blue.100"
          align="center"
        >
          <Text fontSize="sm" color="blue.700" mr={2}>
            Selected:
          </Text>
          {selectedLanguages.map((lang) => (
            <Tooltip key={lang.name} content="Click to remove" showArrow>
              <Badge
                px={3}
                py={1}
                borderRadius="full"
                bg="blue.100"
                color="blue.800"
                border="1px solid"
                borderColor="blue.200"
                cursor="pointer"
                display="flex"
                alignItems="center"
                gap={1}
                _hover={{ bg: "blue.200" }}
                onClick={() => toggleLanguageSelection(lang)}
                transition="all 0.2s"
              >
                {lang.name}
                <CloseButton
                  size="sm"
                  bg="transparent"
                  variant="solid"
                  color="black"
                  aria-label={`Cancel language ${lang.name} selected`}
                >
                  <HiX />
                </CloseButton>
              </Badge>
            </Tooltip>
          ))}
          <Button
            size="xs"
            variant="sutle"
            colorScheme="blue"
            color="blackAlpha.800"
            ml="auto"
            onClick={clearAllSelections}
            aria-label="Clear all selected"
          >
            Clear All
            <MdClear size={14} color="black" />
          </Button>
        </Flex>
      )}

      {filteredLanguages.length === 0 ? (
        <Flex
          minHeight="300px"
          direction="column"
          justify="center"
          align="center"
          p={8}
        >
          <Heading size="md" color="blackAlpha.800" mb={3}>
            No Languages found
          </Heading>
          <Text color="crimson" fontSize="xs">
            Try adjusting your search or filters
          </Text>
        </Flex>
      ) : (
        <Box>
          <SimpleGrid columns={{ base: 1, sm: 2, lg: 3 }} spacing={6}>
            {filteredLanguages.map((language) => (
              <Box
                key={language.name}
                position="relative"
                cursor="pointer"
                onClick={() => toggleLanguageSelection(language)}
                borderRadius="lg"
                border="2px solid"
                borderColor={
                  isLanguageSelected(language.name) ? "blue.500" : "transparent"
                }
                boxShadow={isLanguageSelected(language.name) ? "md" : "sm"}
                transform={
                  isLanguageSelected(language.name) ? "scale(1.02)" : "none"
                }
                transition="all 0.2s ease-in-out"
                _hover={{ transform: "translateY(-2px)", boxShadow: "lg" }}
                aria-selected={isLanguageSelected(language.name)}
                role="option"
              >
                {isLanguageSelected(language.name) && (
                  <Badge
                    position="absolute"
                    top="8px"
                    right="8px"
                    colorPalette="blue"
                    borderRadius="full"
                    fontSize="xs"
                    px={2}
                  >
                    Selected
                  </Badge>
                )}
                <LanguageToolTile language={language} />
              </Box>
            ))}
          </SimpleGrid>
          <Text mt={6} textAlign="center" color="gray.500">
            Showing {filteredLanguages.length} of {languages.length} languages
          </Text>
        </Box>
      )}

      <LanguageToolComparisonDialog
        isOpen={comparisonDialogOpened}
        setIsOpenModal={setComparisonDialogOpened}
        ref={cancelRef}
        selectedLanguages={languagesForComparison}
        comparisonData={toolComparisonData}
      />
      <Toaster />
    </Container>
  );
};

ToolsPage.displayName = "ToolsPage";
