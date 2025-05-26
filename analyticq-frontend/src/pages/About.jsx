import React, { useEffect } from "react";
import {
  Container,
  Heading,
  Text,
  VStack,
  useBreakpointValue,
} from "@chakra-ui/react";
import { updatePageMetadata } from "components/utils/metadata";

/**
 * Renders the About page of the AnalyticQ SAST Analysis Tool.
 * This component displays information about the master's thesis project and its purpose.
 * Uses Chakra UI components for layout and styling.
 *
 * @component
 * @example
 * ```jsx
 * <AboutPage />
 * ```
 *
 * @returns {JSX.Element} A container with project information including title, author, and description
 */
export const AboutPage = () => {
  useEffect(() => {
    updatePageMetadata("About the scanner", "About the SAST Scanner", "/about");
  }, []);

  // Responsive font size for the heading and description
  const headingSize = useBreakpointValue({ base: "2xl", md: "3xl" });
  const textSize = useBreakpointValue({ base: "md", lg: "lg" });

  return (
    <Container maxW="container.md" py={16} as="main" role="main">
      <VStack
        as="section"
        spacing={{ base: 6, md: 8 }} // Responsive spacing
        p={6}
        borderRadius="2xl"
        align="center"
        aria-labelledby="about-heading"
      >
        <Heading
          id="about-heading"
          as="h1"
          size={headingSize} // Responsive heading size
          ml={2}
          color="blackAlpha.800"
          tabIndex={-1}
        >
          AnalyticQ SAST Analysis Tool
        </Heading>

        <Text
          textAlign="center"
          fontSize={textSize} // Responsive text size
          color="blackAlpha.800"
          maxW={{ base: "100%", md: "600px" }} // Adjust max width based on screen size
        >
          Master's Thesis Project developed by Nicolas Gregori
        </Text>

        <Text
          textAlign="center"
          fontSize={{ base: "sm", lg: "md" }} // Responsive text size for the description
          maxW={{ base: "100%", md: "700px" }} // Max width adjusted based on screen size
          lineClamp={3} // Limit the lines for longer descriptions
          color="blackAlpha.800"
        >
          A project focused on a Static Application Security Testing (SAST)
          system tool to identify vulnerabilities in source code.
        </Text>
      </VStack>
    </Container>
  );
};

AboutPage.displayName = "AboutPage";

export default AboutPage;
