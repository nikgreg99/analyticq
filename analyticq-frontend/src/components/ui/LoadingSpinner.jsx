import React from "react";
import {
    Flex,
    Spinner
} from "@chakra-ui/react";

/**
 * A loading spinner component displayed in the center of its container.
 * @component
 * @returns {JSX.Element} A centered spinning loader with extra large size
 * @example
 * return (
 *   <LoadingSpinner />
 * )
 */
const LoadingSpinner = () => (
    <Flex
        justify="center"
        align="center"
        minH="200px"
        role="status"
        aria-live="polite"
    >
        <Spinner
            size="xl"
            color="colorPalette.600"
            aria-label="Loading content"
            data-testid="loading-spinner"
        />
    </Flex>
);

export default LoadingSpinner;
