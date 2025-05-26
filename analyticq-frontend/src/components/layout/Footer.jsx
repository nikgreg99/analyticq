import React from "react";
import {
  Box,
  Container,
  Flex,
  Text,
  useBreakpointValue,
} from "@chakra-ui/react";

/**
 * Footer component that displays the copyright information at the bottom of the page
 * @component
 * @returns {JSX.Element} A footer element containing the copyright text
 */
export const Footer = () => {
  const textSize = useBreakpointValue({ base: "sm", md: "md" }); // Responsive text size
  const paddingY = useBreakpointValue({ base: "4", md: "6" }); // Responsive vertical padding
  const containerWidth = useBreakpointValue({ base: "100%", md: "1/3" }); // Responsive container width

  return (
    <Box
      as="footer"
      bg="blackAlpha.800"
      py={paddingY}
      role="contentinfo"
      aria-label="Footer"
    >
      <Container maxW={containerWidth}>
        <Flex justify="center" align="center" direction="column">
          <Text
            color="whiteAlpha.800"
            textAlign="center"
            fontWeight="medium"
            fontSize={textSize} // Responsive text size
            aria-label="Copyright"
          >
            © {new Date().getFullYear()} AnalyticQ Frontend. All rights
            reserved.
          </Text>
        </Flex>
      </Container>
    </Box>
  );
};

Footer.displayName = "Footer";
