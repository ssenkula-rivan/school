#!/bin/bash

# Daily Backup Script for School Management System
# Run this script via cron for automatic daily backups

# Get script directory and project root
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_DIR="$( cd "$SCRIPT_DIR/../.." && pwd )"

# Change to project directory
cd "$PROJECT_DIR"

# Log file
LOG_FILE="$PROJECT_DIR/logs/backup.log"
mkdir -p "$PROJECT_DIR/logs"

# Function to log messages
log_message() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log_message "Starting daily backup..."

# Create backup
python3 manage.py backup_database --type=daily >> "$LOG_FILE" 2>&1

if [ $? -eq 0 ]; then
    log_message "Backup completed successfully"
else
    log_message "ERROR: Backup failed"
    exit 1
fi

# Cleanup old backups (keep last 30 days)
log_message "Cleaning up old backups..."
python3 manage.py cleanup_backups --days=30 >> "$LOG_FILE" 2>&1

if [ $? -eq 0 ]; then
    log_message "Cleanup completed successfully"
else
    log_message "WARNING: Cleanup failed"
fi

log_message "Daily backup process completed"
