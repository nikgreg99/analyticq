import React, { useState, useEffect } from 'react';
import {
  Box,
  Input,
  InputGroup,
  Field,
  Text
} from '@chakra-ui/react';
import { IoIosSearch } from "react-icons/io";
import { useNavigate } from 'react-router-dom';
import { getContextByRepoName } from 'services/contextService';
import { Toaster, toaster } from "components/ui/toaster";
import { useDispatch} from 'react-redux';
import { searchByRepoNamePrefix } from 'redux/searchSlice';
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
const SearchBar = () => {

  const [isValid, setIsValid] = useState(false);
  const [searchQuery, setSearchQueryState] = useState('');
  const [isSearching, setIsSearching] = useState(false);
  const navigate = useNavigate();
  const dispatch = useDispatch();

  const [debouncedSearchQuery] = useDebounce(searchQuery, 300);

  const errorToast = {
    title: `Context ${searchQuery} was not found`,
    type: "error",
    placement: "top-end",
    max: 4,
  }

  useEffect(() => {
    const REPO_PATTERN = /^[a-zA-Z0-9_-]*$/;
    const isValidRepo = debouncedSearchQuery === '' || REPO_PATTERN.test(debouncedSearchQuery);
    setIsValid(isValidRepo);
  }, [debouncedSearchQuery]);

  // Dispatch action when the debounced search query changes
  useEffect(() => {
    if (debouncedSearchQuery.length >= 3) {
      dispatch(searchByRepoNamePrefix(debouncedSearchQuery));
    }
  }, [debouncedSearchQuery, dispatch]);

  const handleSearch = async (e) => {
    e.preventDefault();

    if (searchQuery.length < 3) return;

    if (!searchQuery.trim()) return;

    setIsSearching(true);

    try {
      const context = await getContextByRepoName(searchQuery);
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

  return (
    <Box position="relative">
      <Field.Root onSubmit={handleSearch}>
        <InputGroup endElement={<IoIosSearch
          onClick={searchQuery.length > 3 ? handleSearch : undefined}
          cursor="pointer"
        />}>
          <Input
            placeholder="Search..."
            value={searchQuery}
            onChange={(e) => {
              setSearchQueryState(e.target.value)
            }}
            onKeyDown={(e) => {
              if (e.key == 'Enter') {
                console.log(e.key);
                handleSearch(e);
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
          />
        </InputGroup>
      </Field.Root>

      {!isValid && searchQuery !== '' && (
        <Text color="red.400" fontSize="2xs" mt={0.5}>
          Repo name can contain letters, numbers, hyphens and underscores
        </Text>
      )}

      {/* Validation for search length */}
      {searchQuery.length < 3 && searchQuery !== '' && (
        <Text color="red.400" fontSize="2xs" mt={0.5}>
          Please enter at least 3 characters to search
        </Text>
      )}

      <Toaster />
    </Box>
  );
};

export default SearchBar;
