import React from 'react';
import {
  Box,
  Flex,
  Heading,
  Link,
  Container
} from '@chakra-ui/react';
import { Link as RouterLink } from 'react-router-dom';
import SearchBar from 'components/ui/HeaderSearchBar';

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
    { label: 'Analyse', href: '/' },
    { label: 'Contexts', href: '/contexts' },
    { label: 'Tools', href: '/tools' },
    { label: 'Languages', href: '/language-supported' },
    { label: 'About', href: '/about' },
  ];

  return (
    <Box as="header" bg="blackAlpha.800" py={6} >
      <Container maxW="container.xl">
        <Flex
          align="center"
          justify="space-between"
          flexWrap={{ base: "wrap", md: "nowrap" }}
        >
          <Flex
            align="center"
            mr={6}
            mb={{ base: 4, md: 0 }}
            width={{ base: "100%", md: "auto" }}
          >
            <Heading
              size="lg"
              fontWeight="bold"
              color="whiteAlpha.800"
              mr={6}
            >
              <Link
                key="home"
                as={RouterLink}
                to="/"
                mr={4}
                color="whiteAlpha.800"
                fontWeight="medium"
                _hover={{
                  border: "none",
                  textDecoration: 'none',
                  color: 'gray.100'
               }}
               _focus={{
                  border: "none"
               }}
              >
              AnalyticQ SAST Scanner
            </Link>
          </Heading>
          <Flex as="nav" align="center" _focus={{ border: "none" }}>
            {navItems.map((item) => (
              <Link
                key={item.href}
                as={RouterLink}
                to={item.href}
                mr={4}
                color="whiteAlpha.800"
                fontWeight="medium"
                _hover={{
                  border: "none",
                  textDecoration: 'none',
                  color: 'gray.100'
                }}
                _focus={{
                  border: "none"
                }}
              >
                {item.label}
              </Link>
            ))}
          </Flex>
        </Flex>

        <Box
          width={{ base: "100%", md: "300px" }}
          mt={{ base: 2, md: 0 }}
        >
          <SearchBar />
        </Box>
      </Flex>
    </Container>
    </Box >
  );
};
