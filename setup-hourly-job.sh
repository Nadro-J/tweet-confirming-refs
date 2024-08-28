#!/bin/bash

# Define the cron job you want to add
CRON_JOB="0 * * * * cd $(pwd) && /usr/bin/python3 $(pwd)/main.py"

crontab -l > mycron

if ! grep -Fq "$CRON_JOB" mycron; then
    echo "$CRON_JOB" >> mycron
    crontab mycron
    echo "Cron job added successfully."
else
    echo "Cron job already exists."
fi

# Clean up
rm mycron
