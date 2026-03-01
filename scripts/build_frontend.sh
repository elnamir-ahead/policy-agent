#!/bin/bash
# Build frontend for production
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_ROOT/frontend"

if [ ! -d "node_modules" ]; then
  echo "Installing frontend dependencies..."
  npm install
fi

# Build (API URL will come from config.json at runtime)
npm run build

echo "Built: $PROJECT_ROOT/frontend/dist"
