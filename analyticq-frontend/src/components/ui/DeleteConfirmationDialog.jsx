import React from "react";
import {
    Box,
    Button,
    CloseButton,
    Dialog,
    Portal,
    Text
} from "@chakra-ui/react";
import { LuTrash2 } from "react-icons/lu";


/**
 * A reusable dialog component for confirming deletion actions.
 *
 * @component
 * @param {Object} props - The component props
 * @param {boolean} props.isOpenModal - Controls the visibility of the dialog
 * @param {function} props.setIsOpenModal - Function to update the dialog's visibility state
 * @param {string} props.itemName - Name or ID of the item to be deleted
 * @param {('context'|'scan' | 'issue')} [props.itemType='context'] - Type of item being deleted, affects dialog content
 * @param {boolean} props.isLoading - Loading state for delete action
 * @param {function} props.onConfirm - Callback function executed when deletion is confirmed
 * @param {React.RefObject} props.cancelRef - React ref for the cancel button
 *
 * @returns {JSX.Element} A modal dialog with delete confirmation message and actions
 */
const DeleteConfirmationDialog = ({
    isOpenModal,
    setIsOpenModal,
    itemName,
    itemType = "context",
    isLoading,
    onConfirm,
    cancelRef
}) => {

    const dialogConfig = {
        context: {
            title: `Deleting ${itemName} codebase?`,
            description: `Are you sure you want to delete "${itemName}"? This action cannot be undone.
                All associated scans and analysis data will also be removed.`,
            buttonText: "Delete Context"
        },
        scan: {
            title: `Deleting SAST scan?`,
            description: `Are you sure you want to delete this scan with ID "${itemName}"? This action cannot be undone.
                All findings and analysis data related to this scan will be permanently removed.`,
            buttonText: "Delete Scan"
        },
        issue: {
            title: `Deleting security issue?`,
            description: `Are you sure you want to delete this issue with ID "${itemName}"? This action cannot be undone.
                All related data for this security finding will be permanently removed.`,
            buttonText: "Delete Issue"
        }
    }

    const config = dialogConfig[itemType];

    return (<Dialog.Root
        role="alertdialog"
        lazyMount
        open={isOpenModal}
        onOpenChange={(e) => setIsOpenModal(e.open)}
        motionPreset="slide-in-bottom"
        aria-labelledby="delete-dialog-title"
        aria-describedby="delete-dialog-description"
    >
        <Dialog.Trigger asChild>
            <Button
                bg="blackAlpha.900"
                color="whiteAlpha.900"
                variant="solid"
                size="sm"
                loading={isLoading}
                loadingText="Deleting..."
            >
                <LuTrash2 />
                {config.buttonText}
            </Button>
        </Dialog.Trigger>
        <Portal>
            <Dialog.Positioner>
                <Dialog.Content>
                    <Dialog.Header
                        display="flex"
                        justifyContent="space-between"
                        alignItems="center"
                        pb={2}
                    >
                        <Dialog.Title
                            display="flex"
                            id="delete-dialog-title"
                            fontWeight="semibold"
                            fontSize="lg"
                        >
                            {config.title}
                        </Dialog.Title>
                    </Dialog.Header>
                    <Dialog.Body id="delete-dialog-description">
                        <Box
                            display="flex"
                            alignItems="center"
                            mb={3}
                        >
                            <Text>
                                {config.description}
                            </Text>
                        </Box>
                    </Dialog.Body>
                    <Dialog.Footer>
                        <Dialog.ActionTrigger asChild>
                            <Button
                                variant="solid"
                                colorPalette="green"
                                disabled={isLoading}
                            >
                                Cancel
                            </Button>
                        </Dialog.ActionTrigger>
                        <Button
                            variant="solid"
                            colorPalette="red"
                            loading={isLoading}
                            loadingText="Deleting..."
                            ref={cancelRef}
                            onClick={onConfirm}
                            mr={3}
                        >
                            <LuTrash2 />
                            Delete
                        </Button>
                    </Dialog.Footer>
                    <Dialog.CloseTrigger asChild>
                        <CloseButton
                            size="sm"
                            aria-label="Close delete confirmation"
                        />
                    </Dialog.CloseTrigger>
                </Dialog.Content>
            </Dialog.Positioner>
        </Portal>
    </Dialog.Root>
    );
};

export default DeleteConfirmationDialog;
