import React from 'react';
import {
  Box,
  Container,
  Heading,
  Text,
  VStack
} from '@chakra-ui/react';

export const AboutPage = () => {
  return (
    <Container maxW="container.md" py={16}>
      <VStack
        spacing={8}
        p={10}
        borderRadius="2xl"
        align="center">
        <Heading
          as="h1"
          size="xl"
          ml={2}
          color="blackAlpha.800"
          >
            AnalyticQ SAST Analysis Tool
        </Heading>

        <Text
            textAlign="center"
            fontSize="lg"
            color="blackAlpha.800"
            maxW="600px"
          >
            Master's Thesis Project developied by Nicolas Gregori
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
