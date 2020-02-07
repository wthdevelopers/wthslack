#!/bin/bash
# Provide CATEGORY_LIST & JUDGE_LIST arguments so as to self-modify code appropriately before launch
# Initialize cloud servers for Slack bot code
# Turn on database servers and cloud functions
# Created by James Raphael Tiovalen (2020)

sudo apt update

# Install dependencies for MySQL
sudo apt install -y mysql-server

# Activate virtual environment and install dependencies
sudo apt install -y python3.7
sudo python3.7 -m venv "../env"
source "../env/bin/activate"
sudo pip install --upgrade pip
sudo pip install -r "../requirements.txt"

# Expose mysql-server to open internet
sed "s/bind-address		= 127.0.0.1/bind-address		= 0.0.0.0/g" "/etc/mysql/mysql.conf.d/mysqld.cnf" > "/etc/mysql/mysql.conf.d/mysqld.cnf"

# Expose port 3306 to public
iptables -A INPUT -i eth0 -p tcp --destination-port 3306 -j ACCEPT

# Run SQL script
mysql -u root -p < "db_scripts/setup.sql"

/etc/init.d/mysql restart

# Run Gunicorn
cd "../app"
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker
