import React from "react";
import {
    Container,
    Heading,
    VStack,
    Text
} from "@chakra-ui/react";
import { IssueCard}  from "components/ui/IssueCard";

export const IssuesPage =  () => {

    const issues = [];

    return (
        <Container
            maxW="container.xl"
            py={10}
        >
            <VStack
                spacing={6}
                align="stretch"
            >
                <Heading
                    as="h1"
                    size="xl"
                    textAlign="center"
                >
                    Security Issues detected
                </Heading>
                {issues.length === 0 ? (
                    <Text>
                        No security issues detected.
                    </Text>
                ) : (
                    <VStack width="full" spacing={6}>
                        {issues.map(issue => {
                            <IssueCard key={issue.id} issue={issues}/>
                        })}
                    </VStack>
                )}
            </VStack>
        </Container>
    );

};
