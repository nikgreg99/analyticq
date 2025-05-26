import { useState, useEffect } from "react";

/**
 * A custom React hook that calculates the optimal number of characters that can fit in a line
 * based on the current window width.
 *
 * The calculation considers:
 * - 90% of the window width as the maximum available width
 * - An average character width of 8 pixels
 * - A padding of 32 pixels
 *
 * The hook automatically updates the estimate when the window is resized.
 *
 * @returns {number} The estimated optimal number of characters that can fit in one line
 */
export const useOptimalCharEstimate = () => {
  const [optimalChars, setOptimalChars] = useState(80);

  useEffect(() => {
    const updateEstimate = () => {
      const maxWidth = window.innerWidth * 0.9;
      const avgCharWidth = 8;
      const padding = 32;
      setOptimalChars(Math.floor((maxWidth - padding) / avgCharWidth));
    };

    updateEstimate(); // initial estimate
    window.addEventListener("resize", updateEstimate);
    return () => window.removeEventListener("resize", updateEstimate);
  }, []);

  return optimalChars;
};
