#!/bin/bash

# https://github.com/orgs/community/discussions/26256#discussioncomment-13849174

# Set environment variables to disable prompts
export GH_PROMPT_DISABLED=1
export GH_NO_UPDATE_NOTIFIER=1

# Check if workflow name is provided
if [ -z "$1" ]; then
  echo "Error: Workflow name is required"
  echo "Usage: $0 <workflow-name>"
  echo "Example: $0 deploy.yml"
  exit 1
fi

WORKFLOW="$1"

echo "Deleting workflow runs for: $WORKFLOW"

# Get repository info once
REPO=$(gh repo view --json nameWithOwner -q .nameWithOwner)

# Get all run IDs first, then process them
echo "Getting workflow run IDs..."
RUN_IDS=$(gh run --workflow "$WORKFLOW" list --limit 100 --json databaseId -q '.[].databaseId' 2>/dev/null | grep -E '^[0-9]+$')
echo "Done!"

if [ -z "$RUN_IDS" ]; then
  echo "No workflow runs found for: $WORKFLOW"
  exit 0
fi

echo "Found $(echo "$RUN_IDS" | wc -l) runs to delete"

# Process each ID
echo "$RUN_IDS" | while read -r id; do
  if [ -n "$id" ]; then
    echo "Deleting run ID: $id"
    gh api "repos/$REPO/actions/runs/$id" -X DELETE >/dev/null 2>&1
    if [ $? -eq 0 ]; then
      echo "✓ Deleted run $id"
    else
      echo "✗ Failed to delete run $id"
    fi
  fi
done

echo "Done!"
