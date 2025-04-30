import React from 'react';
import {
    Flex,
    Box,
    Container
} from '@chakra-ui/react';
import {Header} from './Header';
import {Footer} from './Footer';

export const MainLayout = ({children}) => (
    <Flex
        direction="column"
        minH="100vh"
        bg="gray.200"
    >
        <Header/>
        <Container
            as="main"
            maxW="container.xl"
            flex={1}
            py={4}
            px={4}
            role='main'
            aria-label='Main content area'
        >
            {children}
        </Container>
        <Footer/>
    </Flex>
)
