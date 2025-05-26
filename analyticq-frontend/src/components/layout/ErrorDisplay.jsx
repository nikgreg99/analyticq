import React from "react";
import { Alert, Flex, useBreakpointValue } from "@chakra-ui/react";
import { Box } from "lucide-react";

/**
 * A component that displays error messages with optional back and retry buttons.
 *
 * @param {Object} props - The component props
 * @param {string} props.title - The title of the error message
 * @param {string|React.ReactNode} props.error - The error message or error content to display
 * @param {React.ReactNode} [props.backButton] - Optional back button component
 * @param {React.ReactNode} [props.retryButton=null] - Optional retry button component
 * @returns {React.ReactElement} A flex container with an alert displaying the error
 */
const ErrorDisplay = ({ title, error, backButton, retryButton = null }) => {
  const width = useBreakpointValue({
    base: "100%",
    sm: "90%",
    md: "80%",
    lg: "60%",
  });

  return (
    <Flex
      p={{ base: 4, md: 6 }}
      textAlign="center"
      width="100%"
      height="100%"
      align="center"
      justify="center"
      w={width}
    >
      <Alert.Root
        role="alert"
        aria-live="assertive"
        aria-labelledby="error-title"
        status="error"
        mb={4}
        width="100%"
        height="100%"
        align="center"
        justify="center"
      >
        <Alert.Indicator />
        <Alert.Content textAlign="center">
          <Alert.Title>{title}</Alert.Title>
          <Alert.Description>{error}</Alert.Description>
        </Alert.Content>
        {error}
      </Alert.Root>
      {backButton && <Box>{backButton}</Box>}
      {retryButton && <Box>{retryButton}</Box>}
    </Flex>
  );
};
export default ErrorDisplay;
