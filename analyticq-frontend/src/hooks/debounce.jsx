import React, { useState, useEffect} from 'react';

/**
 * A custom React hook that returns a debounced value after a specified delay.
 * Useful for delaying state updates and preventing excessive re-renders.
 *
 * @param {any} value - The value to be debounced
 * @param {number} delay - The delay time in milliseconds before updating the debounced value
 * @returns {any} The debounced value that updates after the specified delay
 *
 * @example
 * const [searchTerm, setSearchTerm] = useState('');
 * const debouncedSearchTerm = useDebounce(searchTerm, 500);
 */
export function useDebounce(value, delay) {
    const [debouncedValue, setDebouncedValue] = useState(value);

    useEffect(() => {
      const handler = setTimeout(() => {
        setDebouncedValue(value);
      }, delay);

      return () => {
        clearTimeout(handler);
      };
    }, [value, delay]);

    return debouncedValue;
  }
