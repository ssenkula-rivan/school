#!/bin/bash

# Auto Sync Script - Runs every 15 minutes to sync when online

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_DIR="$( cd "$SCRIPT_DIR/../.." && pwd )"

cd "$PROJECT_DIR"

LOG_FILE="$PROJECT_DIR/logs/sync.log"
mkdir -p "$PROJECT_DIR/logs"

log_message() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log_message "Starting auto sync..."

python3 manage.py sync_data --direction=both >> "$LOG_FILE" 2>&1

if [ $? -eq 0 ]; then
    log_message "Sync completed"
else
    log_message "Sync failed or offline"
fi
