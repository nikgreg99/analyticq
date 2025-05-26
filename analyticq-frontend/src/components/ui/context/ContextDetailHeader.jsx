import { Flex, Heading } from "@chakra-ui/react";

/**
 * Renders the header section for the context detail view
 * @component
 * @param {Object} props - The component props
 * @param {string|number} props.contextId - The unique identifier for the context/codebase
 * @returns {JSX.Element} A flex container with a heading displaying the context ID
 */
const ContextDetailHeader = ({ contextId }) => (
  <Flex
    direction={{ base: "column", md: "row" }}
    justify="space-between"
    align={{ base: "flex-start", md: "center" }}
    mb={6}
    gap={4}
  >
    <Heading id="context-detail-heading" size="lg" color="blackAlpha.800">
      Codebase #{contextId} Details
    </Heading>
  </Flex>
);

ContextDetailHeader.displayName = "ContextDetailHeader";

export default ContextDetailHeader;
