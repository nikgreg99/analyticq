import React from "react";
import {
  Alert,
  Flex,
  VStack,
  HStack,
  useBreakpointValue,
  Container,
  AlertIndicator
} from "@chakra-ui/react";

/**
 * A component that displays error messages with optional back and retry buttons.
 *
 * @param {Object} props - The component props
 * @param {string} props.title - The title of the error message
 * @param {string|React.ReactNode} props.error - The error message or error content to display
 * @param {React.ReactNode} [props.backButton] - Optional back button component
 * @param {React.ReactNode} [props.retryButton=null] - Optional retry button component
 * @returns {React.ReactElement} A centered container with an alert displaying the error
 */
const ErrorDisplay = ({ title, error, backButton = null, retryButton = null }) => {
  const alertMaxWidth = useBreakpointValue({ base: "90%", md: "500px", lg: "600px" });
  const spacing = useBreakpointValue({ base: 3, md: 4 });
  const padding = useBreakpointValue({ base: 4, md: 6, lg: 8 });
  const buttonSpacing = useBreakpointValue({ base: 2, md: 3 });

  return (
    <Flex
      width="100%"
      minHeight="200px"
      align="center"
      justify="center"
      p={padding}
    >
      <Container maxWidth={alertMaxWidth} centerContent>
        <VStack spacing={spacing} width="100%" align="stretch">
          <Alert.Root
            status="error"
            variant="subtle"
            borderRadius="lg"
            boxShadow="md"
            width="100%"
            role="alert"
            aria-live="assertive"
            aria-labelledby="error-title"
          >
            <VStack spacing={spacing} align="center" textAlign="center" p={spacing} width="100%">
              <HStack spacing={2} align="center">
                <AlertIndicator />
                <Alert.Title
                  id="error-title"
                  fontSize={{ base: "lg", md: "xl" }}
                  fontWeight="semibold"
                >
                  {title}
                </Alert.Title>
              </HStack>

              <Alert.Description
                fontSize={{ base: "sm", md: "md" }}
                lineHeight="tall"
                color="whiteAlpha.700"
                maxWidth="100%"
              >
                {error}
              </Alert.Description>
            </VStack>
          </Alert.Root>

          {(backButton || retryButton) && (
            <HStack
              spacing={buttonSpacing}
              justify="center"
              wrap="wrap"
              width="100%"
              pt={2}
            >
              {backButton}
              {retryButton}
            </HStack>
          )}
        </VStack>
      </Container>
    </Flex>
  );
};

ErrorDisplay.displayName = "ErrorDisplay";

export default ErrorDisplay;
