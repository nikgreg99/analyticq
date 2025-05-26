import { Flex, Button } from "@chakra-ui/react";
import { ChartNoAxesColumnIncreasing } from "lucide-react";
import DeleteConfirmationDialog from "components/ui/general/DeleteConfirmationDialog";

/**
 * Component that renders action buttons for context details.
 *
 * @component
 * @param {Object} props - Component props
 * @param {string} props.repoName - Name of the repository
 * @param {boolean} props.isOpenModal - Controls visibility of delete confirmation modal
 * @param {function} props.setIsOpenModal - Function to toggle modal visibility
 * @param {boolean} props.isLoading - Loading state for delete operation
 * @param {function} props.onConfirm - Callback function when delete is confirmed
 * @param {React.RefObject} props.cancelRef - React ref for cancel button
 * @param {function} props.onStatsClick - Callback function when stats button is clicked
 * @returns {JSX.Element} A flex container with statistics and delete buttons
 */
const ContextDetailActions = ({
  repoName,
  isOpenModal,
  setIsOpenModal,
  isLoading,
  onConfirm,
  cancelRef,
  onStatsClick,
}) => (
  <Flex
    mt={10}
    direction={{ base: "column", sm: "row" }}
    justify="flex-end"
    align="center"
    wrap="wrap"
    gap={4}
  >
    <Button
      onClick={onStatsClick}
      bg="blackAlpha.900"
      color="whiteAlpha.900"
      variant="solid"
      size="sm"
    >
      <ChartNoAxesColumnIncreasing size={18} />
      View Statistics
    </Button>

    <DeleteConfirmationDialog
      isOpenModal={isOpenModal}
      setIsOpenModal={setIsOpenModal}
      itemName={repoName}
      isLoading={isLoading}
      onConfirm={onConfirm}
      cancelRef={cancelRef}
    />
  </Flex>
);

ContextDetailActions.displayName = "ContextDetailActions";

export default ContextDetailActions;
