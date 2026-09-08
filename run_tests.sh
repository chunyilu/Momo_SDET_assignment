#!/usr/bin/env bash
# Test Execution Runner Script for Momo Search SDET Automation Suite

set -e

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_PYTHON="$PROJECT_DIR/.venv/bin/python"
VENV_PYTEST="$PROJECT_DIR/.venv/bin/pytest"

# Ensure venv exists
if [ ! -f "$VENV_PYTEST" ]; then
    echo "[Setup] Virtual environment not found. Initializing..."
    python3 -m venv "$PROJECT_DIR/.venv"
    "$PROJECT_DIR/.venv/bin/pip" install -r "$PROJECT_DIR/requirements.txt"
    "$PROJECT_DIR/.venv/bin/playwright" install chromium
fi

echo "=========================================================="
echo " Momo E-Commerce Search Test Automation Runner"
echo "=========================================================="

MODE=${1:-"all"}

case "$MODE" in
    smoke)
        echo "Running Smoke Tests (Critical Search Paths)..."
        "$VENV_PYTEST" -m smoke
        ;;
    regression)
        echo "Running Full Regression Test Suite..."
        "$VENV_PYTEST" -m regression
        ;;
    filter-sort)
        echo "Running Sorting & Filtering Tests..."
        "$VENV_PYTEST" -m filter_sort
        ;;
    edge-case)
        echo "Running Edge Cases & Security Tests..."
        "$VENV_PYTEST" -m "edge_case or security"
        ;;
    headed)
        echo "Running Tests in Headed Mode..."
        HEADLESS=false "$VENV_PYTEST" --browser-headless=false
        ;;
    all)
        echo "Running Complete Test Suite..."
        "$VENV_PYTEST"
        ;;
    *)
        echo "Unknown mode: $MODE"
        echo "Usage: $0 [smoke|regression|filter-sort|edge-case|headed|all]"
        exit 1
        ;;
esac

echo "=========================================================="
echo " Test Execution Completed. HTML Report:"
echo " file://$PROJECT_DIR/reports/test_report.html"
echo "=========================================================="
