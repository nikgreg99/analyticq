import React from "react";
import { Alert, Flex, VStack, HStack, CloseButton, useBreakpointValue } from "@chakra-ui/react";

/**
 * A responsive component that displays an empty state message with a title and alert.
 *
 * @component
 * @param {Object} props - The component props
 * @param {string} props.title - The main heading text to display
 * @param {string} props.message - The message to display in the alert description
 * @param {Function} [props.onClose] - Optional callback function when close button is clicked
 * @param {boolean} [props.showCloseButton=true] - Whether to show the close button
 * @returns {JSX.Element} A responsive alert component with heading and description
 */
const EmptyState = ({
  title,
  message,
  onClose = null,
  showCloseButton = true
}) => {
  const alertWidth = useBreakpointValue({
    base: "95%",
    sm: "85%",
    md: "75%",
    lg: "60%",
    xl: "50%"
  });

  const spacing = useBreakpointValue({ base: 3, md: 4 });
  const padding = useBreakpointValue({ base: 4, md: 6 });

  return (
    <Flex
      p={padding}
      width="100%"
      minHeight={{ base: "200px", md: "300px" }}
      align="center"
      justify="center"
    >
      <Alert.Root
        status="info"
        role="alert"
        aria-live="polite"
        aria-atomic="true"
        width={alertWidth}
        borderRadius="lg"
        boxShadow="sm"
        position="relative"
        py={padding}
        px={{ base: 4, md: 6 }}
      >
        <VStack spacing={spacing} align="center" textAlign="center" width="100%">
          <HStack spacing={2} align="center">
            <Alert.Indicator />
            <Alert.Title
              fontSize={{ base: "lg", md: "xl", lg: "2xl" }}
              fontWeight="semibold"
              color="blue.300"
            >
              {title}
            </Alert.Title>
          </HStack>

          <Alert.Description
            fontSize={{ base: "sm", md: "md" }}
            lineHeight="tall"
            color="whiteAlpha.600"
            maxWidth="90%"
          >
            {message}
          </Alert.Description>
        </VStack>

        {showCloseButton && onClose && (
          <CloseButton
            position="absolute"
            top={3}
            right={3}
            size="sm"
            onClick={onClose}
            aria-label="Close empty state message"
            _hover={{ bg: "gray.100" }}
            _focus={{
              boxShadow: "outline",
              bg: "gray.100"
            }}
          />
        )}
      </Alert.Root>
    </Flex>
  );
};

EmptyState.displayName = "EmptyState";

export default EmptyState;
