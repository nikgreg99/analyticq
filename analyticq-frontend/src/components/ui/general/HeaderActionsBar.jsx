import React from "react";
import { Flex } from "@chakra-ui/react";
import { MdBookmark, MdBookmarkBorder, MdHistory } from "react-icons/md";
import { FiStar } from "react-icons/fi";
import { Tooltip } from "./Tooltip";

/**
 * Renders a header actions bar component with favorite and history functionality
 * @param {string} searchQuery - The current search query
 * @param {string[]} searchHistory - Array of previous search queries
 * @param {string[]} favorites - Array of favorited search queries
 * @param {(query: string) => void} toggleFavorite - Function to toggle favorite status of a query
 * @param {(show: boolean) => void} setShowHistory - Function to control search history visibility
 * @param {(show: boolean) => void} setShowFavorites - Function to control favorites visibility
 * @param {boolean} showHistory - Whether search history is currently visible
 * @param {boolean} showFavorites - Whether favorites are currently visible
 * @returns {JSX.Element} Header actions bar with favorite and history controls
 */
const HeaderActionsBar = ({
  searchQuery,
  searchHistory,
  favorites,
  toggleFavorite,
  setShowHistory,
  setShowFavorites,
  showHistory,
  showFavorites,
}) => {
  const MIN_SEARCH_LENGTH = 3;
  const isFavorite = favorites.includes(searchQuery);
  const showFavoriteButton =
    searchQuery && searchQuery.length >= MIN_SEARCH_LENGTH;

  return (
    <Flex alignItems="center" ml={2}>
      {showFavoriteButton && (
        <Tooltip
          content={isFavorite ? "Remove from favorites" : "Add to favorites"}
          showArrow
        >
          {isFavorite ? (
            <MdBookmark
              color="gold"
              aria-label="Remove from favorites"
              onClick={() => toggleFavorite(searchQuery)}
              mr={1}
              cursor="pointer"
            />
          ) : (
            <MdBookmarkBorder
              aria-label="Add to favorites"
              onClick={() => toggleFavorite(searchQuery)}
              mr={1}
              cursor="pointer"
            />
          )}
        </Tooltip>
      )}

      {searchHistory.length > 0 && (
        <MdHistory
          aria-label="Search history"
          onClick={() => {
            setShowFavorites(false);
            setShowHistory(!showHistory);
          }}
          cursor="pointer"
          mr={1}
        />
      )}

      {favorites.length > 0 && (
        <FiStar
          aria-label="Favorite repositories"
          onClick={() => {
            setShowHistory(false);
            setShowFavorites(!showFavorites);
          }}
          cursor="pointer"
        />
      )}
    </Flex>
  );
};

HeaderActionsBar.displayName = "HeaderActionsBar";

export default React.memo(HeaderActionsBar);
