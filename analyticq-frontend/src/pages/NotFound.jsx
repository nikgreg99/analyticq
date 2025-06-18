import React, { useEffect } from "react";
import { Box, Heading, Text, VStack, Button } from "@chakra-ui/react";
import { Link as RouterLink } from "react-router-dom";
import { FaHome } from "react-icons/fa";
import { updatePageMetadata } from "components/utils/metadata";

/**
 * Renders a 404 Not Found page component.
 * Updates page metadata with 404 information and displays a centered error message
 * with a button to navigate back to the home page.
 *
 * @component
 * @return {JSX.Element} A vertical stack containing 404 error message and home navigation button
 */
export const NotFoundPage = () => {
  useEffect(() => {
    updatePageMetadata("Page not found", "Page not found. Try again", "/404");
  });

  return (
    <Box as="main" py={20} px={4}>
      <VStack
        spacing={6}
        textAlign="center"
        role="main"
        maxW="xl"
        mx="auto"
        aria-labelledby="not-found-heading"
      >
        <Heading
          as="h1"
          size="3xl"
          color="gray.500"
          fontWeight="bold"
          aria-hidden="true"
          lineHeight="1"
        >
          404
        </Heading>
        <Heading id="not-found-heading" size="lg" color="gray.700">
          Oops! Page Not Found
        </Heading>
        <Text color="gray.600" maxW="md">
          The page you are looking for might be not exists. Try another path or
          click below to return home.
        </Text>
        <Button
          marginTop="3em"
          as={RouterLink}
          to="/"
          colorPalette="black"
          variant="subtle"
          size="sm"
          mt={8}
          px={8}
          py={6}
          _hover={{
            transform: "translateY(-2px)",
            boxShadow: "1g",
          }}
          transition="all 0.2s"
          aria-label="Go to Home Page"
        >
          <FaHome aria-hidden="true" focusable="false"/>
          Return to Home
        </Button>
      </VStack>
    </Box>
  );
};

NotFoundPage.displayName = "NotFoundPage";
