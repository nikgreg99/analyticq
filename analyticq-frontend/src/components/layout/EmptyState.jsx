import React from "react";
import { Alert, Flex, CloseButton, useBreakpointValue } from "@chakra-ui/react";

/**
 * A responsive component that displays an empty state message with a title and alert.
 *
 * @component
 * @param {Object} props - The component props
 * @param {string} props.title - The main heading text to display
 * @param {string} props.message - The message to display in the alert description
 * @returns {JSX.Element} A responsive alert component with heading and description
 */
const EmptyState = ({ title, message }) => {
  const alertWidth = useBreakpointValue({
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
      minHeight={{ base: "200px", md: "300px" }}
      align="center"
      justify="center"
    >
      <Alert.Root
        status="info"
        title={title}
        role="alert"
        aria-live="assertive"
        aria-atomic="true"
        width={alertWidth}
        flexDirection="column"
        textAlign="center"
        borderRadius="md"
        py={{ base: 4, md: 6 }}
        px={{ base: 3, md: 5 }}
      >
        <Alert.Indicator />
        <Alert.Content>
          <Alert.Title fontSize={{ base: "lg", md: "xl" }}>{title}</Alert.Title>
          <Alert.Description fontSize={{ base: "sm", md: "md" }}>
            {message}
          </Alert.Description>
        </Alert.Content>
        <CloseButton pos="absolute" top={2} right={2} />
      </Alert.Root>
    </Flex>
  );
};

export default EmptyState;
