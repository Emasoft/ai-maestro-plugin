#!/bin/bash
# AI Maestro - List all indexed documents
# Usage: docs-list.sh [--limit N]

set -e

# Source docs helpers
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=/dev/null  # Resolved at runtime based on SCRIPT_DIR
source "${SCRIPT_DIR}/docs-helper.sh"

# shellcheck disable=SC2034 # LIMIT is parsed from CLI args, reserved for future API pagination support
LIMIT=50

while [[ $# -gt 0 ]]; do
  case $1 in
    --limit|-l)
      # shellcheck disable=SC2034 # Parsed from CLI, reserved for future API pagination support
      LIMIT="$2"
      shift 2
      ;;
    --help|-h)
      echo "Usage: docs-list.sh [--limit N]"
      echo ""
      echo "Options:"
      echo "  --limit, -l N    Limit results (default: 50)"
      exit 0
      ;;
    *)
      shift
      ;;
  esac
done

# Initialize (gets SESSION, AGENT_ID, HOST_ID)
init_docs || exit 1

RESPONSE=$(docs_list "$AGENT_ID")

if echo "$RESPONSE" | jq -e '.success == false' > /dev/null 2>&1; then
  ERROR=$(echo "$RESPONSE" | jq -r '.error')
  echo "Error: $ERROR" >&2
  exit 1
fi

RESULTS=$(echo "$RESPONSE" | jq -r '.result // []')
COUNT=$(echo "$RESULTS" | jq 'length')

if [ "$COUNT" = "0" ]; then
  echo "No documents indexed."
  echo ""
  echo "Index documentation with: docs-index.sh"
  exit 0
fi

echo "Indexed Documents ($COUNT):"
echo ""

echo "$RESULTS" | jq -r '.[] | "[\(.docId)] \(.title // "Untitled")\n  Type: \(.docType // "unknown") | File: \(.filePath // "unknown")\n"'
