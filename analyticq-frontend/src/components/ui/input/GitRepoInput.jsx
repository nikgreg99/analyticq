import React, { useState, useCallback, useEffect, useMemo, useRef } from "react";
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

// Memoized branch options to prevent recreation on every render
const BRANCH_OPTIONS = createListCollection({
  items: [
    { label: "main", value: "main" },
    { label: "master", value: "master" },
    { label: "dev", value: "dev" },
    { label: "Other", value: "other" },
  ],
});

export const GitRepoInput = React.memo(({
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

  // Refs for better accessibility
  const urlInputRef = useRef(null);
  const customBranchInputRef = useRef(null);

  // Memoized validation functions to prevent recreation
  const validateUrl = useCallback((inputUrl) => {
    const trimmedUrl = inputUrl.trim().toLowerCase();

    if (!trimmedUrl) {
      setUrlError("Repository URL is required");
      setIsUrlValid(false);
      return false;
    }

    if (!GIT_URL_REGEX.test(trimmedUrl)) {
      setUrlError("Please enter a valid repository URL from GitHub, GitLab, or Bitbucket");
      setIsUrlValid(false);
      return false;
    }

    if (
      trimmedUrl.includes("//github.com//") ||
      trimmedUrl.includes("//gitlab.com//") ||
      trimmedUrl.includes("//bitbucket.org//")
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

  // Memoized URL normalization
  const normalizeGitUrl = useCallback((url) => url.trim().replace(/\.git$/, ""), []);

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

  // Memoized event handlers to prevent unnecessary re-renders
  const handleUrlChange = useCallback((value) => {
    setUrl(value);
    if (!urlTouched) {
      setUrlTouched(true);
    }
  }, [urlTouched]);

  const handleUrlBlur = useCallback(() => {
    setUrlTouched(true);
  }, []);

  const handleBranchChange = useCallback((value) => {
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
      onBranchChange(value[0]);
      // Focus management for accessibility
      if (customBranchInputRef.current) {
        customBranchInputRef.current.blur();
      }
    } else {
      // Focus the custom branch input when "Other" is selected
      setTimeout(() => {
        if (customBranchInputRef.current) {
          customBranchInputRef.current.focus();
        }
      }, 100);

      if (customBranch && validateBranchName(customBranch)) {
        onBranchChange(customBranch);
      } else {
        onBranchChange("");
      }
    }
  }, [onCustomBranchToggle, onBranchChange, customBranch, validateBranchName]);

  const handleCustomBranchChange = useCallback((value) => {
    setCustomBranch(value);
    if (!branchTouched) {
      setBranchTouched(true);
    }

    // Only update branch if "other" is selected
    if (selectedBranch[0] === "other") {
      onBranchChange(value);
    }
  }, [branchTouched, selectedBranch, onBranchChange]);

  const handleCustomBranchBlur = useCallback(() => {
    setBranchTouched(true);
  }, []);

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
  }, [debouncedUrl, validateUrl, onUrlChange, urlTouched, normalizeGitUrl]);

  // Validate branch name after debounce
  useEffect(() => {
    if (branchTouched && selectedBranch[0] === "other") {
      validateBranchName(debouncedBranch);
    }
  }, [debouncedBranch, selectedBranch, validateBranchName, branchTouched]);

  // Memoized responsive column count
  const columnCount = useBreakpointValue({ base: 1, md: 2 });

  // Memoized character count color calculation
  const charCountColor = useMemo(() => {
    if (customBranch.length === MAX_BRANCH_NAME_LENGTH) return "crimson";
    if (customBranch.length > MAX_BRANCH_NAME_LENGTH * 0.8) return "orange.500";
    return "blackAlpha.700";
  }, [customBranch.length]);

  // Memoized accessibility descriptions
  const urlAriaDescribedBy = useMemo(() => {
    const descriptions = ["url-help"];
    if (urlTouched && urlError) {
      descriptions.push("url-error");
    }
    return descriptions.join(" ");
  }, [urlTouched, urlError]);

  const branchAriaDescribedBy = useMemo(() => {
    const descriptions = ["branch-char-count"];
    if (branchTouched && branchError) {
      descriptions.push("branch-error");
    }
    return descriptions.join(" ");
  }, [branchTouched, branchError]);

  return (
    <Box
      p={{ base: 4, md: 6 }}
      borderRadius="md"
      borderWidth="1px"
      borderColor="blackAlpha.200"
      boxShadow="md"
      width="auto"
      role="region"
      aria-labelledby="git-repo-heading"
    >
      {/* Screen reader heading */}
      <Box
        id="git-repo-heading"
        position="absolute"
        left="-10000px"
        aria-level="2"
        as="h2"
      >
        Git Repository Configuration
      </Box>

      <Grid
        templateColumns={`repeat(${columnCount}, 1fr)`}
        gap={6}
        as="form"
        role="form"
        aria-labelledby="git-repo-heading"
      >
        {/* Repository URL */}
        <GridItem colSpan={columnCount}>
          <Field.Root invalid={urlTouched && !!urlError} required>
            <Field.Label htmlFor="repo-url" color="blackAlpha.800">
              Repository URL <Field.RequiredIndicator />
            </Field.Label>
            <Box id="url-help" fontSize="sm" color="blackAlpha.600" mb={2}>
              Enter a GitHub, GitLab, or Bitbucket repository URL
            </Box>
            <InputGroup
              startElement={<Icon as={FiLink} color="black" aria-hidden="true" />}
              endElement={
                <Tooltip content="Git extension (.git) is optional and will be normalized." showArrow>
                  <Icon
                    as={FiInfo}
                    color="black"
                    aria-label="Additional information about URL format"
                    tabIndex={0}
                  />
                </Tooltip>
              }
            >
              <Input
                ref={urlInputRef}
                id="repo-url"
                name="repo-url"
                type="url"
                placeholder="https://github.com/username/repository"
                value={url}
                borderColor={
                  urlTouched && urlError ? "crimson" : "blackAlpha.800"
                }
                color="blackAlpha.800"
                onChange={(e) => handleUrlChange(e.target.value)}
                onBlur={handleUrlBlur}
                aria-describedby={urlAriaDescribedBy}
                aria-invalid={urlTouched && !!urlError}
                pl={8}
                autoComplete="url"
                spellCheck={false}
              />
            </InputGroup>
            {urlTouched && urlError && (
              <Field.ErrorText
                id="url-error"
                mt={1}
                fontSize="sm"
                color="crimson"
                role="alert"
                aria-live="polite"
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
                  collection={BRANCH_OPTIONS}
                  value={selectedBranch}
                  onValueChange={(e) => handleBranchChange(e.value)}
                  id="branch-select"
                >
                  <Select.HiddenSelect
                    aria-label="Select branch"
                    aria-describedby="branch-help"
                  />
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
                        {BRANCH_OPTIONS.items.map((branch) => (
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
                <Box id="branch-help" fontSize="sm" color="blackAlpha.600" mt={1}>
                  Select a common branch or choose "Other" for custom branch
                </Box>
              </Field.Root>
            </GridItem>

            {selectedBranch[0] === "other" && (
              <GridItem colSpan={columnCount}>
                <Field.Root
                  invalid={branchTouched && !!branchError}
                  required
                >
                  <Field.Label htmlFor="custom-branch" color="blackAlpha.800">
                    Custom Branch Name <Field.RequiredIndicator />
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
                          aria-label={`${customBranch.length} of ${MAX_BRANCH_NAME_LENGTH} characters used`}
                        >
                          {customBranch.length}/{MAX_BRANCH_NAME_LENGTH}
                        </Span>
                        <Tooltip
                          content="Branch names can contain letters, numbers, dots, hyphens, and underscores. Maximum 255 characters."
                          showArrow
                        >
                          <Icon
                            as={FiInfo}
                            ml={2}
                            aria-label="Branch naming rules"
                            tabIndex={0}
                          />
                        </Tooltip>
                      </>
                    }
                  >
                    <Input
                      ref={customBranchInputRef}
                      id="custom-branch"
                      name="custom-branch"
                      placeholder="Enter custom branch name"
                      value={customBranch}
                      onChange={(e) => handleCustomBranchChange(e.target.value)}
                      onBlur={handleCustomBranchBlur}
                      maxLength={MAX_BRANCH_NAME_LENGTH}
                      pl={8}
                      borderColor={
                        branchTouched && branchError
                          ? "crimson"
                          : "blackAlpha.800"
                      }
                      color="blackAlpha.800"
                      aria-describedby={branchAriaDescribedBy}
                      aria-invalid={branchTouched && !!branchError}
                      spellCheck={false}
                      autoComplete="off"
                    />
                  </InputGroup>
                  {branchTouched && branchError && (
                    <Field.ErrorText
                      id="branch-error"
                      fontSize="sm"
                      color="crimson"
                      mt={1}
                      role="alert"
                      aria-live="polite"
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
});

GitRepoInput.displayName = "GitRepoInput";
