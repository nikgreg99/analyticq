import React from "react";
import { Box, Progress, HStack } from "@chakra-ui/react";

/**
 * A labeled progress bar component with percentage display
 * @component
 * @param {Object} props - Component props
 * @param {string} props.label - Text label for the progress bar
 * @param {number} props.percentage - Progress percentage value (0-100)
 * @param {string} props.colorScheme- Color scheme for progress bar
 * @returns {JSX.Element} A progress bar with label and percentage display
 */
export const ProgessBarLabeled = ({
  label,
  percentage,
  colorScheme = "blue",
  id,
  hidePercentage = false,
  type = "determinate"
}) => {

  const progressId = React.useId()
  const labelId = id || `progress-${progressId}`;

  const normalizedPercentage = Math.max(0, Math.min(100, percentage || 0));


  return (
    <Box as="section" position="relative" mb={4}>
      <Progress.Root
        id={progressId}
        value={type === 'determinate' ? normalizedPercentage : undefined}
        maxW="sm"
        borderRadius="full"
        size="md"
        flex="1"
        mr={2}
        colorPalette={colorScheme ? colorScheme : null}
        aria-label={`${label} progress: ${percentage}%`}
        aria-labelledby={labelId}
        aria-valuemin={0}
        aria-valuemax={100}
        aria-valuenow={type === 'determinate' ? normalizedPercentage : undefined}
        aria-valuetext={type === 'determinate' ? `${normalizedPercentage}%` : undefined}
        role="progressbar"
      >
        <HStack gap={5}>
          <Progress.Label>{label}</Progress.Label>
          <Progress.Track flex="1">
            <Progress.Range />
          </Progress.Track>
          {!hidePercentage && type === 'determinate' && (
            <Progress.ValueText aria-hidden="true">
              {normalizedPercentage}%
            </Progress.ValueText>
          )}
        </HStack>
      </Progress.Root>
    </Box>
  );
};

ProgessBarLabeled.displayName = "ProgressBarLabeled"
