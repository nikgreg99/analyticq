import React, { useMemo } from "react";
import { Badge, Icon, useBreakpointValue } from "@chakra-ui/react";
import { Tooltip } from "../general/Tooltip";
import {
  LuArchive,
  LuGlobe,
  LuGitBranch,
  LuFolder,
  LuFileCode,
  LuCircleHelp,
} from "react-icons/lu";

/**
 * Displays a responsive badge with icon and label for the repository type.
 *
 * @param {Object} props
 * @param {string} props.inputType - Repository type
 * @param {boolean} [props.withTooltip=true] - Whether to show a tooltip
 */
const RepositoryTypeBadge = ({ inputType, withTooltip = true }) => {
  const isCompact = useBreakpointValue({ base: true, md: false });

  const config = useMemo(() => {
    const type = (inputType || "").toLowerCase();
    const map = {
      archive: {
        colorScheme: "purple",
        icon: LuArchive,
        label: "ARCHIVE",
        description: "Compressed file repository",
      },
      remote: {
        colorScheme: "blue",
        icon: LuGlobe,
        label: "REMOTE",
        description: "Remote git repository",
      },
      repo: {
        colorScheme: "teal",
        icon: LuGitBranch,
        label: "REPO",
        description: "Local git repository",
      },
      local: {
        colorScheme: "green",
        icon: LuFolder,
        label: "LOCAL DIR",
        description: "Local directory",
      },
      script: {
        colorScheme: "orange",
        icon: LuFileCode,
        label: "SCRIPT",
        description: "Executable script",
      },
      default: {
        colorScheme: "gray",
        icon: LuCircleHelp,
        label: "UNKNOWN",
        description: "Unknown repository type",
      },
    };
    return map[type] || map.default;
  }, [inputType]);

  const badge = (
    <Badge
      as="span"
      colorPalette={config.colorScheme}
      display="flex"
      alignItems="center"
      px={{ base: 2, md: 3 }}
      py={{ base: 1, md: 1.5 }}
      fontSize={{ base: "xs", md: "sm" }}
      borderRadius="md"
      aria-label={`Repository type: ${config.label}`}
    >
      <Icon
        as={config.icon}
        boxSize={{ base: 3.5, md: 4 }}
        mr={1}
        aria-hidden="true"
      />
      {isCompact ? config.label.slice(0, 6) : config.label}
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
  ) : (
    badge
  );
};

RepositoryTypeBadge.displayName = "RepositoryTypeBadge";

export default RepositoryTypeBadge;
