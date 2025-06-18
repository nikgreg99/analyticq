import React, { useState, useEffect, useRef, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import { useDispatch } from "react-redux";
import { useDebounce } from "use-debounce";
import { useSavedItems } from "hooks";
import HeaderActionsBar from "./HeaderActionsBar";
import SearchBarDropdown from "./SearchBarDropdown";
import SearchInput from "./SearchInput";
// Chakra UI imports
import { Box, Flex } from "@chakra-ui/react";

import { MdHistory } from "react-icons/md";
import { FiStar } from "react-icons/fi";

// Services and utility imports
import { getContextByRepoName } from "services/contextService";
import { Toaster, toaster } from "components/ui/general/Toaster";
import { searchByRepoNamePrefix, setSearchQuery } from "redux/searchSlice";
import { useKeyboardShortcut } from "hooks/useKeyboardShotcut";
import { useClickOutside } from "hooks/useClickOutiside";

// Constants
const REPO_PATTERN = /^[a-zA-Z0-9_-]*$/;
const MIN_SEARCH_LENGTH = 3;
const MAX_HISTORY_ITEMS = 5;
const DEBOUNCE_DELAY = 300;
const STORAGE_KEYS = {
  HISTORY: "searchHistory",
  FAVORITES: "favorites",
};

// Toast configurations
const TOAST_CONFIGS = {
  error: {
    title: (query) => `Context ${query} was not found`,
    type: "error",
    placement: "top-end",
    max: 4,
  },
  favoriteAdded: {
    title: `Repository added to favorites`,
    type: "success",
    placement: "top-end",
    max: 4,
  },
  favoriteRemoved: {
    title: `Repository removed from favorites`,
    type: "info",
    placement: "top-end",
    max: 4,
  },
};

/**
 * Main HeaderSearchBar component
 */
const HeaderSearchBar = () => {
  // State management
  const [isValid, setIsValid] = useState(true);
  const [searchQuery, setSearchQueryState] = useState("");
  const [isSearching, setIsSearching] = useState(false);
  const [showHistory, setShowHistory] = useState(false);
  const [showFavorites, setShowFavorites] = useState(false);
  const [searchAttempted,setSearchAttempted] = useState(false);
  const [hasSearchResuls, setSearchResults] = useState(false);

  // Custom hooks
  const {
    items: searchHistory,
    addItem: addToHistory,
    removeItem: removeFromHistory,
    clearItems: clearHistory,
  } = useSavedItems(STORAGE_KEYS.HISTORY, MAX_HISTORY_ITEMS);

  const {
    items: favorites,
    addItem: addToFavorites,
    removeItem: removeFromFavorites,
    hasItem: isFavorite,
    clearItems: clearFavorites,
  } = useSavedItems(STORAGE_KEYS.FAVORITES);

  const isShortcutActive = useKeyboardShortcut("s", true);

  // Other hooks
  const navigate = useNavigate();
  const dispatch = useDispatch();
  const searchInputRef = useRef(null);
  const historyRef = useRef(null);
  const favoritesRef = useRef(null);
  const [debouncedSearchQuery] = useDebounce(searchQuery, DEBOUNCE_DELAY);

  // Handle clicks outside dropdowns
  useClickOutside([historyRef, searchInputRef], () => setShowHistory(false));

  useClickOutside([favoritesRef, searchInputRef], () =>
    setShowFavorites(false),
  );

  // Focus search input when shortcut is activated
  useEffect(() => {
    if (isShortcutActive) {
      searchInputRef.current?.focus();
    }
  }, [isShortcutActive]);

  // Validate search query
  useEffect(() => {
    const isValidRepo = !searchQuery || REPO_PATTERN.test(searchQuery);
    setIsValid(isValidRepo);

    if(searchQuery != "" && searchAttempted){
      setSearchAttempted(false);
    }

  }, [searchQuery, searchAttempted]);

  // Trigger search when debounced query changes
  useEffect(() => {
    if (debouncedSearchQuery.length >= MIN_SEARCH_LENGTH) {
      dispatch(searchByRepoNamePrefix(debouncedSearchQuery));
      setSearchResults(true);
    }
    else {
      setSearchResults(false);
    }
  }, [debouncedSearchQuery, dispatch]);

  const handleInputFocus = useCallback(() => {
    if(! searchQuery.trim() && searchHistory.length > 0){
      setShowHistory(true);
      setShowFavorites(false)
    }
  },[searchQuery, searchHistory.length])

  const handleInputBlur = useCallback(() => {
    setTimeout(() => {
      setShowHistory(false);
      setShowFavorites(false);
    }, 150);
  }, []);

  // Toggle favorite status
  const toggleFavorite = useCallback(
    (repo) => {
      if (isFavorite(repo)) {
        removeFromFavorites(repo);
        toaster.create(TOAST_CONFIGS.favoriteRemoved);
      } else {
        addToFavorites(repo);
        toaster.create(TOAST_CONFIGS.favoriteAdded);
      }
    },
    [isFavorite, removeFromFavorites, addToFavorites],
  );

  // Handle input change
  const handleInputChange = useCallback(
    (e) => {
      const value = e.target.value;
      setSearchQueryState(value);
      dispatch(setSearchQuery(value));

      if(value.trim() && (searchHistory.length > 0 || favorites.length > 0)){
          const matchingHistory = searchHistory.filter(item =>
            item.toLowerCase().includes(value.toLowerCase())
          );
          const matchingFavorites = favorites.filter(item =>
            item.toLowerCase().includes(value.toLowerCase())
          )

          if(matchingHistory.length > 0){
            setShowHistory(true);
            setShowFavorites(false);
          }
          else if(matchingFavorites.length > 0) {
            setShowFavorites(true);
            setShowHistory(false);
          }
      }

    },
    [dispatch, searchHistory, favorites],
  );

  // Clear search input
  const handleClearSearch = useCallback(() => {
    setSearchQueryState("");
    dispatch(setSearchQuery(""));
    setSearchAttempted(false);
    setSearchResults(false);
    setShowHistory(false);
    setShowFavorites(false);
    searchInputRef.current?.focus();
  }, [dispatch]);

  // Handle search submission
  const handleSearch = useCallback(
    async (e) => {
      if (e) e.preventDefault();

    setSearchAttempted(true);
      const trimmedQuery = searchQuery.trim();

      // Better validation with user feedback
      if (!trimmedQuery) {
        toaster.create(TOAST_CONFIGS.emptySearch);
        return;
      }

      if (trimmedQuery.length < MIN_SEARCH_LENGTH) {
        toaster.create(TOAST_CONFIGS.searchTooShort);
        return;
      }

      if(!isValid){
        toaster.create({
          title: "Invalid repository name",
          description: "Repository names can only contain letters, numbers, hyphens, and underscores",
          type: "error",
          duration: 3000
        });
        return;
      }

      setIsSearching(true);
      setShowHistory(false);
      setShowFavorites(false);


      try {
        const context = await getContextByRepoName(searchQuery);
        addToHistory(searchQuery);
        navigate(`/contexts/${context.id}`);
      } catch (error) {
        toaster.create({
          ...TOAST_CONFIGS.error,
          title: TOAST_CONFIGS.error.title(searchQuery),
        });
        console.error("Search error:", error);
      } finally {
        setIsSearching(false);
      }
    },
    [searchQuery, navigate, addToHistory, isValid],
  );

  // Handle selection from history or favorites
  const handleSelectItem = useCallback(
    async (item) => {
      setSearchQueryState(item);
      dispatch(setSearchQuery(item));
     setShowHistory(false);
      setShowFavorites(false);

      // Immediate search without setTimeout for better UX
      try {
        setIsSearching(true);
        const context = await getContextByRepoName(item);
        addToHistory(item);
        navigate(`/contexts/${context.id}`);
      } catch {
        toaster.create({
          ...TOAST_CONFIGS.error,
          title: TOAST_CONFIGS.error.title(item),
        });
      } finally {
        setIsSearching(false);
      }
    },
    [dispatch, addToHistory, navigate],
  );


  return (
    <Box position="relative" data-testid="header-search-bar">
      <Flex>
        <Box flex="1">
          <SearchInput
            searchQuery={searchQuery}
            isValid={isValid}
            isSearching={isSearching}
            showValidationErrors={true}
            inputRef={searchInputRef}
            onSearch={handleSearch}
            onChange={handleInputChange}
            onClear={handleClearSearch}
            onBlur={handleInputBlur}
            onFocus={handleInputFocus}
            showShortcutIndicator={isShortcutActive}
          />
        </Box>

        <HeaderActionsBar
          searchQuery={searchQuery}
          searchHistory={searchHistory}
          favorites={favorites}
          toggleFavorite={toggleFavorite}
          setShowHistory={setShowHistory}
          setShowFavorites={setShowFavorites}
          showHistory={showHistory}
          showFavorites={showFavorites}
        />
      </Flex>

      {/* History dropdown */}
      {showHistory && searchHistory.length > 0 && (
        <SearchBarDropdown
          ref={historyRef}
          title="Recent Searches"
          icon={MdHistory}
          items={searchHistory.filter(item =>
            !searchQuery.trim() ||
            item.toLowerCase().includes(searchQuery.toLowerCase())
          )}
          favorites={favorites}
          onSelect={handleSelectItem}
          onRemove={removeFromHistory}
          onToggleFavorite={toggleFavorite}
          onClearAll={clearHistory}
          role="listbox"
          aria-label="Search history suggestions"
        />
      )}

      {/* Favorites dropdown */}
      {showFavorites && favorites.length > 0 && (
        <SearchBarDropdown
          ref={favoritesRef}
          title="Favorite Repositories"
          icon={FiStar}
          items={favorites.filter(item =>
            !searchQuery.trim() ||
            item.toLowerCase().includes(searchQuery.toLowerCase())
          )}
          isFavoritesList={true}
          onSelect={handleSelectItem}
          onRemove={removeFromFavorites}
          onClearAll={clearFavorites}
          role="listbox"
          aria-label="Favorite repository suggestions"
        />
      )}

      <Toaster />
    </Box>
  );
};

HeaderSearchBar.displayName = "HeaderSearchBar";

export default React.memo(HeaderSearchBar);
