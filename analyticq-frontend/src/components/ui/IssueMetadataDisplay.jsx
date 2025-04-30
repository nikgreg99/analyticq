import React, { useState } from "react";
import {
  Box,
  Text,
  Button,
  Heading,
  Flex,
  Icon,
  Link
} from "@chakra-ui/react";
import { FaChevronDown, FaChevronUp, FaExternalLinkAlt } from "react-icons/fa";


/**
 * A component that displays issue metadata in a formatted JSON-like structure.
 * If no metadata is provided or if it's empty, displays a message indicating no metadata is available.
 *
 * @component
 * @param {Object} props - The component props
 * @param {Object} props.metadata - The metadata object to display
 * @returns {JSX.Element} A formatted display of the metadata or a "no metadata" message
 *
 * @example
 * const metadata = { key: "value", nested: { prop: true } };
 * <IssueMetadataDisplay metadata={metadata} />
 */
export const IssueMetadataDisplay = ({ metadata }) => {
  if (!metadata || Object.keys(metadata).length === 0) {
    return (
      <Flex p={4}
        borderRadius="md"
        width="auto"
        bg="gray.50">
        <Text
          fontStyle="italic"
          textAlign="center"
          color="blackAlpha.800"
        >
          No additional metadata available
        </Text>
      </Flex>
    );
  }

  return (
    <Box borderRadius="md" borderWidth="1px" overflow="hidden" role="region" aria-labelledby="metadata-heading">
      <Box p={4} fontFamily="monospace" fontSize="sm">
        <Box color="blackAlpha.800">{"{"}</Box>
        <JsonTree data={metadata} />
        <Box color="blackAlpha.800">{"}"}</Box>
      </Box>
    </Box>
  );
};


/**
 * Recursive component to render a collapsible JSON tree
 */
const JsonTree = ({ data, indentLevel = 1 }) => {
  if (!data || typeof data !== "object") return null;

  const entries = Object.entries(data);

  return (
    <>
      {entries.map(([key, value], index) => {
        const isLast = index === entries.length - 1;
        return (
          <JsonNode
            key={key}
            nodeKey={key}
            value={value}
            indentLevel={indentLevel}
            isLastItem={isLast}
          />
        );
      })}
    </>
  );
};

/**
 * Renders text content with embedded URLs as clickable links.
 * The component wraps the entire text in quotation marks and transforms any URLs within the text into clickable links.
 *
 * @component
 * @param {Object} props - Component props
 * @param {string} props.value - The text string that may contain URLs to be transformed into links
 *
 * @returns {JSX.Element} A Text component containing the string with any URLs rendered as clickable links
 *
 * @example
 * // Will render regular text: "Hello world"
 * <StringsWithLinks value="Hello world" />
 *
 * // Will render text with a clickable link: "Check this https://example.com website"
 * <StringsWithLinks value="Check this https://example.com website" />
 */
const StringsWithLinks = ({ value }) => {
  const urlRegex = /(https?:\/\/[^\s"]+)/g;

  if (!urlRegex.test(value)) {
    // If no URLs found, render as normal string
    return <Text as="span" color="blackAlpha.800">"{value}"</Text>;
  }

  const parts = value.split(urlRegex);

  return (
    <Text as="span">
      "
      {parts.map((part, index) => {
        // Check if this part matches a URL
        if (index % 2 === 1) {
          // This is a URL (odd index in parts array)
          return (
            <Link
              key={index}
              href={part}
              color="blue.500"
              external
              _hover={{ textDecoration: "underline" }}
              aria-label={`Visit link: ${part}`}
            >
              {part}
              <Icon as={FaExternalLinkAlt} boxSize={2} ml={1} verticalAlign="super" color="blackAlpha.800" />
            </Link>
          );
        }
        // Regular text
        return part;
      })}
      "
    </Text>
  );
};



const JsonNode = ({ nodeKey, value, indentLevel, isLastItem }) => {
  const [isExpanded, setIsExpanded] = useState(true);
  const indent = "  ".repeat(indentLevel);
  const isObject = value !== null && typeof value === "object";

  const toggle = () => {
    if (isObject) setIsExpanded(!isExpanded);
  };

  const renderValue = () => {
    if (value === null) return <Text as="span" color="blackAlpha.800">null</Text>;
    if (typeof value === "boolean") return <Text as="span" color="blackAlpha.800">{value.toString()}</Text>;
    if (typeof value === "number") return <Text as="span" color="blackAlpha.800">{value}</Text>;
    if (typeof value === "string") return <StringsWithLinks value={value} />;

    if (Array.isArray(value)) {
      if (value.length === 0) return <Text as="span" color="blackAlpha.800">[]</Text>;
      return (
        <>
          <Text as="span" color="blackAlpha.800">[</Text>
          {isExpanded && (
            <Box ml={6}>
              {value.map((item, idx) => (
                <Box key={idx}>
                  {"  ".repeat(indentLevel + 1)}
                  <JsonValue value={item} />
                  {idx < value.length - 1 && ","}
                </Box>
              ))}
            </Box>
          )}
          <Text as="span" color="blackAlpha.800">{indent}]</Text>
        </>
      );
    }

    if (isObject) {
      const keys = Object.keys(value);
      if (keys.length === 0) return <Text as="span" color="blackAlpha.800">{"{}"}</Text>;

      return (
        <>
          <Text as="span" color="blackAlpha.800">{"{"}</Text>
          {isExpanded && (
            <JsonTree data={value} indentLevel={indentLevel + 1} />
          )}
          <Text as="span" color="blackAlpha.800">{indent}{"}"}</Text>
        </>
      );
    }

    return <Text as="span" color="blackAlpha.800">{String(value)}</Text>;
  };

  return (
    <Box>
      <Heading></Heading>
      <Flex align="flex-start">
        {isObject ? (
          <Button
            onClick={toggle}
            variant="unstyled"
            size="xs"
            minW="auto"
            h="auto"
            p={0}
            mr={1}
            aria-label={isExpanded ? `Collapse ${nodeKey}` : `Expand ${nodeKey}`}
            aria-expanded={isExpanded}
          >
            <Icon as={isExpanded ? FaChevronDown : FaChevronUp} boxSize={3} />
          </Button>
        ) : (
          <Box width="14px" />
        )}
        <Box>
          {indent}
          <Text as="span" fontWeight="bold" color="blackAlpha.800">"{nodeKey}"</Text>
          <Text as="span" color="blackAlpha.800">: </Text>
          {renderValue()}
          {!isLastItem && <Text as="span" color="blackAlpha.800">,</Text>}
        </Box>
      </Flex>
    </Box>
  );
};





/**
 * Renders a value as a text span with a specific color.
 * @component
 * @param {Object} props - The component props
 * @param {any} props.value - The value to be displayed as text
 * @returns {JSX.Element} A Text component displaying the string representation of the value
 */
const JsonValue = ({ value }) => {
  return <Text as="span" color="blackAlpha.800">{String(value)}</Text>;
};

export default IssueMetadataDisplay;
