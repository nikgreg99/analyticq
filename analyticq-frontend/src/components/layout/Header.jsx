import React from "react";
import { Box, Flex, Heading, Link, Container } from "@chakra-ui/react";
import { Link as RouterLink } from "react-router-dom";
import HeaderSearchBar from "components/ui/general/HeaderSearchBar";

/**
 * Header component that displays the main navigation bar of the application.
 * @component
 * @returns {JSX.Element} A header element containing the application title, navigation links, and search functionality
 *
 * @example
 * return (
 *   <Header />
 * )
 *
 * @description
 * The header includes:
 * - Application title "AnalyticQ SAST Scanner"
 * - Navigation links (Home, Contexts, Tools, Languages, About)
 * - Search bar component
 * - Responsive design for mobile and desktop views
 * - Themed with Chakra UI components
 */
export const Header = () => {
  const navItems = [
    { label: "Analyse", href: "/" },
    { label: "Contexts", href: "/contexts" },
    { label: "Tools", href: "/tools" },
    { label: "About", href: "/about" },
  ];

  return (
    <Box as="header" bg="blackAlpha.800" py={6} role="banner">
      <Container maxW="container.xl">
        <Flex
          align="center"
          justify="space-between"
          flexWrap={{ base: "wrap", md: "nowrap" }} // Stack items vertically on small screens, horizontally on large ones
        >
          <Flex
            align="center"
            mr={6}
            mb={{ base: 4, md: 0 }}
            width={{ base: "100%", md: "auto" }} // Make header full width on small screens
          >
            <Heading size="lg" fontWeight="bold" color="whiteAlpha.800" mr={6}>
              <Link
                key="home"
                as={RouterLink}
                to="/"
                mr={4}
                color="whiteAlpha.800"
                fontWeight="medium"
                _hover={{
                  border: "none",
                  textDecoration: "none",
                  color: "gray.100",
                }}
                _focus={{
                  border: "none",
                }}
                aria-label="Go to homepage"
              >
                AnalyticQ SAST Scanner
              </Link>
            </Heading>
            <Flex
              as="nav"
              align="center"
              _focus={{ border: "none" }}
              flexWrap={{ base: "wrap", md: "nowrap" }}
            >
              {navItems.map((item) => (
                <Link
                  key={item.href}
                  as={RouterLink}
                  to={item.href}
                  mr={{ base: 2, md: 4 }} // Adjust margin on smaller screens
                  color="whiteAlpha.800"
                  fontWeight="medium"
                  _hover={{
                    border: "none",
                    textDecoration: "none",
                    color: "gray.100",
                  }}
                  _focus={{
                    border: "none",
                  }}
                >
                  {item.label}
                </Link>
              ))}
            </Flex>
          </Flex>

          {/* Responsive search bar */}
          <Box
            width={{ base: "100%", md: "300px" }} // Make the search bar full width on small screens
            mt={{ base: 2, md: 0 }} // Adjust margin for mobile
          >
            <HeaderSearchBar />
          </Box>
        </Flex>
      </Container>
    </Box>
  );
};

Header.displayName = "Header";
