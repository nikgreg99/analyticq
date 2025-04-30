import React, { useEffect} from "react";
import {
    Heading,
    Text,
    VStack,
    Button
  } from '@chakra-ui/react';
  import { Link as RouterLink } from 'react-router-dom';
  import { FaHome } from "react-icons/fa";
  import { updatePageMetadata } from 'components/utils/metadata';

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
        updatePageMetadata(
            "Page not found",
            "Page not found. Try again",
            "/404"
        );
    });


    return (
        <VStack spacing={6}
                textAlign="center"
                py={20}
                role="main"
                aria-labelledby="404 Not Found Page"
        >
            <Heading
                as="p"
                size="3xl"
                color="gray.500"
                fontWeight="bold"
                aria-hidden="true"
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
                colorPalette="black"
                variant="subtle"
                size="sm"
                px={2}
                py={2}
                _hover={{ boxShadow: "1g"}}
                aria-label="Go to Home Page"
            >
                <FaHome/>
                Go to Home Page
            </Button>
        </VStack>
    );
  };
