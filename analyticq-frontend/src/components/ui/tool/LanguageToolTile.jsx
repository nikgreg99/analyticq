import React, { useMemo } from "react";
import { Box, Flex, Icon, Badge, Text, Heading } from "@chakra-ui/react";
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
  const { toolsCount, hasTools } = useMemo(() => {
    const toolsList = Array.isArray(language.tools) ? language.tools : [];
    return {
      toolsCount: toolsList.length,
      hasTools: toolsList.length > 0,
    };
  }, [language.tools]);

  if (!language) {
    return null;
  }

  const headingId = `language-${language.name?.toLowerCase().replace(/\s+/g, "-")}-heading`;
  const toolsDescId = `language-${language.name?.toLowerCase().replace(/\s+/g, "-")}-tools-desc`;

  return (
    <Box
      p={5}
      shadow="md"
      borderWidth="1px"
      _hover={{
        transform: "translateY(-5px)",
        shadow: "lg",
        transition: "all 0.3s ease",
      }}
      role="group"
      position="relative"
      aria-labelledby={headingId}
      aria-describedby={toolsDescId}
      transition="all 0.3s ease"
    >
      <Flex align="center" mb={3}>
        <Icon
          aria-hidden="true"
          as={Code}
          boxSize={6}
          transition="color 0.2s ease"
          color="black"
        />
        <Heading id={headingId} fontSize="xl" ml={3} color="blackAlpha.800">
          {language.name || "Unknown language"}
        </Heading>
      </Flex>

      <Text
        fontSize="sm"
        color="blackAlpha.800"
        mb={4}
        aria-label={`${toolsCount} ${toolsCount === 1 ? "tool" : "tools"} available`}
      >
        {toolsCount} {toolsCount === 1 ? "tool" : "tools"} available
      </Text>

      {hasTools ? (
        <Flex wrap="wrap" gap={2} aria-label={`Tools for ${language.name}`}>
          {language.tools.map((tool, index) => (
            <Badge
              key={`tooltip-${index}`}
              variant="subtle"
              px={2}
              py={1}
              borderRadius="md"
              fontSize="sm"
              fontWeight="medium"
              colorPalette={colorScheme}
              aria-label={tool}
              truncate
              textOverflow="ellipsis"
              overflow="hidden"
              maxW="120px"
            >
              {tool}
            </Badge>
          ))}
        </Flex>
      ) : (
        <Text color="gray.500" fontSize="sm" aria-label="No tools available">
          No tools available for this language
        </Text>
      )}
    </Box>
  );
};

LanguageToolTile.displayName = "LanguageToolTile";
