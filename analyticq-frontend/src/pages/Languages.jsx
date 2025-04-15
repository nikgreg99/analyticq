import React, { useState, useEffect, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import {
    Container,
    Heading,
    SimpleGrid,
    Box,
    Text,
    Icon,
    Flex,
    VStack,
    Badge
} from "@chakra-ui/react";
import { Code } from "lucide-react";
import { updatePageMetadata } from "components/utils/metadata";
import { getSupportedLanguages } from "services/toolService";
import LoadingSpinner from "components/ui/LoadingSpinner";
import ErrorDisplay from "components/layout/ErrorDisplay";
import BackButton from "components/ui/BackButton";

/**
 * Renders a page displaying all programming languages supported by the SAST analyzer
 *
 * @component
 * @param {Object} props - Component props
 * @param {string[]|null} props.initialSupportedLanguages - Initial array of supported programming languages. If null, languages will be fetched from API
 * @returns {JSX.Element} A page showing a grid of supported programming languages with icons
 *
 * @throws {Error} When failing to fetch supported languages from API
 *
 * @example
 * ```jsx
 * <LanguagesPage initialSupportedLanguages={["JavaScript", "Python", "Java"]} />
 * ```
 */
export const LanguagesPage = ({ initialSupportedLanguages = null }) => {

    const [languagesSupported, setLanguagesSupported] = useState(initialSupportedLanguages);
    const [loading, setLoading] = useState(!initialSupportedLanguages);
    const [error, setError] = useState(null);
    const navigate = useNavigate();


    useEffect(() => {
        updatePageMetadata(
            "Language Supported",
            'Analytic Q Language Supported',
            '/language-supported'
        )
    }, []);

    const handleClickBack = () => {
        navigate("/");
    }


    const fetchSupportedLanguages = useCallback(async () => {
        try {
            const data = await getSupportedLanguages();
            console.log("Fetching supported languages", data);
            setLanguagesSupported(data);
            setError();
        }
        catch (error) {
            console.error("Error fetching context details:", error);
            setError("Failed to load suppported language details. Please try again later.");
        }
        finally {
            setLoading(false);
        }
    }, [setLoading])


    useEffect(() => {
        if (!initialSupportedLanguages) {
            fetchSupportedLanguages()
        }
    }, [fetchSupportedLanguages, initialSupportedLanguages]);

    if (loading) {
        return <LoadingSpinner />
    }

    if (error) {
        return <ErrorDisplay
            title="Language Supported"
            error={error}
            backButton={<BackButton onClick={handleClickBack} label="Back to Home" />}
        />
    }

    const formatLanguageName = (language) => {
        // Your formatting logic here
        return language.charAt(0).toUpperCase() + language.slice(1);
    };

    return (
        <Container maxWidth="auto">
            <VStack>
                <Box textAlign="center" mb={4}>
                    <Heading
                        as="h1"
                        size="xl"
                        mb={2}
                        color="blackAlpha.800"
                    >
                        Supported Languages
                    </Heading>
                    <Text
                        color="blackAlpha.800"
                        fontSize="lg">
                        This analyzer system supports the following programming languages:
                    </Text>
                </Box>

                <SimpleGrid
                    columns={{ base: 1, sm: 2, md: 3, lg: 4, xl: 5 }}
                    spacing={4}
                    px={{ base: 2, md: 4 }}
                >
                    {languagesSupported.map((lang) => (
                        <Box
                            key={lang}
                            p={4}
                            borderWidth="1px"
                            borderRadius="lg"
                            _hover={{
                                transform: "translateY(-4px)",
                                shadow: "md",
                                borderColor: "blue.400"
                            }}
                            transition="all 0.3s ease"
                        >
                            <Flex align="center" justify="center">
                                <Icon
                                    as={Code}
                                    boxSize={6}
                                    mr={3}
                                    color="blackAlpha.800"
                                />
                                <Text
                                    fontWeight="semibold"
                                    fontSize="md"
                                    color="blackAlpha.800"
                                >
                                    {formatLanguageName(lang)}
                                </Text>
                            </Flex>
                        </Box>
                    ))}
                </SimpleGrid>
                <Box>
                    <Badge
                        alignSelf="center"
                        fontSize="md"
                        mb={2}
                        color="whiteAlpha.900"
                    >
                        {languagesSupported.length} languages available
                    </Badge>

                </Box>
            </VStack>
        </Container>

    );

}
