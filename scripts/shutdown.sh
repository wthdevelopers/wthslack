#!/bin/bash
# Purge, vacuum and clean up the database
# Disable servers until the next year to keep costs low
# Created by James Raphael Tiovalen (2020)

# Leave virtual environment
source "../env/bin/activate"
deactivate

# Remove MySQL database
mysql -u root -p < "db_scripts/teardown.sql"

# Remove virtual environment folder
sudo rm -rf "../env"
