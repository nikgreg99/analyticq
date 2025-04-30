import React, { useState, useEffect, useCallback, useMemo } from "react";
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
    Select,
    Portal,
    Spinner,
    Box,
    createListCollection
} from "@chakra-ui/react";
import LoadingSpinner from "components/ui/LoadingSpinner";
import ErrorDisplay from "components/layout/ErrorDisplay";
import BackButton from "components/ui/BackButton";
import { IoIosSearch } from "react-icons/io";
import { LanguageToolTile } from "components/ui/LanguageToolTile";
import { updatePageMetadata } from "components/utils/metadata";
import { getAllTools } from "services/toolService";

/**
 * A component that displays a searchable and filterable grid of programming languages and their associated SAST tools.
 *
 * @component
 * @param {Object} props - Component props
 * @param {Array<Object>} [props.initialLanguagesData=null] - Initial data for languages and their tools
 *                                                            Each object contains:
 *                                                            - name: {string} The programming language name
 *                                                            - tools: {Array<string>} List of associated tool names
 *
 * @returns {JSX.Element} A page containing:
 *                        - Search input for filtering languages
 *                        - Dropdown to filter by specific tool
 *                        - Grid of language cards showing associated tools
 *                        - Loading spinner while fetching data
 *                        - Error message if data fetch fails
 *
 * @example
 * <ToolsPage initialLanguagesData={[
 *   {
 *     name: "JavaScript",
 *     tools: ["eslint", "jshint"]
 *   }
 * ]} />
 */
export const ToolsPage = ({ initialLanguagesData = null }) => {

    const [languages, setLanguages] = useState(initialLanguagesData);
    const [loading, setLoading] = useState(!initialLanguagesData);
    const [error, setError] = useState(null);
    const [searchTerm, setSearchTerm] = useState('');
    const [filterByTool, setFilterByTool] = useState(['all']);
    const navigate = useNavigate();

    useEffect(() => {
        updatePageMetadata(
            "Tool Explorer",
            'SAST Tool Explorer',
            '/tools'
        )
    }, []);

    const handleClickBack = () => {
        navigate(-1);
    }

    const capitalizeFirstLetter = (string) => {
        return string.charAt(0).toUpperCase() + string.slice(1);
    }

    const processToolsData = useCallback((data) => {
        const languages = {};

        // Iterate through each tool and add it to the corresponding languages
        Object.entries(data).forEach(([toolName, supportedLanguages]) => {
            supportedLanguages.forEach(lang => {
                const langLower = lang.toLowerCase();

                if (!languages[langLower]) {
                    languages[langLower] = {
                        name: capitalizeFirstLetter(lang),
                        tools: []
                    };
                }

                languages[langLower].tools.push(toolName);
            });
        });

        // Convert to array for easier rendering
        return Object.values(languages);
    }, []);


    const fetchAllTools = useCallback(async () => {
        try {
            setLoading(true);
            const data = await getAllTools();
            console.log("Fetching data: ", data);
            const processedLanguages = processToolsData(data);
            console.log("Processed data", processedLanguages);
            setLanguages(processedLanguages);
            setError(null);
        }
        catch (error) {
            setError('Failed to fetch tools languages. Please try again later.');
            console.error('Error fetching  tools languages:', error);
        }
        finally {
            setLoading(false);
        }
    }, [processToolsData]);

    useEffect(() => {
        if (!initialLanguagesData) {
            fetchAllTools();
        }
    }, [initialLanguagesData, fetchAllTools]);

    const toolOptions = useMemo(() => {
        if (!languages) return createListCollection({ items: [{ label: "All", value: "all" }] });

        const uniqueTools = Array.from(
            new Set(languages.flatMap(lang => lang.tools))
        ).sort()

        console.log("Unique tools", uniqueTools)


        return createListCollection({
            items: [
                { label: "All", value: "all" },
                ...uniqueTools.map(tool => ({
                    label: capitalizeFirstLetter(tool),
                    value: tool
                }))
            ]
        });

    }, [languages])


    // Memoized filtered languages based on search term and selected tool
    const filteredLanguages = useMemo(() => {
        if (!languages) return [];

        const filter = languages.filter(lang => {
            const matchesSearch = lang.name.toLowerCase().includes(searchTerm.toLowerCase());
            console.log("Filter applied", matchesSearch);
            console.log(filterByTool);

            if (filterByTool[0] === 'all') {
                return matchesSearch;
            } else {
                return matchesSearch && lang.tools.includes(filterByTool[0]);
            }
        });

        console.log("Applying filtering", filter);
        return filter;


    }, [languages, searchTerm, filterByTool]);


    if (loading) {
        return (<LoadingSpinner />
        );
    }

    if (error) {
        <ErrorDisplay
            title="Tool Explorer"
            error={error}
            backButton={
                <BackButton onClick={handleClickBack} label="Back to Contexts" />
            }
        />
    }

    return (
        <Container
            maxW="max-content"
            py={8}
            px={{ base: 4, md: 8 }}
        >
            <Flex
                direction="column"
                align="center"
                mb={10}
            >
                <Heading
                    mb={6}
                    textAlign="center"
                    size="2xl"
                    color="blackAlpha.800"
                >
                    SAST Tools Explorer
                </Heading>

                <Text
                    textAlign="center"
                    fontSize="lg"
                    color="blackAlpha.800"
                >
                    Discover programming languages and their associated SAST tools
                </Text>
            </Flex>


            <Stack
                direction={{ base: 'column', md: 'row' }}
                spacing={4}
                mb={8}
                w="100%"
                mx="auto"
                maxW="800px"
            >
                <InputGroup
                    size="lg"
                    flex={1}
                    endElement={<IoIosSearch />}
                    aria-labelledby="search-languages"
                >
                    <Input
                        id="search-languages"
                        placeholder="Search language..."
                        value={searchTerm}
                        color="blackAlpha.800"
                        onChange={(e) => setSearchTerm(e.target.value)}
                        borderRadius="lg"
                        pr="4.5rem"
                        focusBorderColor="blue.500"
                        aria-label="Search for a programming language"
                    >
                    </Input>
                </InputGroup>

                <InputGroup
                   flex={1}
                    maxW={{ base: 'full', md: '250px' }}
                >
                    <Select.Root
                        value={filterByTool}
                        onValueChange={(e) => setFilterByTool(e.value)}
                        borderRadius="lg"
                        collection={toolOptions}
                        focusBorderColor="blue.500"
                        minW={{ base: '100%', md: '250px' }}
                        aria-label="tool-filter"
                    >
                        <Select.HiddenSelect />
                        <Select.Control>
                            <Select.Trigger>
                                <Select.ValueText placeholder="Select tool..." color="blackAlpha.800" />
                            </Select.Trigger>
                            <Select.IndicatorGroup>
                                {loading && (
                                    <Spinner />
                                )}
                                <Select.ClearTrigger />
                                <Select.Indicator />
                            </Select.IndicatorGroup>
                        </Select.Control>
                        <Portal>
                            <Select.Positioner>
                                <Select.Content>
                                    {toolOptions.items.map((tool) => (
                                        <Select.Item item={tool} key={tool.value}>
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

            {filteredLanguages.length === 0 ? (
                <Flex
                    minHeight="300px"
                    direction="column"
                    justify="center"
                    align="center"
                    minH="auto"
                    p={8}
                >
                    <Heading size="md" color="blackAlpha.800" mb={3}>No Languages found</Heading>
                    <Text color="crimson" fontSize="xs" mt={2}>Try adjusting your search or filters</Text>
                </Flex>) : (
                <Box>
                    <SimpleGrid columns={{ base: 1, sm: 2, lg: 3 }} spacing={6} mb={8}>
                        {
                            filteredLanguages.map(language => (
                                <LanguageToolTile
                                    key={language.name}
                                    language={language}
                                />
                            ))}
                    </SimpleGrid>

                    <Text mt={6} color="gray.500" textAlign="center">
                        Showing {filteredLanguages.length} of {languages.length} languages
                    </Text>
                </Box>
            )}

        </Container >
    );
}
