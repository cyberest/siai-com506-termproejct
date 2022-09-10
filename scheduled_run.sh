#!/bin/bash
# With cron, this script will be run every day (as long as Docker container is online)

# Navigate to the location of main.py
cd /root/work
# Start scraping data
# - into all export options 
# - without cleaning
python main.py -export_opt all -clean false