import React from "react";
import { Button } from "@chakra-ui/react";
import { LuArrowLeft } from "react-icons/lu";

/**
 * A reusable back button component with an arrow icon
 * @component
 * @param {Object} props - The component props
 * @param {Function} props.onClick - Callback function to be called when the button is clicked
 * @param {string} [props.label="Back"] - The text label for the button, defaults to "Back"
 * @returns {JSX.Element} A button component with an arrow icon and label
 */
const BackButton = ({ onClick, label = "Back" }) => (
  <Button
    bg="blackAlpha.900"
    color="whiteAlpha.900"
    variant="solid"
    size="sm"
    onClick={onClick}
    aria-label={label}
  >
    <LuArrowLeft />
    {label}
  </Button>
);

BackButton.displayName = "BackButton";

export default BackButton;
