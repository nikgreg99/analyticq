import React, { useState, useEffect, useCallback } from "react";
import {
    VStack,
    Select,
    Input,
    createListCollection,
    Portal,
    Box,
    Flex
} from '@chakra-ui/react';
import {
    FormControl,
    FormLabel,
    FormErrorMessage
} from "@chakra-ui/form-control";


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
    onBranchChange,
}) => {
    const [selectedBranch, setSelectedBranch] = useState([]);
    const [url, setUrl] = useState('');
    const [isUrlValid,  setIsUrlValid] = useState(false);
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

        if(!trimmedBranch){
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

    const handleUrlChange = (value) => {
        setUrl(value);

        if(validateUrl(value)){
            onUrlChange(value);
        }
    }

    const handleBranchChange = (value) => {
        console.log("Selected branch", value[0]);
        setSelectedBranch(value);
        setBranchError("");

        if (value[0] != "other"){
            onBranchChange(value[0]);

        }
    }

    const handleCustomBranchChange = (value) => {
        console.log("Selected custom branch: ", value);
        setCustomBranch(value);

        // Only validate and trigger onBranchChange if 'other' is selected
        if (selectedBranch[0] === "other") {
            const isValid = validateBranchName(value);
            console.log("Branch name valid ? :", isValid)
            if (isValid) {
                onBranchChange(value);
            }
        }
    };


    const branchOptions = createListCollection({
        items: [
            {label: "main", value: "main"},
            {label: "master", value: "master"},
            {label: "dev", value:"dev"},
            {label: "Other", value:"other"}
        ],
    })


    useEffect(() => {
        console.log(selectedBranch, customBranch);
        if (selectedBranch[0] == "other" && customBranch) {
            console.log("Validating custom branch name");
            console.log("Validating branch name:", validateBranchName(customBranch));

        }
    }, [customBranch, selectedBranch, validateBranchName]);


    return (
        <VStack
            spacing={2}
            align="stretch"
            p={4}
            borderRadius="md"
            boxShadow="sm"
        >
            <FormControl isInvalid={!!urlError || !!branchError}>
                <Flex alignItems="center" mb={2}>
                    <FormLabel
                        textColor="GrayText"
                        fontWeight="semibold"
                        mb={0}
                        flex="0 0 150px"
                    >
                        Repository URL
                    </FormLabel>
                    <Box flex={1}>
                        <Input
                            mt={3}
                            placeholder="https://github.com/username/repository"
                            value={url}
                            color="black"
                            borderColor={urlError ? "red.500" : "blackAlpha.900"}
                            onChange={(e) => handleUrlChange(e.target.value)}
                            aria-describedby="url-error"
                            />
                        <FormErrorMessage textColor="crimson" mt={4} fontSize="small">
                            {urlError}
                        </FormErrorMessage>
                    </Box>
                </Flex>

                {isUrlValid && (
                     <Flex alignItems="center" mb={2}>
                     <FormLabel
                         textColor="GrayText"
                         flex="0 0 150px"
                         >
                         Branch
                     </FormLabel>
                     <Box flex={1}>
                         <Select.Root
                             mt={1}
                             collection={branchOptions}
                             value={selectedBranch}
                             onValueChange={(e) => handleBranchChange(e.value)}
                             border="black"
                             defaultValue={["main"]}
                             >
                             <Select.HiddenSelect />
                             <Select.Control>
                                 <Select.Trigger>
                                     <Select.ValueText
                                         placeholder="Select branch"
                                         aria-placeholder="Select branch"
                                         color="blackAlpha.900"
                                         />
                                 </Select.Trigger>
                                 <Select.IndicatorGroup>
                                     <Select.ClearTrigger/>
                                     <Select.Indicator />
                                 </Select.IndicatorGroup>
                             </Select.Control>
                             <Portal>
                                 <Select.Positioner>
                                     <Select.Content
                                     >
                                         {branchOptions.items.map((branch) => (
                                             <Select.Item
                                             item={branch}
                                             key={branch.value}
                                             >
                                                 {branch.label}
                                             <Select.ItemIndicator/>
                                             </Select.Item>
                                         ))}
                                     </Select.Content>
                                 </Select.Positioner>
                             </Portal>
                         </Select.Root>
                         {selectedBranch[0] === "other" && (
                             <Box mt={2}>
                                 <Input
                                     mt={3}
                                     placeholder="Enter custom branch"
                                     aria-placeholder="Enter custom branch"
                                     borderColor={branchError? "red.500" : "blackApha.900"}
                                     color="black"
                                     value={customBranch}
                                     onChange={(e) => handleCustomBranchChange(e.target.value)}
                                     aria-describedby="branch-error"
                                     maxLength={MAX_BRANCH_NAME_LENGTH}
                                 />
                                 <FormErrorMessage textColor="crimson" mt={4} fontSize="small">
                                     {branchError}
                                 </FormErrorMessage>
                                 <Box
                                     borderColor="gray.300"
                                     color="blackAlpha.900"
                                     fontSize="xs"
                                     mt={1}
                                  >
                                     {customBranch.length}/{MAX_BRANCH_NAME_LENGTH} characters
                                </Box>
                             </Box>
                         )}
                     </Box>
                 </Flex>
                )}
            </FormControl>
        </VStack>
    );
}
