import React, { useState, useRef, useEffect } from "react";
import { Button, useClipboard } from "@chakra-ui/react";
import { FaCopy, FaCheck } from "react-icons/fa";
import { Tooltip } from "./Tooltip";
import { Toaster, toaster } from "./Toaster";

/**
 * A button component that copies text to clipboard with visual feedback
 * @component
 * @param {Object} props - Component props
 * @param {string} props.value - The text value to copy to clipboard
 * @param {('sm'|'md'|'lg')} [props.size='md'] - Size of the button
 * @param {string} [props.label='Copy'] - Tooltip text shown before copying
 * @param {string} [props.successMessage='Copied to clipboard!'] - Toast message shown after copying
 * @returns {JSX.Element} A button with copy functionality and visual feedback
 */
export const CopyButton = ({
  value,
  size = "md",
  label = "Copy",
  successMessage = "Copied to clipboard!",
}) => {
  const clipboard = useClipboard({ value });
  const [hasCopied, setHasCopied] = useState(false);
  const timeoutRef = useRef(null);

  const handleCopy = () => {
    if (!value) return;

    clipboard.copy();
    setHasCopied(true);

    toaster.create({
      title: successMessage,
      type: "success",
      duration: 2000,
      isClosable: true,
      position: "top",
    });

    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
    }

    timeoutRef.current = setTimeout(() => {
      setHasCopied(false);
    }, 1000);
  };

  useEffect(() => {
    return () => {
      if (timeoutRef.current) clearTimeout(timeoutRef.current);
    };
  }, []);

  return (
    <>
      <Tooltip content={hasCopied ? "Copied!" : label} showArrow>
        <Button
          aria-label={hasCopied ? "Copied!" : label}
          size={size}
          onClick={handleCopy}
          cursor="pointer"
          variant="ghost"
          _hover={{ bg: "gray.100" }}
          disabled={hasCopied}
        >
          {hasCopied ? <FaCheck color="green" /> : <FaCopy color="black" />}
        </Button>
      </Tooltip>
      <Toaster />
    </>
  );
};

CopyButton.displayName = "CopyButton";
