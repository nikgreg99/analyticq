import React from "react";
import {
    ButtonGroup,
    IconButton,
    Pagination }
from "@chakra-ui/react";
import { LuChevronLeft, LuChevronRight } from "react-icons/lu";

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
const PaginationControls = ({ total, pageSize, currentPage, onPageChange }) => {
    return (
        <Pagination.Root
            alignSelf="center"
            count={total}
            pageSize={pageSize}
            defaultPage={currentPage}
            onPageChange={(e) => onPageChange(e.page)}
        >
            <ButtonGroup>
                <Pagination.PrevTrigger asChild>
                    <IconButton>
                        <LuChevronLeft/>
                    </IconButton>
                </Pagination.PrevTrigger>

                <Pagination.Items
                    render={(page) => (
                        <IconButton>
                            {page.value}
                        </IconButton>
                    )}
                />

                <Pagination.NextTrigger asChild>
                    <IconButton>
                        <LuChevronRight/>
                    </IconButton>
                </Pagination.NextTrigger>
            </ButtonGroup>
        </Pagination.Root>
    );
};

export default PaginationControls;
