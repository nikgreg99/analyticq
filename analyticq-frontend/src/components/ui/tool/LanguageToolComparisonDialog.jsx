import React from "react";
import {
  Button,
  Box,
  CloseButton,
  Dialog,
  Portal,
  Text,
  Table,
  Badge,
  Flex,
  Heading,
} from "@chakra-ui/react";
import { MdCompareArrows } from "react-icons/md";
import { IoMdClose } from "react-icons/io";
import { formatLanguageName } from "components/utils/strings";

/**
 * A modal dialog component for comparing SAST tools across multiple programming languages.
 *
 * @component
 * @param {Object} props - The component props
 * @param {boolean} props.isOpen - Controls the visibility of the dialog
 * @param {function} props.onClose - Function to close the dialog
 * @param {Array<Object>} props.selectedLanguages - Array of selected language objects to compare
 * @param {Array<Object>} props.comparisonData - Processed data showing tool support across languages
 *
 * @returns {JSX.Element} A modal dialog displaying tool comparison data across languages
 */
const LanguageToolComparisonDialog = ({
  isOpen,
  setIsOpenModal,
  selectedLanguages,
  comparisonData,
}) => {
  if (!selectedLanguages || selectedLanguages.length === 0) {
    return null;
  }

  return (
    <Dialog.Root
      role="dialog"
      lazyMount
      open={isOpen}
      onOpenChange={(e) => setIsOpenModal(e.open)}
      motionPreset="slide-in-bottom"
      size="xl"
      aria-labelledby="comparison-dialog-title"
      aria-describedby="comparison-dialog-description"
    >
      <Portal>
        <Dialog.Backdrop />
        <Dialog.Positioner>
          <Dialog.Content maxWidth="800px" width="100%">
            <Dialog.Header
              display="flex"
              justifyContent="space-between"
              alignItems="center"
              pb={2}
              borderBottomWidth="1px"
              borderColor="gray.200"
            >
              <Dialog.Title
                display="flex"
                alignItems="center"
                gap={2}
                id="comparison-dialog-title"
                fontWeight="semibold"
                fontSize="xl"
              >
                <MdCompareArrows />
                SAST Tool Comparison
              </Dialog.Title>
            </Dialog.Header>
            <Dialog.Body id="comparison-dialog-description" py={4}>
              <Box mb={4}>
                <Heading size="sm" mb={2}>
                  Selected Languages
                </Heading>
                <Flex gap={2} wrap="wrap">
                  {selectedLanguages.map((lang) => (
                    <Badge
                      key={lang.name}
                      colorScheme="blue"
                      py={1}
                      px={2}
                      borderRadius="full"
                    >
                      {lang.name}
                    </Badge>
                  ))}
                </Flex>
              </Box>

              <Box mt={6}>
                <Heading size="sm" mb={3}>
                  Tools Comparison
                </Heading>
                {comparisonData.length > 0 ? (
                  <Table.Root variant="line" size="md">
                    <Table.Header>
                      <Table.Row>
                        <Table.ColumnHeader>Tool</Table.ColumnHeader>
                        <Table.ColumnHeader>
                          Languages Supported
                        </Table.ColumnHeader>
                        <Table.ColumnHeader numeric>
                          Coverage
                        </Table.ColumnHeader>
                      </Table.Row>
                    </Table.Header>
                    <Table.Body>
                      {comparisonData.map((item) => (
                        <Table.Row key={item.tool}>
                          <Table.Cell fontWeight="medium">
                            {formatLanguageName(item.tool)}
                          </Table.Cell>
                          <Table.Cell>
                            {item.supportedLanguages?.length > 0 ? (
                              <Flex wrap="wrap" gap={1}>
                                {item.supportedLanguages.map((lang) => (
                                  <Badge
                                    key={lang}
                                    colorScheme="blue"
                                    variant="subtle"
                                  >
                                    {lang}
                                  </Badge>
                                ))}
                              </Flex>
                            ) : (
                              <Text fontSize="sm" color="gray.500">
                                None
                              </Text>
                            )}
                          </Table.Cell>
                          <Table.Cell numeric>
                            <Badge
                              colorScheme={
                                item.supportCount === selectedLanguages.length
                                  ? "green"
                                  : "blue"
                              }
                              variant="solid"
                            >
                              {Math.round(
                                (item.supportCount / selectedLanguages.length) *
                                  100,
                              )}
                              %
                            </Badge>
                          </Table.Cell>
                        </Table.Row>
                      ))}
                    </Table.Body>
                  </Table.Root>
                ) : (
                  <Box py={4} textAlign="center">
                    <Text color="gray.500">
                      No common tools found across the selected languages
                    </Text>
                  </Box>
                )}
              </Box>
            </Dialog.Body>
            <Dialog.Footer>
              <Flex justify="flex-end" width="100%">
                <Button onClick={() => setIsOpenModal(!isOpen)}>
                  Close
                  <IoMdClose />
                </Button>
              </Flex>
            </Dialog.Footer>
            <Dialog.CloseTrigger asChild>
              <CloseButton size="sm" aria-label="Close comparison" />
            </Dialog.CloseTrigger>
          </Dialog.Content>
        </Dialog.Positioner>
      </Portal>
    </Dialog.Root>
  );
};

LanguageToolComparisonDialog.displayName = "LanguageToolComparisonDialog";

export default LanguageToolComparisonDialog;
