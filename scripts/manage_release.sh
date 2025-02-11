#!/bin/bash

# Get the latest version from the repository
LATEST_TAG=$(git describe --tags --abbrev=0)

# Increment the version (assuming semantic versioning)
IFS='.' read -r -a VERSION_PARTS <<< "$LATEST_TAG"
MAJOR=${VERSION_PARTS[0]}
MINOR=${VERSION_PARTS[1]}
PATCH=${VERSION_PARTS[2]}

NEW_PATCH=$((PATCH + 1))
NEW_TAG="$MAJOR.$MINOR.$NEW_PATCH"

# Tag the repository with the new version
git tag -a "$NEW_TAG" -m "Release $NEW_TAG"

# Push the tag to the repository
git push origin "$NEW_TAG
