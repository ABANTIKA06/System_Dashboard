#!/bin/bash

SOURCE="/home/abantika/disk_storage/backups"
LOG="/home/abantika/disk_storage/logs/disk.log"

DAYS=7
THRESHOLD=80

usage=$(df -P / | awk 'NR==2 {print $5}' | tr -d '%')

echo "$(date): Disk = $usage%" >> $LOG

if [ "$usage" -gt "$THRESHOLD" ]; then
    echo "$(date): Cleaning old backup files in $SOURCE..." >> $LOG

    find "$SOURCE" -type f -mtime +$DAYS -print -delete >> $LOG

    notify-send "Disk Cleanup Done" "Old backups deleted!"
else
    echo "$(date): Usage normal. No cleanup." >> $LOG
fi

