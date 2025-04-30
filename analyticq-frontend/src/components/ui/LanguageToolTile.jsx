import React from "react";
import {
    Box,
    Flex,
    Icon,
    Badge,
    Text,
    Heading
} from "@chakra-ui/react";
import { Code } from "lucide-react";

/**
 * A component that displays a tile containing information about a programming language and its tools.
 *
 * @component
 * @param {Object} props - The component props
 * @param {Object} props.language - The language object to display
 * @param {string} props.language.name - The name of the programming language
 * @param {string[]} props.language.tools - Array of tools associated with the language
 * @param {string} [props.colorScheme="red"] - The color scheme to use for the badges
 *
 * @returns {JSX.Element} A box containing the language name, number of tools, and tool badges
 *
 * @example
 * const language = {
 *   name: "JavaScript",
 *   tools: ["React", "Vue", "Angular"]
 * };
 *
 * <LanguageToolTile language={language} colorScheme="blue" />
 */
export const LanguageToolTile = ({ language, colorScheme = "red" }) => {

    const toolsCount = language.tools.length;
    const hasTools = toolsCount > 0;

    return (
        <Box
            p={5}
            shadow="md"
            borderWidth="1px"
            _hover={{
                transform: "translateY(-5px)",
                shadow: 'lg',
                transition: 'all 0.3s ease'
            }}
            role="group"
            position="relative"
        >
            <Flex align="center" mb={3}>
                <Icon
                    aria-hidden="true"
                    as={Code}
                    boxSize={6}
                    transition="color 0.2s ease"
                >
                    <Code color="black" />
                </Icon>
                <Heading fontSize="xl" ml={3} color="blackAlpha.800">{language.name}</Heading>
            </Flex>

            <Text
                fontSize="sm"
                color="blackAlpha.800"
                mb={4}
                aria-label={`${toolsCount} ${toolsCount === 1 ? "tool" : "tools"} available`}
            >
                {language.tools.length} {language.tools.length === 1 ? "tool" : "tools"} available
            </Text>

            {hasTools ? (
                <Flex
                    wrap="wrap"
                    gap={2}
                    aria-label="Available tools"
                >
                    {language.tools.map((tool, index) => (
                        <Badge
                            key={index}
                            variant="subtle"
                            px={2}
                            py={1}
                            borderRadius="md"
                            fontSize="sm"
                            fontWeight="medium"
                            colorScheme={colorScheme}
                            title={tool}
                        >
                            {tool}
                        </Badge>
                    ))}
                </Flex>
            ) : (
                <Text
                    color="gray.500"
                    fontSize="sm"
                    aria-label="No tools available"
                >
                    No tools configured
                </Text>
            )}
        </Box >
    );
};
