import React, { useState, useMemo } from "react";
import {
  Box,
  Flex,
  Select,
  Portal,
  Text,
  VStack,
  VisuallyHidden,
  Field,
  Input,
  Button,
  HStack
} from "@chakra-ui/react";
import { DEFAULT_PAGE_SIZE_OPTIONS } from "components/utils/pagination";
import { Rows3, ChevronDown } from "lucide-react";
import PaginationControls from "../general/PaginationControls";

export const PaginationFooter = ({
  totalItems,
  pageSize,
  setPageSize,
  currentPage,
  setCurrentPage,
  pageSizeOptions = DEFAULT_PAGE_SIZE_OPTIONS,
  ariaLabel = "Pagination Navigation",
  responsive = false,
  showTotalItems = true,
  showQuickJump = true,
  quickJumpPlaceholder = "Go to page..."
}) => {
  const [jumpToPage, setJumpToPage] = useState("");
  const [jumpErrorMessage, setJumpErrorMessage] = useState("");

  const totalPages = useMemo(() => {
    return Math.max(1, Math.ceil(totalItems / parseInt(pageSize[0], 10)));
  }, [totalItems, pageSize]);

  const startItem = Math.min(totalItems, (currentPage - 1) * parseInt(pageSize[0], 10) + 1);
  const endItem = Math.min(totalItems, currentPage * parseInt(pageSize[0], 10));

  const handleQuickJump = (e) => {
    e?.preventDefault();
    const pageNum = parseInt(jumpToPage, 10);

    if (isNaN(pageNum)) {
      setJumpErrorMessage("Please enter a valid number");
    } else if (pageNum < 1) {
      setJumpErrorMessage(`Page must be at least 1`);
    } else if (pageNum > totalPages) {
      setJumpErrorMessage(`Page ${pageNum} not available. Maximum page is ${totalPages}`);
    } else {
      setCurrentPage(pageNum);
      setJumpToPage("");
      setJumpErrorMessage("");
    }
  };

  const handleJumpInputChange = (e) => {
    setJumpToPage(e.target.value);
    if (jumpErrorMessage) {
      setJumpErrorMessage("");
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter') {
      handleQuickJump(e);
    }
  };

  const handlePageSizeChange = (value) => {
    setPageSize(value);
    const firstItemIndex = (currentPage - 1) * parseInt(pageSize[0], 10);
    const newPage = Math.floor(firstItemIndex / parseInt(value, 10)) + 1;
    setCurrentPage(Math.min(newPage, Math.ceil(totalItems / parseInt(value, 10))));
  };

  return (
    <Flex
      direction={responsive ? { base: "column", md: "row" } : "row"}
      justify="space-between"
      align="center"
      w="100%"
      gap={4}
      py={2}
      aria-label={ariaLabel}
      role="navigation"
    >
      {/* Left side: Page size selector and total items */}
      <Box
        display="flex"
        alignItems="center"
        flex={responsive ? { base: "1", md: "0 0 auto" } : "0 0 auto"}
      >
        <Box position="relative">
          <VisuallyHidden id="rowsPerPageLabel">Rows per page</VisuallyHidden>
          <Select.Root
            size="sm"
            value={pageSize}
            onValueChange={(e) => handlePageSizeChange(e.value)}
            collection={pageSizeOptions}
            variant="subtle"
            width={responsive ? { base: "100%", md: "150px" } : "150px"}
          >
            <Select.HiddenSelect />
            <Select.Control>
              <Select.Trigger data-testid="page-size-select">
                <Rows3 size={14} style={{ marginRight: 6 }} aria-hidden="true" />
                <Select.ValueText placeholder="Select rows per page" />
              </Select.Trigger>
              <Select.IndicatorGroup>
                <Select.Indicator>
                  <ChevronDown size={14} aria-hidden="true" />
                </Select.Indicator>
              </Select.IndicatorGroup>
            </Select.Control>
            <Portal>
              <Select.Positioner>
                <Select.Content>
                  {pageSizeOptions.items.map((item) => (
                    <Select.Item item={item} key={item.value}>
                      {item.label}
                      <Select.ItemIndicator />
                    </Select.Item>
                  ))}
                </Select.Content>
              </Select.Positioner>
            </Portal>
          </Select.Root>
        </Box>

        {showTotalItems && (
          <Text
            fontSize="sm"
            color="gray.600"
            ml={2}
            display={{ base: "none", md: "block" }}
            aria-live="polite"
          >
            {totalItems > 0 ?
              `Showing ${startItem}-${endItem} of ${totalItems} items` :
              'No items'}
          </Text>
        )}
      </Box>

      {/* Right side: Pagination controls with quick jump below */}
      {totalPages > 1 && (
        <VStack
          spacing={2}
          align={responsive ? { base: "center", md: "flex-end" } : "flex-end"}
          flex={responsive ? { base: "1", md: "0 0 auto" } : "0 0 auto"}
          width={responsive ? { base: "100%", md: "auto" } : "auto"}
        >
          {/* Pagination Controls */}
          <Box
            display="flex"
            alignItems="center"
            gap={2}
          >
            <PaginationControls
              total={totalItems}
              pageSize={pageSize[0]}
              currentPage={currentPage}
              onPageChange={setCurrentPage}
              showPageInfo={false}
            />
            <Text
              fontSize="sm"
              color="gray.600"
              minWidth="100px"
              textAlign="center"
              aria-live="polite"
              data-testid="pagination-info"
            >
              Page {currentPage} of {totalPages}
            </Text>
          </Box>

          {showQuickJump && (
            <Box
              as="form"
              onSubmit={handleQuickJump}
              width="100%"
              display="flex"
              flexDirection="column"
              alignItems="center"
            >
              <HStack spacing={2} align="center">
                <Text fontSize="sm" color="gray.600" whiteSpace="nowrap">
                  Go to:
                </Text>
                <Field.Root invalid={!!jumpErrorMessage} width="120px" mb={0}>
                  <Input
                    placeholder={quickJumpPlaceholder}
                    size="sm"
                    width="auto"
                    color="blackAlpha.600"
                    value={jumpToPage}
                    onChange={handleJumpInputChange}
                    onKeyDown={handleKeyDown}
                    aria-label="Jump to page"
                    data-testid="quick-jump-input"
                    borderRadius="md"
                    textAlign="center"
                  />
                </Field.Root>
              </HStack>
              {jumpErrorMessage && (
                <Field.ErrorText textAlign="center" fontSize="xs" mt={1}>
                  {jumpErrorMessage}
                </Field.ErrorText>
              )}
            </Box>
          )}
        </VStack>
      )}
    </Flex>
  );
};
