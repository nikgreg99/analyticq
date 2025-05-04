import React, { useMemo } from 'react';
import { Badge, Icon } from "@chakra-ui/react";
import { Tooltip } from './Tooltip';
import { LuArchive, LuGlobe, LuGitBranch, LuFolder, LuFileCode, LuCircleHelp, LuCircle } from "react-icons/lu";

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
const RepositoryTypeBadge = ({ inputType, withTooltip = true }) => {

  const config = useMemo(() => {

    const type = (inputType || "").toLowerCase();

    const map = {
      archive: {
        colorScheme: "purple",
        icon: LuArchive,
        label: "ARCHIVE",
        description: "Compressed file repository"
      },
      remote: {
        colorScheme: "blue",
        icon: LuGlobe,
        label: "REMOTE",
        description: "Remote git repository"
      },
      repo: {
        colorScheme: "teal",
        icon: LuGitBranch,
        label: "REPO",
        description: "Local git repository"
      },
      local: {
        colorScheme: "green",
        icon: LuFolder,
        label: "LOCAL DIR",
        description: "Local directory"
      },
      script: {
        colorScheme: "orange",
        icon: LuFileCode,
        label: "SCRIPT",
        description: "Executable script"
      },
      default: {
        colorScheme: "gray",
        icon: LuCircleHelp,
        label: "UNKNOWN",
        description: "Unknown repository type"
      }
    }


    return map[type] || map.default;
  }, [inputType]);



  const badge = (
    <Badge
      as="span"
      colorPalette={config.colorScheme}
      display="flex"
      alignItems="center"
      px={2}
      py={1}
      aria-label={`Repository type: ${config  .label}`}
    >
      <Icon as={config.icon} mr={1} aria-hidden="true" />
      {config.label}
    </Badge>
  );

  return withTooltip ? (
    <Tooltip
      content={config.description}
      aria-label="Repository type description"
      showArrow
      placement="top"
    >
      {badge}
    </Tooltip>
  ) : badge;
};

export default RepositoryTypeBadge;
