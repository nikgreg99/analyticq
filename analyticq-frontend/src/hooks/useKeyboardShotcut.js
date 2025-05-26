import { useState, useEffect } from "react";

/**
 * A custom hook that detects keyboard shortcuts with optional modifier keys.
 * @param {string} key - The main key to detect (e.g., 'a', 'Enter', etc.)
 * @param {boolean} [altKey=false] - Whether the Alt key should be pressed
 * @param {boolean} [ctrlKey=false] - Whether the Control key should be pressed
 * @param {boolean} [shiftKey=false] - Whether the Shift key should be pressed
 * @returns {boolean} A boolean indicating if the keyboard shortcut is currently active
 *
 * @example
 * const isShortcutActive = useKeyboardShortcut('s', false, true); // Ctrl + S
 * // Use isShortcutActive in your component
 */
export function useKeyboardShortcut(
  key,
  altKey = false,
  ctrlKey = false,
  shiftKey = false,
) {
  const [isActive, setIsActive] = useState(false);

  useEffect(() => {
    const handleKeyDown = (e) => {
      if (
        e.key === key &&
        e.altKey === altKey &&
        e.ctrlKey === ctrlKey &&
        e.shiftKey === shiftKey
      ) {
        e.preventDefault();
        setIsActive(true);
        setTimeout(() => setIsActive(false), 2000);
        return true;
      }
      return false;
    };

    document.addEventListener("keydown", handleKeyDown);
    return () => document.removeEventListener("keydown", handleKeyDown);
  }, [key, altKey, ctrlKey, shiftKey]);

  return isActive;
}
