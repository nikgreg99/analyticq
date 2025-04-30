import React, { useEffect } from 'react';
import {
  Container,
  Heading,
  Text,
  VStack
} from '@chakra-ui/react';
import { updatePageMetadata } from 'components/utils/metadata';

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
    updatePageMetadata(
      'About the scanner',
      'About the SAST Scanner',
      "/about"
    )
  },[]);

  return (
    <Container
      maxW="container.md"
      py={16}
      as="main"
      role='main'
    >
      <VStack
        as="section"
        spacing={8}
        p={10}
        borderRadius="2xl"
        align="center"
        aria-labelledby="about-heading"
      >
        <Heading
          id="about-heading"
          as="h1"
          size="xl"
          ml={2}
          color="blackAlpha.800"
          tabIndex={-1}
        >
          AnalyticQ SAST Analysis Tool
        </Heading>

        <Text
          textAlign="center"
          fontSize="lg"
          color="blackAlpha.800"
          maxW="600px"
        >
          Master's Thesis Project developed by Nicolas Gregori
        </Text>

        <Text
          textAlign="center"
          fontSize="md"
          maxW="700px"
          lineClamp="tall"
          color="blackAlpha.800"
        >
          A project focused  on a Static Application
          Security Testing (SAST) system tool to identify vulnerabilities in source code.
        </Text>
      </VStack>
    </Container>
  );
};

export default AboutPage;
