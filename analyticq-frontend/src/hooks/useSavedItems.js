import { useState, useEffect, useCallback } from "react";

/**
 * A custom hook for managing a list of items in localStorage with automatic saving and loading.
 *
 * @param {string} storageKey - The key used to store/retrieve items in localStorage
 * @param {number} [maxItems=Infinity] - Maximum number of items to store (oldest items are removed when limit is reached)
 *
 * @returns {Object} An object containing:
 *   @property {Array} items - The current list of stored items
 *   @property {function(item: *): void} addItem - Adds an item to the beginning of the list
 *   @property {function(item: *): void} removeItem - Removes an item from the list
 *   @property {function(item: *): boolean} hasItem - Checks if an item exists in the list
 *   @property {function(): void} clearItems - Removes all items from the list and localStorage
 *
 * @throws {Error} If localStorage operations fail during save/load
 *
 * @example
 * const { items, addItem, removeItem, hasItem, clearItems } = useSavedItems('myItems', 10);
 */
export function useSavedItems(storageKey, maxItems = Infinity) {
  const [items, setItems] = useState([]);

  useEffect(() => {
    const savedItems = localStorage.getItem(storageKey);
    if (savedItems) {
      try {
        setItems(JSON.parse(savedItems));
      } catch (e) {
        console.error(`Error loading ${storageKey}:`, e);
        localStorage.removeItem(storageKey);
      }
    }
  }, [storageKey]);

  /**
   * Saves items to local storage.
   * @param {Array|Object} newItems - The items to be saved in localStorage
   * @throws {Error} If localStorage is not available or if JSON serialization fails
   * @function
   */
  const saveItems = useCallback(
    (newItems) => {
      try {
        localStorage.setItem(storageKey, JSON.stringify(newItems));
      } catch (e) {
        console.error(`Error saving to ${storageKey}:`, e);
      }
    },
    [storageKey],
  );

  /**
   * Adds a new item to the list while maintaining uniqueness and max length.
   * If the item already exists (case-insensitive), it's moved to the front.
   * New items are added at the beginning of the list.
   *
   * @param {string} item - The item to be added to the list
   * @callback
   * @returns {void}
   *
   * @example
   * addItem("newItem");
   */
  const addItem = useCallback(
    (item) => {
      setItems((prevItems) => {
        const filteredItems = prevItems.filter(
          (i) => i.toLowerCase() !== item.toLowerCase(),
        );
        const newItems = [item, ...filteredItems].slice(0, maxItems);
        saveItems(newItems);
        return newItems;
      });
    },
    [maxItems, saveItems],
  );

  /**
   * Removes a specific item from the items state and persists the changes.
   *
   * @param {*} item - The item to be removed from the items array
   * @returns {void}
   */
  const removeItem = useCallback(
    (item) => {
      setItems((prevItems) => {
        const newItems = prevItems.filter((i) => i !== item);
        saveItems(newItems);
        return newItems;
      });
    },
    [saveItems],
  );

  /**
   * Checks if a specific item exists in the items array.
   * @param {*} item - The item to check for existence in the array.
   * @returns {boolean} True if the item exists in the array, false otherwise.
   * @memberof hooks/items
   */
  const hasItem = useCallback((item) => items.includes(item), [items]);

  /**
   * Clears all items from both the state and local storage.
   * @function clearItems
   * @returns {void}
   */
  const clearItems = useCallback(() => {
    setItems([]);
    localStorage.removeItem(storageKey);
  }, [storageKey]);

  return { items, addItem, removeItem, hasItem, clearItems };
}
