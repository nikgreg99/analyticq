import React, { useState, useCallback, useEffect, useMemo } from "react";
import {
  Box,
  Grid,
  GridItem,
  Input,
  Flex,
  Icon,
  InputGroup,
  useBreakpointValue,
  Select,
  createListCollection,
  Field,
  Portal,
  Span,
} from "@chakra-ui/react";
import { FiLink, FiGitBranch, FiCode, FiInfo } from "react-icons/fi";
import { Tooltip } from "../general/Tooltip";
import { useDebounce } from "use-debounce";

// Constants
const MAX_BRANCH_NAME_LENGTH = 255;
const DEFAULT_BRANCH = "main";
const GIT_URL_REGEX =
  /^(https?:\/\/)?(www\.)?(github\.com|gitlab\.com|bitbucket\.org)\/([\w-]+)\/([\w.-]+)(\.git)?$/;
const BRANCH_NAME_REGEX = /^(?!\/|\.|-)[a-zA-Z0-9._/-]+(?<!\/|\.|-)$/;

export const GitRepoInput = ({
  onUrlChange,
  onBranchChange,
  onCustomBranchToggle,
  isCustomBranchSelected,
  customBranchValue,
  // Props to sync with parent state
  gitUrl = "",
  branch = "",
}) => {
  const [selectedBranch, setSelectedBranch] = useState(
    isCustomBranchSelected ? ["other"] : [DEFAULT_BRANCH]
  );
  const [url, setUrl] = useState(gitUrl);
  const [isUrlValid, setIsUrlValid] = useState(false);
  const [urlError, setUrlError] = useState("");
  const [customBranch, setCustomBranch] = useState(customBranchValue || branch);
  const [branchError, setBranchError] = useState("");

  // Track if fields have been touched/interacted with
  const [urlTouched, setUrlTouched] = useState(false);
  const [branchTouched, setBranchTouched] = useState(false);

  const [debouncedUrl] = useDebounce(url, 500);
  const [debouncedBranch] = useDebounce(customBranch, 500);

  // Reset component state when parent resets (when both gitUrl and branch are empty)
  useEffect(() => {
    if (gitUrl === "" && branch === "") {
      setUrl("");
      setCustomBranch("");
      setSelectedBranch([DEFAULT_BRANCH]);
      setIsUrlValid(false);
      setUrlError("");
      setBranchError("");
      setUrlTouched(false);
      setBranchTouched(false);
    }
  }, [gitUrl, branch]);

  const validateUrl = useCallback((inputUrl) => {
    const trimmedUrl = inputUrl.trim().toLowerCase();

    if (!trimmedUrl) {
      setUrlError("Repository URL is required");
      setIsUrlValid(false);
      return false;
    }

    if (!GIT_URL_REGEX.test(trimmedUrl)) {
      setUrlError("Please enter a valid repository URL");
      setIsUrlValid(false);
      return false;
    }

    if (
      trimmedUrl.includes("//github.com//") ||
      trimmedUrl.includes("//gitlab.com//")
    ) {
      setUrlError("Invalid URL: contains duplicate slashes");
      setIsUrlValid(false);
      return false;
    }

    setUrlError("");
    setIsUrlValid(true);
    return true;
  }, []);

  const validateBranchName = useCallback((branchName) => {
    const trimmedBranch = branchName.trim();

    if (!trimmedBranch) {
      setBranchError("Branch name is required");
      return false;
    }

    if (!BRANCH_NAME_REGEX.test(trimmedBranch)) {
      setBranchError(
        "Invalid branch name. Use letters, numbers, dots, hyphens, and underscores only."
      );
      return false;
    }

    if (trimmedBranch.toLowerCase() === "head") {
      setBranchError('Branch name cannot be "HEAD"');
      return false;
    }

    if (trimmedBranch.length > MAX_BRANCH_NAME_LENGTH) {
      setBranchError(
        `Branch name cannot exceed ${MAX_BRANCH_NAME_LENGTH} characters`
      );
      return false;
    }

    setBranchError("");
    return true;
  }, []);

  const normalizeGitUrl = (url) => url.trim().replace(/\.git$/, "");

  const handleUrlChange = (value) => {
    setUrl(value);
    if (!urlTouched) {
      setUrlTouched(true);
    }
  };

  const handleBranchChange = (value) => {
    setSelectedBranch(value);
    setBranchTouched(true);
    setBranchError("");

    const isOtherSelected = value[0] === "other";

    // Inform parent component about custom branch toggle
    if (onCustomBranchToggle) {
      onCustomBranchToggle(isOtherSelected);
    }

    if (!isOtherSelected) {
      // If selecting a predefined branch, use that value
      // Send the branch value directly to parent component
      onBranchChange(value[0]);
    } else if (customBranch && validateBranchName(customBranch)) {
      // If switching to "Other" and we have a valid custom branch
      onBranchChange(customBranch);
    } else {
      // If switching to "Other" with no valid custom branch, clear it
      onBranchChange("");
    }
  };

  const handleCustomBranchChange = (value) => {
    setCustomBranch(value);
    if (!branchTouched) {
      setBranchTouched(true);
    }

    // Only update branch if "other" is selected
    if (selectedBranch[0] === "other") {
      // Always pass the current value to parent, validation will happen on blur/debounce
      onBranchChange(value);
    }
  };

  // Sync with parent's customBranchValue when it changes externally
  useEffect(() => {
    if (customBranchValue !== undefined && customBranchValue !== customBranch) {
      setCustomBranch(customBranchValue);
    }
  }, [customBranchValue, customBranch]);

  // Initialize selectedBranch based on isCustomBranchSelected
  useEffect(() => {
    if (isCustomBranchSelected && selectedBranch[0] !== "other") {
      setSelectedBranch(["other"]);
    } else if (!isCustomBranchSelected && selectedBranch[0] === "other") {
      setSelectedBranch([DEFAULT_BRANCH]);
      onBranchChange(DEFAULT_BRANCH);
    }
  }, [isCustomBranchSelected, onBranchChange, selectedBranch]);

  // Update URL in parent component after validation
  useEffect(() => {
    if (urlTouched) {
      const normalizedUrl = normalizeGitUrl(debouncedUrl);
      if (validateUrl(normalizedUrl)) {
        onUrlChange(normalizedUrl);
      } else {
        // Clear parent URL if validation fails
        onUrlChange("");
      }
    }
  }, [debouncedUrl, validateUrl, onUrlChange, urlTouched]);

  // Validate branch name after debounce
  useEffect(() => {
    if (branchTouched && selectedBranch[0] === "other") {
      validateBranchName(debouncedBranch);
    }
  }, [debouncedBranch, selectedBranch, validateBranchName, branchTouched]);

  const branchOptions = createListCollection({
    items: [
      { label: "main", value: "main" },
      { label: "master", value: "master" },
      { label: "dev", value: "dev" },
      { label: "Other", value: "other" },
    ],
  });

  const columnCount = useBreakpointValue({ base: 1, md: 2 });

  const charCountColor = useMemo(() => {
    if (customBranch.length === MAX_BRANCH_NAME_LENGTH) return "crimson";
    if (customBranch.length > MAX_BRANCH_NAME_LENGTH * 0.8) return "orange.500";
    return "blackAlpha.700";
  }, [customBranch.length]);

  return (
    <Box
      p={{ base: 4, md: 6 }}
      borderRadius="md"
      borderWidth="1px"
      borderColor="blackAlpha.200"
      boxShadow="md"
      width="auto"
    >
      <Grid
        templateColumns={`repeat(${columnCount}, 1fr)`}
        gap={6}
        as="form"
        role="form"
      >
        {/* Repository URL */}
        <GridItem colSpan={columnCount}>
          <Field.Root invalid={urlTouched && !!urlError} required>
            <Field.Label color="blackAlpha.800">
              Repository URL <Field.RequiredIndicator />
            </Field.Label>
            <InputGroup
              startElement={<Icon as={FiLink} color="black" />}
              endElement={
                <Tooltip content="Git extension is optional." showArrow>
                  <Icon as={FiInfo} color="black" />
                </Tooltip>
              }
            >
              <Input
                id="repo-url"
                name="repo-url"
                placeholder="https://github.com/username/repository"
                value={url}
                borderColor={
                  urlTouched && urlError ? "crimson" : "blackAlpha.800"
                }
                color="blackAlpha.800"
                onChange={(e) => handleUrlChange(e.target.value)}
                onBlur={() => setUrlTouched(true)}
                aria-describedby={
                  urlTouched && urlError ? "url-error" : undefined
                }
                aria-invalid={urlTouched && !!urlError}
                pl={8}
                autoComplete="url"
              />
            </InputGroup>
            {urlTouched && urlError && (
              <Field.ErrorText
                id="url-error"
                mt={1}
                fontSize="sm"
                color="crimson"
                role="alert"
              >
                {urlError}
              </Field.ErrorText>
            )}
          </Field.Root>
        </GridItem>

        {/* Branch selection and custom branch input */}
        {isUrlValid && (
          <>
            <GridItem colSpan={columnCount}>
              <Field.Root invalid={branchTouched && !!branchError} required>
                <Field.Label color="blackAlpha.800">
                  Branch <Field.RequiredIndicator />
                </Field.Label>
                <Select.Root
                  collection={branchOptions}
                  value={selectedBranch}
                  onValueChange={(e) => handleBranchChange(e.value)}
                  id="branch-select"
                >
                  <Select.HiddenSelect aria-label="Select branch" />
                  <Select.Control>
                    <Select.Trigger width="full">
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
                            _hover={{ bg: "blackAlpha.50" }}
                          >
                            <Flex align="center">
                              <Icon
                                as={
                                  branch.value === "other"
                                    ? FiCode
                                    : FiGitBranch
                                }
                                mr={2}
                                w={4}
                                h={4}
                                aria-hidden="true"
                              />
                              {branch.label}
                            </Flex>
                          </Select.Item>
                        ))}
                      </Select.Content>
                    </Select.Positioner>
                  </Portal>
                </Select.Root>
              </Field.Root>
            </GridItem>

            {selectedBranch[0] === "other" && (
              <GridItem colSpan={columnCount}>
                <Field.Root
                  htmlFor="custom-branch"
                  invalid={branchTouched && !!branchError}
                  required
                >
                  <Field.Label htmlFor="custom-branch" color="blackAlpha.800">
                    Custom Branch <Field.RequiredIndicator />
                  </Field.Label>
                  <InputGroup
                    startElement={
                      <Icon as={FiCode} color="black" aria-hidden="true" />
                    }
                    endElement={
                      <>
                        <Span
                          id="branch-char-count"
                          fontSize="xs"
                          color={charCountColor}
                          aria-live="polite"
                        >
                          {customBranch.length}/{MAX_BRANCH_NAME_LENGTH}
                        </Span>
                        <Tooltip
                          content="Letters, digits, '.', '-', '_' only. Max 255 chars."
                          showArrow
                        >
                          <Icon as={FiInfo} ml={2} aria-hidden="true" />
                        </Tooltip>
                      </>
                    }
                  >
                    <Input
                      id="custom-branch"
                      name="custom-branch"
                      placeholder="Enter custom branch name"
                      value={customBranch}
                      onChange={(e) => handleCustomBranchChange(e.target.value)}
                      onBlur={() => setBranchTouched(true)}
                      maxLength={MAX_BRANCH_NAME_LENGTH}
                      pl={8}
                      borderColor={
                        branchTouched && branchError
                          ? "crimson"
                          : "blackAlpha.800"
                      }
                      color="blackAlpha.800"
                      aria-describedby={
                        branchTouched && branchError
                          ? "branch-error branch-char-count"
                          : "branch-char-count"
                      }
                      aria-invalid={branchTouched && !!branchError}
                    />
                  </InputGroup>
                  {branchTouched && branchError && (
                    <Field.ErrorText
                      id="branch-error"
                      fontSize="sm"
                      color="crimson"
                      mt={1}
                      role="alert"
                    >
                      {branchError}
                    </Field.ErrorText>
                  )}
                </Field.Root>
              </GridItem>
            )}
          </>
        )}
      </Grid>
    </Box>
  );
};

GitRepoInput.displayName = "GitRepoInput";
