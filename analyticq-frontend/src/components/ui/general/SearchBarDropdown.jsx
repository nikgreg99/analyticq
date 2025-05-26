import React from "react";
import { Box, Flex, Text, VStack } from "@chakra-ui/react";
import { FiX } from "react-icons/fi";
import { MdBookmark, MdBookmarkBorder } from "react-icons/md";

/**
 * A dropdown component for displaying searchable items with favorites functionality
 * @component
 * @param {Object} props - Component props
 * @param {string} props.title - The title displayed at the top of the dropdown
 * @param {React.ComponentType} props.icon - Icon component to display next to the title
 * @param {string[]} props.items - Array of items to display in the dropdown
 * @param {boolean} [props.isFavoritesList=false] - Whether this dropdown displays favorites
 * @param {string[]} [props.favorites=[]] - Array of favorited items
 * @param {Function} props.onSelect - Callback fired when an item is selected
 * @param {Function} props.onRemove - Callback fired when an item is removed
 * @param {Function} [props.onToggleFavorite] - Callback fired when favorite status is toggled
 * @param {Function} props.onClearAll - Callback fired when clear all button is clicked
 * @param {React.Ref} ref - Forwarded ref
 * @returns {JSX.Element} The SearchBarDropdown component
 */
const SearchBarDropdown = React.memo(
  React.forwardRef(
    (
      {
        title,
        icon,
        items,
        isFavoritesList = false,
        favorites = [],
        onSelect,
        onRemove,
        onToggleFavorite,
        onClearAll,
      },
      ref,
    ) => {
      const Icon = icon;

      return (
        <Box
          ref={ref}
          position="absolute"
          top="auto"
          left="0"
          right="0"
          mt={1}
          zIndex="10"
          boxShadow="md"
          borderRadius="md"
          maxH="200px"
          overflowY="auto"
          bg="blackAlpha.800"
          data-testid={
            isFavoritesList ? "favorites-dropdown" : "history-dropdown"
          }
        >
          <VStack align="stretch">
            <Flex align="center" px={3} py={2} borderColor="gray.600">
              <Icon color={isFavoritesList ? "gold" : undefined} />
              <Text ml={2} mr={2} fontWeight="medium" color="whiteAlpha.800">
                {title}
              </Text>
              <FiX
                onClick={onClearAll}
                cursor="pointer"
                aria-label={`Clear all ${isFavoritesList ? "favorites" : "history"}`}
              />
            </Flex>

            {items.map((item, index) => (
              <Flex
                key={index}
                px={3}
                py={2}
                cursor="pointer"
                _hover={{ bg: "gray.600" }}
                onClick={() => onSelect(item)}
                borderBottom={index < items.length - 1 ? "1px" : "none"}
                borderColor="gray.600"
                alignItems="center"
                role="button"
                aria-label={`Select ${item}`}
              >
                <Text fontSize="small" color="whiteAlpha.800" flex="1">
                  {item}
                </Text>

                {!isFavoritesList &&
                  onToggleFavorite &&
                  (favorites.includes(item) ? (
                    <MdBookmark
                      color="gold"
                      aria-label={`Remove ${item} from favorites`}
                      onClick={(e) => {
                        e.stopPropagation();
                        onToggleFavorite(item);
                      }}
                      cursor="pointer"
                      mr={2}
                      size={16}
                    />
                  ) : (
                    <MdBookmarkBorder
                      aria-label={`Add ${item} to favorites`}
                      onClick={(e) => {
                        e.stopPropagation();
                        onToggleFavorite(item);
                      }}
                      cursor="pointer"
                      mr={2}
                      size={16}
                    />
                  ))}

                <FiX
                  aria-label={`Remove ${item} from ${isFavoritesList ? "favorites" : "history"}`}
                  cursor="pointer"
                  onClick={(e) => {
                    e.stopPropagation();
                    onRemove(item);
                  }}
                />
              </Flex>
            ))}
          </VStack>
        </Box>
      );
    },
  ),
);

SearchBarDropdown.displayName = "SearchBarDropdown";

export default SearchBarDropdown;
