#!/bin/bash

# Setup automatic daily backups using cron

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_DIR="$( cd "$SCRIPT_DIR/../.." && pwd )"
BACKUP_SCRIPT="$SCRIPT_DIR/daily_backup.sh"

echo "Setting up automatic daily backups..."
echo ""

# Check if cron is available
if ! command -v crontab &> /dev/null; then
    echo "ERROR: crontab not found. Please install cron."
    exit 1
fi

# Create cron job (runs daily at 2 AM)
CRON_JOB="0 2 * * * $BACKUP_SCRIPT"

# Check if job already exists
if crontab -l 2>/dev/null | grep -q "$BACKUP_SCRIPT"; then
    echo "Cron job already exists"
else
    # Add cron job
    (crontab -l 2>/dev/null; echo "$CRON_JOB") | crontab -
    echo "Cron job added successfully"
fi

echo ""
echo "Daily backup scheduled at 2:00 AM"
echo "Backup location: $PROJECT_DIR/backups/"
echo ""
echo "To view cron jobs: crontab -l"
echo "To remove cron job: crontab -e"
