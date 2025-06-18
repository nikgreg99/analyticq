import React from "react";
import {
    Box,
    HStack,
    Text,
    Icon
} from "@chakra-ui/react";


/**
 * A component that displays an item with an icon, label, and description in a vertical layout.
 *
 * @component
 * @param {object} props - The component props
 * @param {React.ReactNode} props.icon - The icon element to display
 * @param {string} props.label - The label text to display
 * @param {string} props.description - The description text to display
 * @returns {JSX.Element} A Box component containing the icon, label and description
 */
export const UsageItem = ({ icon, label, description }) => (
  <Box>
    <HStack spacing={2} mb={1} role="img" aria-label={label}>
      {React.isValidElement(icon) ? icon : <Icon as={icon} color="blackAlpha.800"/>}
      <Text fontWeight="medium" color="gray.700">
        {label}
      </Text>
    </HStack>
    <Text fontSize="sm" color="gray.600" ml={6}>
      {description}
    </Text>
  </Box>
);
