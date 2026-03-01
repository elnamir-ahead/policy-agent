#!/bin/bash
# Build Lambda deployment package with dependencies
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
OUTPUT_DIR="$PROJECT_ROOT/infrastructure/build"
PACKAGE_DIR="$OUTPUT_DIR/package"

rm -rf "$PACKAGE_DIR" "$OUTPUT_DIR/lambda.zip"
mkdir -p "$PACKAGE_DIR"

# Install dependencies
pip install -q duckduckgo-search -t "$PACKAGE_DIR" --upgrade 2>/dev/null || pip3 install -q duckduckgo-search -t "$PACKAGE_DIR" --upgrade

# Copy backend code (exclude app.py)
for f in "$PROJECT_ROOT/backend"/*.py; do
  [ -f "$f" ] && [ "$(basename "$f")" != "app.py" ] && cp "$f" "$PACKAGE_DIR/"
done
cp -r "$PROJECT_ROOT/backend/data" "$PACKAGE_DIR/"

# Create zip
cd "$PACKAGE_DIR"
zip -rq "$OUTPUT_DIR/lambda.zip" .
echo "Built: $OUTPUT_DIR/lambda.zip"
