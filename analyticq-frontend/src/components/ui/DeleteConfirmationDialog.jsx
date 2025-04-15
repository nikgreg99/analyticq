import React from "react";
import {
    Button,
    CloseButton,
    Dialog,
    Portal
} from "@chakra-ui/react";
import { LuTrash2 } from "react-icons/lu";

/**
 * A dialog component that confirms deletion of a repository context
 * @param {Object} props - The component props
 * @param {boolean} props.isOpenModal - Controls visibility of the dialog
 * @param {Function} props.setIsOpenModal - Callback to update modal's open state
 * @param {string} props.repoName - Name of the repository to be deleted
 * @param {boolean} props.isLoading - Loading state for the delete operation
 * @param {Function} props.onConfirm - Callback function triggered when deletion is confirmed
 * @param {React.RefObject} props.cancelRef - React ref for the cancel button
 * @returns {JSX.Element} A confirmation dialog for repository deletion
 */
const DeleteConfirmationDialog = ({
    isOpenModal,
    setIsOpenModal,
    repoName,
    isLoading,
    onConfirm,
    cancelRef
}) => (

    <Dialog.Root
        role="alertdialog"
        lazyMount
        open={isOpenModal}
        onOpenChange={(e) => setIsOpenModal(e.open)}
        motionPreset="slide-in-bottom"
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
                Delete Context
            </Button>
        </Dialog.Trigger>
        <Portal>
            <Dialog.Positioner>
                <Dialog.Content>
                    <Dialog.Header>
                        <Dialog.Title>Deleting {repoName} codebase...</Dialog.Title>
                    </Dialog.Header>
                    <Dialog.Body>
                        Are you sure you want to delete "{repoName}"? This action cannot be undone.
                        All associated scans and analysis data will also be removed.
                    </Dialog.Body>
                    <Dialog.Footer>
                        <Dialog.ActionTrigger asChild>
                            <Button
                                variant="solid"
                                colorPalette="green"
                            >
                                Cancel
                            </Button>
                        </Dialog.ActionTrigger>
                        <Button
                            variant="solid"
                            colorPalette="red"
                            ref={cancelRef}
                            onClick={onConfirm}
                        >
                            <LuTrash2 />
                            Delete
                        </Button>
                    </Dialog.Footer>
                    <Dialog.CloseTrigger asChild>
                        <CloseButton size="sm" />
                    </Dialog.CloseTrigger>
                </Dialog.Content>
            </Dialog.Positioner>
        </Portal>
    </Dialog.Root>
);

export default DeleteConfirmationDialog;
