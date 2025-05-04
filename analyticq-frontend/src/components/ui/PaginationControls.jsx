import React, { useMemo } from "react";
import {
    ButtonGroup,
    Flex,
    IconButton,
    Pagination,
    VStack,
    useBreakpointValue,
    Text
}
    from "@chakra-ui/react";
import { LuChevronLeft, LuChevronRight } from "react-icons/lu";
import { Tooltip } from "./Tooltip";
import { Box } from "lucide-react";

/**
 * A pagination control component that allows navigation through paginated content.
 *
 * @component
 * @param {Object} props - The component props
 * @param {number} props.total - The total number of items to paginate
 * @param {number} props.pageSize - The number of items to display per page
 * @param {number} props.currentPage - The current active page number
 * @param {Function} props.onPageChange - Callback function triggered when page is changed
 * @returns {JSX.Element} A pagination control component with previous/next buttons and page numbers
 */
const PaginationControls = ({ total, pageSize, currentPage, onPageChange, siblingCount = 1, showTooltip = true, showPageInfo = true }) => {

    const totalPages = useMemo(() => Math.ceil(total / pageSize), [total, pageSize]);
    const pageInfoText = useMemo(() => `Page ${currentPage} of ${totalPages}`, [currentPage, totalPages]);

    const compactMode = useBreakpointValue({ base: true, md: false });

    if (totalPages <= 1 || total === 0) return null;

    return (
        <VStack
            align="center"
            width="auto"
        >
            <Flex
                alignSelf="center"
                justifyContent="center"
                aria-label="Pagination Navigation"
            >
                <Pagination.Root
                    alignSelf="center"
                    count={total}
                    pageSize={pageSize}
                    defaultPage={currentPage}
                    onPageChange={(e) => onPageChange(e.page)}
                    siblingCount={compactMode ? 0 : siblingCount}
                >
                    <ButtonGroup
                        variant="surface"
                        size="sm"
                    >
                        <Pagination.PrevTrigger   asChild>
                            {showTooltip ? (
                                <Tooltip content="Previous Page">
                                    <IconButton
                                        size="sm"
                                        aria-label="Previous page"
                                        disabled={currentPage === 1}
                                    >
                                        <LuChevronLeft />
                                    </IconButton>
                                </Tooltip>
                            ) : (
                                <IconButton
                                    aria-label="Previous page"
                                    disabled={currentPage === 1}
                                    size="sm"
                                >
                                    <LuChevronLeft />
                                </IconButton>
                            )}
                        </Pagination.PrevTrigger>

                        <Pagination.Items
                            render={(page) => (
                                <IconButton
                                    key={`page-${page.value}`}
                                    size="sm"
                                    variant={page.selected ? "solid" : "subtle"}
                                    colorPalette={page.selected ? "blue" : "gray"}
                                    aria-current={page.selected ? "page" : undefined}
                                    aria-label={`Page ${page.value}`}
                                >
                                    {page.value}
                                </IconButton>
                            )}
                        />

                        <Pagination.NextTrigger asChild>
                            {showTooltip ? (
                                <Tooltip content="Next Page">
                                    <IconButton
                                        aria-label="Next page"
                                        size="sm"
                                        disabled={currentPage === totalPages}
                                    >
                                        <LuChevronRight />
                                    </IconButton>
                                </Tooltip>
                            ) : (
                                <IconButton
                                    aria-label="Next page"
                                    size="sm"
                                    disabled={currentPage === totalPages}
                                >
                                    <LuChevronRight />
                                </IconButton>
                            )}
                        </Pagination.NextTrigger>
                    </ButtonGroup>
                </Pagination.Root>
            </Flex>
            {showPageInfo && (
                <Text
                    fontSize="xs"
                    color="Highlight"
                    textAlign="center"
                    mt={2}
                >
                    {pageInfoText}
                </Text>
            )}
        </VStack>
    );
};

PaginationControls.displayName = "PaginationControls";

export default PaginationControls;
