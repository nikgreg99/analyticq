import React from "react";
import { Box, VStack, Progress, Flex, Button, Text } from "@chakra-ui/react";

export const ScanStatusIndicator = ({ scanStatus, resetScan }) => {
  const isInProgress =
    scanStatus.status === "pending" || scanStatus.status === "running";

  const getStatusColor = () => {
    switch (scanStatus.status) {
      case "pending":
        return "yellow";
      case "running":
        return "blue";
      case "completed":
        return "green";
      case "failed":
        return "red";
      default:
        return "gray";
    }
  };

  const getStatusText = () => {
    switch (scanStatus.status) {
      case "pending":
        return "Queued...";
      case "running":
        return "Scanning in progress...";
      case "completed":
        return "Analysis complete!";
      case "failed":
        return "Analysis failed.";
      default:
        return "";
    }
  };

  return (
    <Box
      p={6}
      borderRadius="lg"
      bordderWidth="1px"
      aria-live="polite"
      aria-atomic="true"
    >
      <VStack align="stretch">
        <Progress.Root
          size="sm"
          colorPalette={getStatusColor}
          color="blackAlpha.800"
          value={scanStatus.status === "completed" ? 100 : null}
          striped
          animated
          aria-label={`Analysis status: ${scanStatus.status}`}
        >
          <Progress.Track>
            <Progress.Range />
          </Progress.Track>
        </Progress.Root>

        <Flex justify="space-between" align="center">
          <Text fontWeight="medium" color="gray.700">
            {getStatusText()}
          </Text>
          {(scanStatus.status === "pending" ||
            scanStatus.status === "running") && (
            <Text fontSize="sm" color="gray.500">
              ID: {scanStatus.id.substring(0, 8)}...
            </Text>
          )}
        </Flex>

        {(scanStatus.status === "pending" ||
          scanStatus.status === "running") && (
          <Text fontSize="sm" color="gray.600">
            This may take several minutes depending on the size of your
            codebase.
          </Text>
        )}

        {isInProgress && (
          <Button
            size="sm"
            colorPalette="blue"
            variant="solid"
            onClick={resetScan}
            aria-label="Clear error status and try again"
          >
            Try Again
          </Button>
        )}
      </VStack>
    </Box>
  );
};

ScanStatusIndicator.displayName = "ScanStatusIndicator";
