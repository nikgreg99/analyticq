import React, { useState, useEffect, useRef } from 'react';
import {
  Box,
  Input,
  InputGroup,
  Field,
  Text,
  Spinner,
  VStack,
  Flex,
  Icon
} from '@chakra-ui/react';
import { IoIosSearch, IoIosClose, IoMdKeypad, IoMdTrash } from "react-icons/io";
import { MdHistory } from "react-icons/md";
import { FiX } from 'react-icons/fi';
import { useNavigate } from 'react-router-dom';
import { getContextByRepoName } from 'services/contextService';
import { Toaster, toaster } from "components/ui/Toaster";
import { Tooltip } from './Tooltip';
import { useDispatch } from 'react-redux';
import { searchByRepoNamePrefix, setSearchQuery } from 'redux/searchSlice';
import { useDebounce } from 'use-debounce';


/**
 * A search bar component that allows users to search for repositories.
 * The component includes real-time validation, debounced search, and error handling.
 *
 * @component
 * @example
 * return (
 *   <SearchBar />
 * )
 *
 * @description
 * Features:
 * - Real-time validation for repository name format
 * - Minimum 3 characters required for search
 * - Debounced search functionality (300ms)
 * - Loading state during search
 * - Error handling with toast notifications
 * - Keyboard support (Enter key) for search submission
 *
 * @returns {JSX.Element} A search bar component with validation and error messages
 */
const HeaderSearchBar = () => {

  const [isValid, setIsValid] = useState(false);
  const [searchQuery, setSearchQueryState] = useState('');
  const [isSearching, setIsSearching] = useState(false);
  const [isShortcutActive, , setIsShortcutActive] = useState(false);
  const [searchHistory, setSearchHistory] = useState([]);
  const [showHistory, setShowHistory] = useState(false);
  const navigate = useNavigate();
  const dispatch = useDispatch();
  const searchInputRef = useRef(null);
  const historyRef = useRef(null);

  const [debouncedSearchQuery] = useDebounce(searchQuery, 300);

  const errorToast = {
    title: `Context ${searchQuery} was not found`,
    type: "error",
    placement: "top-end",
    max: 4,
  };

  useEffect(() => {
    const savedHistory = localStorage.getItem('searchHistory');
    if (savedHistory) {
      try {
        setSearchHistory(JSON.parse(savedHistory));
      }
      catch (e) {
        console.error('Error loading search history:', e);
        localStorage.removeItem('searchHistory');
      }
    }
  }, []);

  useEffect(() => {
    const handleKeyDown = (e) => {
      if (e.altKey && e.key === 's') {
        e.preventDefault();
        searchInputRef.current?.focus();

        setIsShortcutActive(true);
        setTimeout(() => setIsShortcutActive(false), 2000);
      }
    };

    document.addEventListener('keydown', handleKeyDown)

    return () => {
      document.removeEventListener('keydown', handleKeyDown);
    }
  }, [setIsShortcutActive]);

  useEffect(() => {
    const handleClickOutside = (e) => {
      if (
        historyRef.current &&
        !historyRef.current.contains(e.target) &&
        !searchInputRef.current.contains(e.target)
      ) {
        setShowHistory(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    }
  }, [])


  useEffect(() => {
    const REPO_PATTERN = /^[a-zA-Z0-9_-]*$/;
    const isValidRepo = debouncedSearchQuery === '' || REPO_PATTERN.test(debouncedSearchQuery);
    setIsValid(isValidRepo);
  }, [debouncedSearchQuery]);

  // Handle input change - update both local state and Redux state
  const handleInputChange = (e) => {
    const value = e.target.value;
    setSearchQueryState(value);
    // Update the Redux store with the search query
    dispatch(setSearchQuery(value));
  };

  // Dispatch search action when the debounced search query changes
  useEffect(() => {
    if (debouncedSearchQuery.length >= 3) {
      dispatch(searchByRepoNamePrefix(debouncedSearchQuery));
    }
  }, [debouncedSearchQuery, dispatch]);

  const updateSearchHistory = (searchQuery) => {
    const updatedHistory = [...searchHistory];
    const existingIndex = updatedHistory.findIndex(item =>
      item.toLowerCase() === searchQuery.toLowerCase);

    if (existingIndex !== -1) {
      updatedHistory.splice(existingIndex, 1);
    }

    updatedHistory.unshift(searchQuery);
    const trimmedHistory = updatedHistory.slice(0, 5); // Keep only the last 5 searches
    setSearchHistory(trimmedHistory);
    saveHistoryToStorage(trimmedHistory);
  }

  const saveHistoryToStorage = (history) => {
    try {
      localStorage.setItem('searchHistory', JSON.stringify(history));
    }
    catch (e) {
      console.error('Error saving search history:', e);
    }
  };

  const removeHistoryItem = (event, index) => {
    event.stopPropagation();

    const updatedHistory = [...searchHistory];
    updatedHistory.splice(index, 1);
    setSearchHistory(updatedHistory);
    saveHistoryToStorage(updatedHistory);
  }

  const clearAllHistory = () => {
    setSearchHistory([]);
    localStorage.removeItem('searchHistory');
    setShowHistory(false);
  }

  const selectHistoryItem = (item) => {
    setSearchQueryState(item);
    dispatch(setSearchQuery(item));
    setShowHistory(false);
    setTimeout(() => {
      handleSearch()
    }, 100);
  }


  // Handle search submission
  const handleSearch = async (e) => {

    if (e) e.preventDefault();

    if (searchQuery.length < 3) return;
    if (!searchQuery.trim()) return;

    setIsSearching(true);
    setShowHistory(false);

    try {
      const context = await getContextByRepoName(searchQuery);

      updateSearchHistory(searchQuery);

      navigate(`/contexts/${context.id}`);
    }
    catch (error) {
      toaster.create(errorToast);
      console.log('Search error:', error);
    }
    finally {
      setIsSearching(false);
    }
  };

  const handleClearSearch = () => {
    setSearchQueryState('');
    dispatch(setSearchQuery(''));
    // Optional: focus the input after clearing
    searchInputRef.current?.focus();
  };

  return (
    <Box position="relative">
      <Field.Root onSubmit={handleSearch}>
        <InputGroup
          startElement={
            <Tooltip
              content="Press Alt+S to focus search"
              showArrow
            >
              <span style={{ pointerEvents: "auto" }}>
                <IoMdKeypad
                  color={isShortcutActive ? "blue.300" : "gray.400"}
                  opacity={isShortcutActive ? 1 : 0.7}
                  onClick={() => searchInputRef.current?.focus()}
                  aria-label="Keyboard shortcut for search"
                  cursor="pointer"
                />
              </span>
            </Tooltip>
          }
          endElement={
            <>
              {isSearching ? <Spinner size="sm" /> :
                <IoIosSearch
                  onClick={searchQuery.length >= 3 ? handleSearch : undefined}
                  cursor="pointer"
                  aria-label="Search"
                />
              }
              {searchQuery && (
                <IoIosClose
                  aria-label="Clear search"
                  onClick={handleClearSearch}
                  mr={1}
                  cursor="pointer"
                />
              )}
              {searchHistory.length > 0 && (
                <MdHistory
                  aria-label="Search history"
                  onClick={() => setShowHistory(!showHistory)}
                  cursor="pointer"
                />
              )}
            </>
          }>

          <Input
            ref={searchInputRef}
            placeholder="Search..."
            value={searchQuery}
            onChange={handleInputChange}
            onKeyDown={(e) => {
              if (e.key === 'Enter') {
                handleSearch(e);
              }
            }}
            onFocus={() => {
              if (searchHistory.length > 0) {
                setShowHistory(true);
              }
            }}
            border="1px"
            borderColor={isValid ? "gray.600" : "red.400"}
            borderRadius="md"
            bg="whiteAlpha.100"
            color="white"
            _placeholder={{ color: 'gray.400' }}
            _hover={{ borderColor: isValid ? "gray.500" : "red.400" }}
            _focus={{
              borderColor: 'blue.300',
              boxShadow: 'none'
            }}
            disabled={isSearching}
            aria-label='Search repository'
            transition="all 0.2s"
          />

        </InputGroup>
      </Field.Root>

      {showHistory && searchHistory.length > 0 && (
        <Box
          ref={historyRef}
          position="absolute"
          top="auto"
          left="0"
          righ="0"
          mt={1}
          zIndex="10"
          boxShadow="md"
          borderRadius="md"
          maxH="200px"
          overflowY="auto"
          bg="blackAlpha.800"
        >
          <VStack align="stretch">
            <Flex
              align="center"
              px={3}
              py={2}
              borderColor="gray.600"
            >
              <MdHistory />
              <Text ml={2}mr={2} fontWeight="medium" color="whiteAlpha.800">Recent Searches</Text>
              <IoMdTrash onClick={clearAllHistory} />
            </Flex>
            {searchHistory.length > 0 ? (
              searchHistory.map((item, index) => (
                <Flex
                  key={index}
                  px={3}
                  py={2}
                  cursor="pointer"
                  _hover={{ bg: "gray.600" }}
                  onClick={() => selectHistoryItem(item)}
                  borderBottom={index < searchHistory.length - 1 ? "1px" : "none"}
                  borderColor="gray.600"
                  alignContent="center"
                >
                  <Text
                    fontSize="small"
                    color="whiteAlpha.800"
                    flex="1"
                    onClick={() => selectHistoryItem(item)}
                  >
                    {item}
                  </Text>
                  <Icon
                    aria-label={`Remove ${item} from history`}
                    icon={<FiX />}
                    cursor="pointer"
                    size="xs"
                    onClick={(e) => removeHistoryItem(e, index)}
                  >
                    <FiX/>
                  </Icon>
                </Flex>
              ))
            ) : (
              <Box px={3} py={2}>
                <Text fontSize="sm" color="gray.400">No recent searches</Text>
              </Box>
            )}
          </VStack>
        </Box>
      )}

      {
        !isValid && searchQuery !== '' && (
          <Text color="red.400" fontSize="2xs" mt={0.5}>
            Repo name can contain letters, numbers, hyphens and underscores
          </Text>
        )
      }

      {
        searchQuery.length < 3 && searchQuery !== '' && (
          <Text color="red.400" fontSize="2xs" mt={0.5}>
            Please enter at least 3 characters to search
          </Text>
        )
      }

      <Toaster />
    </Box >
  );
};

export default HeaderSearchBar;
