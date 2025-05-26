"use client";

import { ChakraProvider, defaultSystem } from "@chakra-ui/react";
import { ColorModeProvider } from "./ColorMode";

/**
 * A wrapper component that provides Chakra UI theme and color mode context to its children.
 * This component combines ChakraProvider and ColorModeProvider to enable styling and theming.
 *
 * @component
 * @param {Object} props - The props to be passed to the ColorModeProvider
 * @returns {JSX.Element} A provider component that wraps its children with Chakra UI context
 *
 * @example
 * <Provider>
 *   <App />
 * </Provider>
 */
export function Provider(props) {
  return (
    <ChakraProvider value={defaultSystem}>
      <ColorModeProvider {...props} />
    </ChakraProvider>
  );
}
