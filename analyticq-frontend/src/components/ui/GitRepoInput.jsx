import React, { useState, useEffect, useCallback } from "react";
import {
  VStack,
  Select,
  Input,
  createListCollection,
  Portal,
  Box,
  Flex,
  Icon,
  Grid,
  Text,
  InputGroup
} from '@chakra-ui/react';
import {
  FormControl,
  FormLabel,
  FormErrorMessage,
  FormHelperText
} from "@chakra-ui/form-control";
import { FiLink, FiGitBranch, FiCode, FiInfo } from "react-icons/fi";
import { Tooltip } from "./Tooltip";

/**
 * A component that provides inputs for Git repository URL and branch selection.
 *
 * @component
 * @param {Object} props - The component props
 * @param {function} props.onUrlChange - Callback function triggered when repository URL changes
 * @param {function} props.onBranchChange - Callback function triggered when branch selection changes
 *
 * @returns {JSX.Element} A form with repository URL input and branch selection dropdown
 *
 * @example
 * <GitRepoInput
 *   onUrlChange={(url) => console.log(url)}
 *   onBranchChange={(branch) => console.log(branch)}
 * />
 *
 * @description
 * The component provides:
 * - Repository URL input with validation for GitHub, GitLab, and Bitbucket URLs
 * - Branch selection dropdown with common options (main, master, dev)
 * - Custom branch input option with validation
 * - Real-time validation and error messaging
 * - Character count for custom branch names
 */
export const GitRepoInput = ({
  onUrlChange,
  onBranchChange
}) => {

  const [selectedBranch, setSelectedBranch] = useState(["main"]);
  const [url, setUrl] = useState('');
  const [isUrlValid, setIsUrlValid] = useState(false);
  const [urlError, setUrlError] = useState('');
  const [customBranch, setCustomBranch] = useState('');
  const [branchError, setBranchError] = useState('');

  const MAX_BRANCH_NAME_LENGTH = 255; // Git's maximum branch name length

  const validateUrl = useCallback((inputUrl) => {
    const GIT_URL_REGEX = /^(https?:\/\/)?(www\.)?(github\.com|gitlab\.com|bitbucket\.org)\/([\w-]+)\/([\w-]+)(\.git)?$/;
    const trimmedUrl = inputUrl.trim().toLowerCase();

    // Check if URL is empty
    if (!trimmedUrl) {
      setUrlError('Repository URL is required');
      setIsUrlValid(false);
      return false;
    }

    // Check URL format
    if (!GIT_URL_REGEX.test(trimmedUrl)) {
      setUrlError('Please enter a valid repository URL');
      console.log(urlError);
      setIsUrlValid(false);
      return false;
    }

    // Prevent duplicate slashes in URL
    if (trimmedUrl.includes("//github.com//") || trimmedUrl.includes("//gitlab.com//")) {
      setUrlError("Invalid URL: contains duplicate slashes");
      setIsUrlValid(false);
      return false;
    }

    setUrlError('');
    setIsUrlValid(true);
    return true;
  }, [urlError]);

  const validateBranchName = useCallback((branchName) => {
    const BRANCH_NAME_REGEX = /^(?!\/|\.|-)[a-zA-Z0-9._-]+(?<!\/|\.|-)$/;
    const MIN_BRANCH_NAME_LENGTH = 1;
    const trimmedBranch = branchName.trim();

    if (!trimmedBranch) {
      setBranchError('Branch name is required');
      return false;
    }

    if (!BRANCH_NAME_REGEX.test(trimmedBranch)) {
      setBranchError('Invalid branch name. Use letters, numbers, dots, hyphens, and underscores only.');
      return false;
    }

    if (trimmedBranch.length < MIN_BRANCH_NAME_LENGTH) {
      setBranchError(`Branch name must be at least ${MIN_BRANCH_NAME_LENGTH} character long`);
      return false;
    }

    if (trimmedBranch.length > MAX_BRANCH_NAME_LENGTH) {
      setBranchError(`Branch name cannot exceed ${MAX_BRANCH_NAME_LENGTH} characters`);
      return false;
    }

    // Prevent reserved branch names like HEAD
    if (trimmedBranch.toLowerCase() === 'head') {
      setBranchError('Branch name cannot be "HEAD"');
      return false;
    }

    setBranchError('');
    return true;
  }, []);

  const normalizeGitUrl = (url) => {
    return url.trim().replace(/\.git$/, '');
  };

  const handleUrlChange = (value) => {
    const normalizedUrl = normalizeGitUrl(value);
    setUrl(value); // Keep the original input value for user experience

    if (validateUrl(normalizedUrl)) {
      onUrlChange(normalizedUrl); // Pass the normalized URL to the parent component
    }
  };

  const handleBranchChange = (value) => {
    console.log("Selected branch", value[0]);
    setSelectedBranch(value);
    setBranchError("");

    if (value[0] !== "other") {
      onBranchChange(value[0]);
    }
  };

  const handleCustomBranchChange = (value) => {
    console.log("Selected custom branch: ", value);
    setCustomBranch(value);

    // Only validate and trigger onBranchChange if 'other' is selected
    if (selectedBranch[0] === "other") {
      const isValid = validateBranchName(value);
      console.log("Branch name valid ? :", isValid);
      if (isValid) {
        onBranchChange(value);
      }
    }
  };

  const branchOptions = createListCollection({
    items: [
      { label: "main", value: "main" },
      { label: "master", value: "master" },
      { label: "dev", value: "dev" },
      { label: "Other", value: "other" }
    ],
  });

  useEffect(() => {
    console.log(selectedBranch, customBranch);
    if (selectedBranch[0] === "other" && customBranch) {
      console.log("Validating custom branch name");
      console.log("Validating branch name:", validateBranchName(customBranch));
    }
  }, [customBranch, selectedBranch, validateBranchName]);

  return (
    <VStack
      spacing={4}
      align="stretch"
      p={4}
      borderRadius="md"
      boxShadow="md"
      borderWidth="1px"
      borderColor="blackAlpha.200"
      aria-labelledby="git-repo-input-title"
      role="group"
    >
      <Text id="git-repo-input-title" srOnly>Git Repository Configuration</Text>
      <FormControl isInvalid={!!urlError}>
        <Grid templateColumns={{ base: '1fr', md: '150px 1fr' }} gap={4} alignItems="center">
          <FormLabel
            display="flex"
            alignItems="center"
            mb={0}
            color="blackAlpha.800"
            fontWeight="semibold"
            htmlFor="repository-url"
          >
            <Icon as={FiLink} mr={2} w={5} h={5} color="black" aria-hidden="true" />
            <Text color="blackAlpha.800">Repository URL</Text>
          </FormLabel>
          <Box>
            <Input
              placeholder="https://github.com/username/repository"
              value={url}
              size="md"
              borderColor={urlError ? "crimson" : "blackAlpha.800"}
              color="blackAlpha.800"
              onChange={(e) => handleUrlChange(e.target.value)}
              aria-describedby={urlError ? "url-error" : "url-helper-text"}
              aria-invalid={!!urlError}
            />
            <FormErrorMessage id="url-error" mt={1} fontSize="smaller" color="crimson">
              {urlError}
            </FormErrorMessage>
            <FormHelperText id="url-helper-text" mt={1} fontSize="smaller" color="black">
              The .git extension is optional.
            </FormHelperText>
            <Tooltip
              content="Example: https://github.com/username/repository"
              placement="top"
              hasArrow
            >
              <Box position="absolute" right="10px" top="10px" cursor="pointer">
                <Icon as={FiInfo} color="gray.500" />
              </Box>
            </Tooltip>
          </Box>
        </Grid>
      </FormControl>

      {isUrlValid && (
        <FormControl isInvalid={!!branchError}>
          <Grid templateColumns={{ base: '1fr', md: '150px 1fr' }} gap={4} alignItems="center">
            <FormLabel
              display="flex"
              alignItems="center"
              mb={0}
              color="blackAlpha.800"
              fontWeight="semibold"
              htmlFor="branch-select"
            >
              <Icon as={FiGitBranch} mr={2} w={5} h={5} color="black" aria-hidden="true" />
              <Text color="blackAlpha.800">Branch</Text>
            </FormLabel>
            <Box>
              <Select.Root
                collection={branchOptions}
                value={selectedBranch}
                onValueChange={(e) => handleBranchChange(e.value)}
                defaultValue={["main"]}
                id="branch-select"
              >
                <Select.HiddenSelect />
                <Select.Control>
                  <Select.Trigger width="full" aria-label="Branch selection">
                    <Select.ValueText
                      placeholder="Select branch"
                      color="blackAlpha.800"
                    />
                    <Select.Indicator />
                  </Select.Trigger>
                </Select.Control>
                <Portal>
                  <Select.Positioner>
                    <Select.Content>
                      {branchOptions.items.map((branch) => (
                        <Select.Item
                          item={branch}
                          key={branch.value}
                          _hover={{ bg: 'blackAlpha.50' }}
                        >
                          <Flex align="center">
                            {branch.value === "other" ? (
                              <Icon as={FiCode} mr={2} w={4} h={4} aria-hidden="true" />
                            ) : (
                              <Icon as={FiGitBranch} mr={2} w={4} h={4} aria-hidden="true" />
                            )}
                            {branch.label}
                          </Flex>
                        </Select.Item>
                      ))}
                    </Select.Content>
                  </Select.Positioner>
                </Portal>
              </Select.Root>

              {selectedBranch[0] === "other" && (
                <Box mt={3}>
                  <InputGroup
                    endElement={<FiCode color="black" />}
                  >
                    <Input
                      id="custom-branch"
                      pl={8}
                      placeholder="Enter custom branch name"
                      value={customBranch}
                      size="md"
                      focusBorderColor="blackAlpha.800"
                      borderColor={branchError ? "crimson" : "blackAlpha.800"}
                      color="blackAlpha.800"
                      onChange={(e) => handleCustomBranchChange(e.target.value)}
                      maxLength={MAX_BRANCH_NAME_LENGTH}
                      aria-describedby={branchError ? "branch-error" : "branch-char-count"}
                      aria-invalid={!!branchError}
                    />
                  </InputGroup>
                  <Box position="absolute" left="10px" top="10px">
                    <Icon as={FiCode} color="black" aria-hidden="true" />
                  </Box>
                  <Flex justify="space-between" mt={1}>
                    <FormErrorMessage id="branch-error" fontSize="x-small" color="crimson">
                      {branchError}
                    </FormErrorMessage>
                    <Text
                      id="branch-char-count"
                      fontSize="xs"
                      color={customBranch.length === MAX_BRANCH_NAME_LENGTH ? "crimson" : "blackAlpha.700"}
                      aria-live="polite"
                    >
                      {customBranch.length}/{MAX_BRANCH_NAME_LENGTH}
                    </Text>
                  </Flex>
                </Box>
              )}
            </Box>
          </Grid>
        </FormControl>
      )}
    </VStack>
  );
};
