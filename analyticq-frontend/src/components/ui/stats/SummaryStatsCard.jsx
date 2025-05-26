import React, { memo } from "react";
import { Tooltip } from "../general/Tooltip";
import { Box, Flex, Text, Icon, Card, HStack } from "@chakra-ui/react";

/**
 * A card component that displays summary statistics with an icon, title, and value.
 *
 * @component
 * @param {Object} props - The component props
 * @param {string} props.title - The title text to display
 * @param {string|number} props.value - The value to display
 * @param {IconType} props.icon - The icon component to render
 * @param {string} [props.colorScheme="gray"] - The color scheme for the card background
 * @returns {JSX.Element} A card displaying summary statistics
 */
export const SummaryStatsCard = memo(
  ({ title, value, icon, colorScheme = "gray" }) => {
    return (
      <Card.Root
        bg={`${colorScheme}.500`}
        borderRadius="lg"
        boxShadow="md"
        role="region"
        aria-labelledby={`${title}-label`}
        aria-describedby={`${title}-value`}
      >
        <Card.Body>
          <Flex align="center">
            <HStack p={2} borderRadius="md" mr={4}>
              <Icon
                as={icon}
                boxSize={6}
                color="blackAlpha.800"
                aria-hidden="true"
              />
              <Box ml={2}>
                <Text
                  id={`${title}-label`}
                  fontSize={{ base: "sm", md: "md" }}
                  fontWeight="bold"
                  color="blackAlpha.800"
                >
                  {title}
                </Text>
                <Tooltip content={`Total ${title.toLowerCase()}`} showArrow>
                  <Text
                    id={`${title}-value`}
                    fontSize="sm"
                    fontWeight="bold"
                    color="blackAlpha.800"
                  >
                    {value}
                  </Text>
                </Tooltip>
              </Box>
            </HStack>
          </Flex>
        </Card.Body>
      </Card.Root>
    );
  },
);
