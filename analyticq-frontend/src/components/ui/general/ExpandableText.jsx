import React, { useState } from "react";
import {
  Text,
  Button,
  Icon,
  useBreakpointValue,
  HStack,
} from "@chakra-ui/react";
import { FaEye, FaEyeSlash } from "react-icons/fa";

/**
 * A component that displays text with expandable functionality.
 * The text is truncated if it exceeds the maximum character limit,
 * and can be expanded/collapsed via a toggle button.
 *
 * @param {Object} props - Component props
 * @param {string} props.text - The text content to display
 * @param {number} [props.maxChars=200] - Maximum number of characters to show before truncating
 * @param {string} [props.expansableTextColor] - Color of the text content
 *
 * @returns {JSX.Element} A horizontally stacked container with text and optional expand/collapse button
 *
 * @example
 * <ExpandableText
 *   text="Long text content..."
 *   maxChars={150}
 *   expansableTextColor="gray.600"
 * />
 */
const ExpandableText = ({ text, maxChars = 200, expansableTextColor }) => {
  const [expanded, setExpanded] = useState(false);
  const isTruncated = text.length > maxChars;
  const displayText =
    expanded || !isTruncated ? text : text.slice(0, maxChars) + "..";

  const toggleExpanded = () => setExpanded((prev) => !prev);

  const baseFontSize = useBreakpointValue({ base: "sm", md: "md" });

  return (
    <HStack w="100%">
      <Text
        id="expandable-text"
        fontSize={baseFontSize}
        noOfLines={expanded ? undefined : 3}
        color={expansableTextColor}
        whiteSpace="pre-wrap"
        wordBreak="break-word"
      >
        {displayText}
      </Text>

      {isTruncated && (
        <Button
          onClick={toggleExpanded}
          variant="link"
          size="sm"
          mt={2}
          colorPalette="blue"
          aria-expanded={expanded}
          aria-controls="expandable-text"
        >
          <Icon as={expanded ? FaEyeSlash : FaEye} boxSize={4} />
          <Text>{expanded ? "Hide" : "View more"}</Text>
        </Button>
      )}
    </HStack>
  );
};

ExpandableText.displayName = "ExpandableText";

export default ExpandableText;
