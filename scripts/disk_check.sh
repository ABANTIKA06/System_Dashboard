#!/bin/bash
#Disk Usage Alert Script


CSV="/home/abantika/disk_storage/data/disk_usage.csv"
LOG_FILE="/home/abantika/disk_storage/logs/disk.log"
ALERT_FILE="/home/abantika/disk_storage/logs/disk_alert.log"

#Define usage threshold
THRESHOLD=8

# Get disk usage (trim spaces, remove %)
USAGE=$(df -P /home | awk 'NR==2 {print $5}' | tr -d '%' | xargs)

# Write to CSV (for dashboard and graphs)
echo "$(date '+%Y-%m-%d %H:%M:%S'),${USAGE}" >> "$CSV"


# Write usage to log file with timestamp
echo "$(date '+%Y-%m-%d %H:%M:%S') Disk usage is ${USAGE}%" >> "$LOG_FILE"

# Check against threshold
if [ "$USAGE" -ge "$THRESHOLD" ]; then
    MESSAGE="Disk usage is too high: ${USAGE}%"
    echo "$(date '+%Y-%m-%d %H:%M:%S') $MESSAGE" >> "$ALERT_FILE"

    # Send alerts
    wall "$MESSAGE"
    notify-send "Disk Alert" "$MESSAGE"
fi
