#!/bin/bash

# Setup automatic sync every 15 minutes

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
SYNC_SCRIPT="$SCRIPT_DIR/auto_sync.sh"

echo "Setting up automatic sync..."
echo ""

if ! command -v crontab &> /dev/null; then
    echo "ERROR: crontab not found"
    exit 1
fi

# Create cron job (runs every 15 minutes)
CRON_JOB="*/15 * * * * $SYNC_SCRIPT"

if crontab -l 2>/dev/null | grep -q "$SYNC_SCRIPT"; then
    echo "Auto sync already configured"
else
    (crontab -l 2>/dev/null; echo "$CRON_JOB") | crontab -
    echo "Auto sync configured successfully"
fi

echo ""
echo "Sync will run every 15 minutes when online"
echo "Manual sync: python3 manage.py sync_data"
echo "View sync status: http://localhost:8000/core/sync/"
