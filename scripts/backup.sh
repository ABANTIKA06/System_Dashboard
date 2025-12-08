#!/bin/bash
# Backup Script for Disk Usage Monitoring Project

# What to back up (entire project)
SOURCE="/home/abantika/disk_storage"

# Where to store backups
DEST="/home/abantika/disk_storage/backups"

# Minimal backup history log (optional, interviewer-friendly)
LOG="/home/abantika/disk_storage/logs/backup_history.log"


# Backup filename
TIME=$(date '+%Y-%m-%d_%H-%M')
BACKUP_FILE="$DEST/project_backup_${TIME}.tar.gz"

# Write to history log
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Starting backup..." >> "$LOG"

# Create compressed backup
tar --exclude="$DEST" -czf "$BACKUP_FILE" "$SOURCE" 2>>"$LOG"

# Notifications + result
if [ $? -eq 0 ]; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Backup created: $BACKUP_FILE" >> "$LOG"
    notify-send "Backup Successful" "Project backup saved to $BACKUP_FILE"
else
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Backup FAILED!" >> "$LOG"
    notify-send "Backup Failed" "Check backup_history.log"
fi

exit 0

