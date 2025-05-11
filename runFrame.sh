#!/bin/bash

sleep 3

# Ensure path environment variables are availble during cron job
export PATH=/usr/local/bin:/usr/bin:/bin:/home/pi/myenv/bin

# Activate py311 python virtual environment
source /home/iain/py311/bin/activate

# Define log file
LOG_FILE="runFrame_log.txt"

# Initialize (clear) the log file
> "$LOG_FILE"

# Function to write log messages with time and date stamp
log_message() {
    echo "$(date): $1" >> "$LOG_FILE"
}

log_message "Begin log."

# Run the two Python scripts in the background
python3 file_transfer.py &
PID1=$!
log_message "Started file_transfer.py with PID $PID1"

python3 slideshow.py &
PID2=$!
log_message "Started slideshow.py with PID $PID2"

# Monitor the processes
echo "Monitoring processes (PID $PID1 and PID $PID2)..."

while true; do
    # Check if PID1 is still running
    if ! kill -0 $PID1 2>/dev/null; then
        log_message "file_transfer.py (PID $PID1) has been terminated."
        break
    fi

    # Check if PID2 is still running
    if ! kill -0 $PID2 2>/dev/null; then
        log_message "slideshow.py (PID $PID2) has been terminated."
        break
    fi

    # Wait for a short interval before checking again
    sleep 1
done

# Terminate the other process if still running
log_message "Terminating remaining process..."
kill $PID1 $PID2 2>/dev/null

# Final log and exit
log_message "Monitoring script finished."
echo "Logs written to $LOG_FILE"
exit 0
