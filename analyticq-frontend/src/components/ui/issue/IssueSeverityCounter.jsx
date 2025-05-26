import React from "react";
import {
  Box,
  Text,
  Icon,
  Flex,
  Skeleton,
  useBreakpointValue,
} from "@chakra-ui/react";
import {
  FaExclamationTriangle,
  FaExclamation,
  FaInfoCircle,
  FaBell,
  FaCheckCircle,
} from "react-icons/fa";

const SEVERITY_ICONS = {
  critical: FaExclamationTriangle,
  high: FaExclamation,
  medium: FaBell,
  low: FaCheckCircle,
  info: FaInfoCircle,
};

const SEVERITY_STYLES = {
  critical: {
    bg: "red.100",
    text: "red.700",
    hoverBg: "red.200",
    iconColor: "red.600",
  },
  high: {
    bg: "orange.100",
    text: "orange.700",
    hoverBg: "orange.200",
    iconColor: "orange.600",
  },
  medium: {
    bg: "yellow.100",
    text: "yellow.700",
    hoverBg: "yellow.200",
    iconColor: "yellow.600",
  },
  low: {
    bg: "green.100",
    text: "green.700",
    hoverBg: "green.200",
    iconColor: "green.600",
  },
  info: {
    bg: "blue.100",
    text: "blue.700",
    hoverBg: "blue.200",
    iconColor: "blue.600",
  },
  warning: {
    bg: "teal.100",
    text: "teal.700",
    hoverBg: "teal.200",
    iconColor: "teal.600",
  },
  inactive: {
    bg: "gray.50",
    text: "gray.500",
    hoverBg: "gray.100",
    iconColor: "gray.400",
  },
};

/**
 * A component that displays a counter for issues of a specific severity level.
 *
 * @component
 * @param {Object} props - The component props
 * @param {string} props.label - The text label for the severity level
 * @param {number} props.count - The number of issues for this severity level
 * @param {string} props.colorScheme - The color scheme key used to determine background and text colors
 * @param {boolean} props.hasCritical - Whether the critical severity level is present, affects width calculation
 * @returns {JSX.Element} A box containing the severity label and count with appropriate styling
 */
export const IssueSeverityCounter = ({
  label,
  count,
  hasCritical,
  isLoading = false,
}) => {
  const widthPercent = useBreakpointValue({
    base: "100%",
    sm: "45%",
    md: hasCritical ? "19%" : "22%",
  });

  const severityKey = count === 0 ? "inactive" : label.toLowerCase();
  const styles = SEVERITY_STYLES[severityKey] || SEVERITY_STYLES.inactive;

  // Find the appropriate icon for this severity
  const bgColor = styles.bg || "gray.50";
  const txtColor = styles.text || "gray.600";

  const SeverityIcon = SEVERITY_ICONS[severityKey] || FaInfoCircle;

  return (
    <Box
      p={4}
      as="section"
      bg={bgColor}
      borderRadius="md"
      textAlign="center"
      width={{ base: "100%", sm: "45%", md: widthPercent }}
      role="region"
      aria-labelledby={`${severityKey}-label`}
      data-testid={`severity-counter-${severityKey}`}
      transition="all 0.2s ease-in-out"
      boxShadow="sm"
    >
      <Flex
        direction="column"
        alignItems="center"
        justifyContent="center"
        height="100%"
      >
        <Flex alignItems="center" mb={1}>
          <Icon
            as={SeverityIcon}
            color={styles.iconColor}
            mr={1}
            aria-hidden="true"
          />
          <Text
            id={`${severityKey}-label`}
            fontSize="sm"
            color={txtColor}
            aria-label={`${severityKey} severity level`}
          >
            {label}
          </Text>
        </Flex>

        {isLoading ? (
          <Skeleton height="20px" width="50%" mt={2} />
        ) : (
          <Text
            fontSize={{ base: "xl", md: "2xl" }}
            fontWeight="bold"
            color={txtColor}
            aria-live="polite"
            aria-atomic="true"
            aria-label={`${count} ${label.toLowerCase()} ${count === 1 ? "issue" : "issues"}`}
          >
            {count}
          </Text>
        )}
      </Flex>
    </Box>
  );
};

IssueSeverityCounter.displayName = "SeverityCounter";

export default IssueSeverityCounter;
