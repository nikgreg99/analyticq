
import React from 'react';
import {
  Box,
  Flex,
  Heading,
  Link,
  Container
} from '@chakra-ui/react';
import { Link as RouterLink } from 'react-router-dom';

export const Header = () => {
  const navItems = [
    { label: 'Home', href: '/' },
    { label: 'About', href: '/about' }
  ];

  return (
    <Box as="header" bg="blackAlpha.800" py={6} >
      <Container maxW="container.xl">
        <Flex align="center">
          <Flex align="center" mr={6}>
            <Heading
              size="lg"
              fontWeight="bold"
              color="whiteAlpha.800"
              mr={6}
            >
              AnalyticQ SAST Scanner
            </Heading>
            <Flex as="nav" align="center"  _focus={{border: "none"}}>
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
        </Flex>
      </Container>
    </Box>
  );
};
