#!/bin/bash
# With cron, this script will be run every day (as long as Docker container is online)
# Currnet running time is set to 13:00 UTC (which translates to 22:00 KST)

# Navigate to the location of main.py
cd /root/work

# logging last time runned
echo -e date > /tmp/cron.log

# Start scraping data
# - into all export options 
# - without cleaning
python main.py -export_opt all -clean false > /tmp/cron.log