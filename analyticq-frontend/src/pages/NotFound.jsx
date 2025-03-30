import React from "react";
import {
    Heading,
    Text,
    VStack,
    Button
  } from '@chakra-ui/react';
  import { Link as RouterLink } from 'react-router-dom';

  export const NotFoundPage = () => {
    return (
        <VStack spacing={6}
                textAlign="center"
                py={20}>
            <Heading
                size="3xl"
                color="gray.500"
                fontWeight="bold"
            >
                404
            </Heading>
            <Heading size="lg" color="gray.700">
                Oops! Page Not Found
            </Heading>
            <Text
                color="gray.600"
                maxW="md">
                The page you are looking for might be not exists. Try another path or click below
                to return home.
            </Text>
            <Button
                marginTop="3em"
                as={RouterLink}
                to="/"
                colorScheme="blue"
                size="sm"
                px={2}
                py={2}
                _hover={{ boxShadow: "1g"}}
            >
                Go  Home
            </Button>
        </VStack>
    );
  };
