#!/bin/bash
TAG="v1.2.6"
TITLE=$TAG"-alpha"
NOTES="update"
gh release create "$TAG" --title "$TITLE" --notes "$NOTES"
REPO_URL=$(gh repo view --json nameWithOwner -q '.nameWithOwner')
echo "Source ZIP:"
echo "https://github.com/$REPO_URL/archive/refs/tags/$TAG.zip"

# gh release create v1.2.1 --title "v1.2.1-alpha" --notes "整理框架，增加图像保存功能，和csv保存功能"


# https://github.com/sunw43350/ws/releases/tag/v1.2.1
# https://github.com/sunw43350/ws/archive/refs/tags/v1.2.1.zip