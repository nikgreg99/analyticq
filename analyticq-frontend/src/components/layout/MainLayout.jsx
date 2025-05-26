import React from "react";
import { Flex, Box, Container } from "@chakra-ui/react";
import { Header } from "./Header";
import { Footer } from "./Footer";

export const MainLayout = ({ children }) => (
  <Flex direction="column" minH="100vh" bg="gray.200">
    <Header />
    <Container
      as="main"
      maxW="container.xl"
      flex={1}
      py={{ base: 4, md: 6 }} // Adjust padding for different screen sizes
      px={{ base: 4, md: 6 }} // Adjust padding for different screen sizes
      role="main"
      aria-label="Main content area"
    >
      {children}
    </Container>
    <Footer />
  </Flex>
);

MainLayout.displayName = "MainLayout";
