#!/bin/bash
# Cowrie SSH Honeypot Setup Script
# Run this on a fresh Ubuntu EC2 instance as ubuntu user
# Usage: bash setup-cowrie.sh

echo "=== Installing Dependencies ==="
sudo apt update
sudo apt install -y git python3-virtualenv libssl-dev libffi-dev \
build-essential libpython3-dev python3-minimal authbind \
virtualenv python3-pip awscli

echo "=== Creating Cowrie User ==="
sudo adduser --disabled-password --gecos "" cowrie

echo "=== Setting Up Cowrie ==="
sudo su - cowrie << 'EOF'
git clone http://github.com/cowrie/cowrie
cd cowrie
virtualenv --python=python3 cowrie-env
source cowrie-env/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
pip install -e .
cp src/cowrie/data/etc/cowrie.cfg.dist etc/cowrie.cfg
cowrie start
cowrie status
EOF

echo "=== Setting Up S3 Log Sync ==="
(crontab -l 2>/dev/null; echo "*/5 * * * * sudo -u cowrie aws s3 sync /home/cowrie/cowrie/var/log/cowrie/ s3://honeypot-logs-sakshee/Cowrie/Singapore/ --quiet") | crontab -

echo "=== Setting Up Auto-restart on Reboot ==="
(crontab -l 2>/dev/null; echo "@reboot sleep 30 && sudo -u cowrie bash -c 'cd /home/cowrie/cowrie && source cowrie-env/bin/activate && cowrie start'") | crontab -

echo "=== Setup Complete ==="
echo "Cowrie is running on port 2222"
echo "Logs syncing to S3 every 5 minutes"
