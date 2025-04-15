import React from 'react';
import { Badge, Flex, Icon } from "@chakra-ui/react";
import { LuArchive, LuGlobe, LuGitBranch, LuFolder, LuFileCode } from "react-icons/lu";

/**
 * A component that displays a badge with an icon and label based on the repository type.
 *
 * @component
 * @param {Object} props - The component props
 * @param {string} props.inputType - The type of repository to display. Can be one of:
 *   - "archive" - Purple badge with archive icon
 *   - "remote" - Blue badge with globe icon
 *   - "repo" - Teal badge with git branch icon
 *   - "local" - Green badge with folder icon
 *   - "script" - Orange badge with file code icon
 *   If type is not recognized, displays gray badge with "UNKNOWN"
 *
 * @returns {JSX.Element} A Badge component containing an icon and label
 *
 * @example
 * <RepositoryTypeBadge inputType="remote" />
 */
const RepositoryTypeBadge = ({ inputType }) => {

    const typeConfig = {

        "archive": { colorScheme: "purple", icon: LuArchive, label: "ARCHIVE" },
        "remote": { colorScheme: "blue", icon: LuGlobe, label: "REMOTE" },
        "repo": { colorScheme: "teal", icon: LuGitBranch, label: "REPO" },
        "local": { colorScheme: "green", icon: LuFolder, label: "LOCAL DIR" },
        "script": { colorScheme: "orange", icon: LuFileCode, label: "SCRIPT" },
        "default": { colorScheme: "gray", icon: LuFileCode, label: "UNKNOWN" }
    }

    const config = typeConfig[inputType?.toLowerCase()] || typeConfig.default;

    return (
        <Badge
            colorScheme={config.colorScheme}
            display="flex"
            alignItems="center"
            px={2}
            py={1}
        >
            <Icon as={config.icon} mr={1} />
            {config.label || inputType || "N/A"}
        </Badge>
    )

}

export default RepositoryTypeBadge;
