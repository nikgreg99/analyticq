import React, { useState } from "react";
import { InputGroup, Input, Field, Text, Spinner, Box, Flex } from "@chakra-ui/react";
import { IoIosSearch, IoIosClose, IoMdKeypad } from "react-icons/io";
import { Tooltip } from "./Tooltip";

/**
 * A search input component with validation, loading state, and keyboard shortcuts.
 *
 * @component
 * @param {Object} props - The component props
 * @param {string} props.searchQuery - The current search query value
 * @param {boolean} props.isValid - Whether the current search query is valid
 * @param {boolean} props.isSearching - Whether a search is currently in progress
 * @param {boolean} props.showValidationErrors - Whether to show validation error messages
 * @param {React.RefObject} props.inputRef - Ref object for the input element
 * @param {Function} props.onSearch - Callback fired when search is triggered
 * @param {Function} props.onChange - Callback fired when input value changes
 * @param {Function} props.onClear - Callback fired when clear button is clicked
 * @param {boolean} props.showShortcutIndicator - Whether to show the keyboard shortcut indicator
 * @returns {JSX.Element} A search input field with validation and loading states
 */
const SearchInput = ({
  searchQuery,
  isValid,
  isSearching,
  showValidationErrors,
  inputRef,
  onSearch,
  onChange,
  onClear,
  showShortcutIndicator,
}) => {
  const MIN_SEARCH_LENGTH = 3;
  const [isFocused, setIsFocused] = useState(false);
  const [attemptedSubmit, setAttemptedSubmit] = useState(false);

  // Only show validation messages when appropriate
  const shouldShowLengthError =
    showValidationErrors &&
    searchQuery &&
    searchQuery.length < MIN_SEARCH_LENGTH &&
    (attemptedSubmit || (!isFocused && searchQuery.length > 0));

  const shouldShowPatternError =
    showValidationErrors &&
    !isValid &&
    searchQuery &&
    (attemptedSubmit || !isFocused);

  const handleSearch = (e) => {
    if (e) e.preventDefault();
    setAttemptedSubmit(true);
    onSearch(e);
  };

  return (
    <Box position="relative">
      <Field.Root onSubmit={handleSearch}>
        <InputGroup
          startElement={
            <Tooltip content="Press Alt+S to focus search" showArrow>
              <span style={{ pointerEvents: "auto" }}>
                <IoMdKeypad
                  color={showShortcutIndicator ? "blue.300" : "gray.400"}
                  opacity={showShortcutIndicator ? 1 : 0.7}
                  onClick={() => inputRef.current?.focus()}
                  aria-label="Keyboard shortcut for search"
                  cursor="pointer"
                />
              </span>
            </Tooltip>
          }
          endElement={
            <Flex alignItems="center" height="100%">
              {isSearching ? (
                <Spinner size="sm" />
              ) : (
                <IoIosSearch
                  onClick={
                    searchQuery.length >= MIN_SEARCH_LENGTH ? handleSearch : undefined
                  }
                  cursor={
                    searchQuery.length >= MIN_SEARCH_LENGTH
                      ? "pointer"
                      : "default"
                  }
                  aria-label="Search"
                  size={20}
                />
              )}

              {searchQuery && (
                <IoIosClose
                  aria-label="Clear search"
                  onClick={onClear}
                  mr={1}
                  cursor="pointer"
                  size={20}
                />
              )}
            </Flex>
          }
        >
          <Input
            ref={inputRef}
            placeholder="Search repositories..."
            value={searchQuery}
            onChange={onChange}
            onKeyDown={(e) => e.key === "Enter" && handleSearch(e)}
            onFocus={() => setIsFocused(true)}
            onBlur={() => setIsFocused(false)}
            border="1px"
            borderColor={shouldShowPatternError || shouldShowLengthError ? "red.400" : "gray.600"}
            borderRadius="md"
            bg="whiteAlpha.100"
            color="white"
            _placeholder={{ color: "gray.400" }}
            _hover={{ borderColor: shouldShowPatternError || shouldShowLengthError ? "red.400" : "gray.500" }}
            _focus={{ borderColor: "blue.300", boxShadow: "none" }}
            disabled={isSearching}
            aria-label="Search repository"
            transition="all 0.2s"
            height="40px"
          />
        </InputGroup>

        {(shouldShowPatternError || shouldShowLengthError) && (
          <Box
            position="absolute"
            width="100%"
            top="100%"
            left="0"
            zIndex="1"
            mt={1}
          >
            {shouldShowPatternError && (
              <Text color="red.400" fontSize="xs" bg="gray.800" p={1} borderRadius="sm">
                Repo name can contain letters, numbers, hyphens, and underscores
              </Text>
            )}

            {shouldShowLengthError && (
              <Text color="red.400" fontSize="xs" bg="gray.800" p={1} borderRadius="sm">
                Please enter at least {MIN_SEARCH_LENGTH} characters to search
              </Text>
            )}
          </Box>
        )}
      </Field.Root>
    </Box>
  );
};

SearchInput.displayName = "SearchInput";

export default React.memo(SearchInput);
