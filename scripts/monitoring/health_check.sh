#!/bin/bash
# Health check script for Cowrie honeypot
# Run this to verify everything is working

echo "=== Cowrie Health Check ==="
echo "Time: $(date -u)"
echo ""

# Check if cowrie process is running
if pgrep -f "twistd" > /dev/null; then
    echo "Cowrie: RUNNING"
else
    echo "Cowrie: NOT RUNNING"
fi

# Check if port 2222 is listening
if ss -tlnp | grep -q 2222; then
    echo "Port 2222: LISTENING"
else
    echo "Port 2222: NOT LISTENING"
fi

# Count today's connections
TODAY=$(date -u +%Y-%m-%dT)
CONNECTIONS=$(sudo -u cowrie grep -c "session.connect" \
/home/cowrie/cowrie/var/log/cowrie/cowrie.json 2>/dev/null || echo 0)
echo "📡 Total connections logged: $CONNECTIONS"

# Count login attempts
LOGINS=$(sudo -u cowrie grep -c "login.failed\|login.success" \
/home/cowrie/cowrie/var/log/cowrie/cowrie.json 2>/dev/null || echo 0)
echo "Login attempts: $LOGINS"

# Check S3 sync
echo ""
echo "=== S3 Status ==="
aws s3 ls s3://honeypot-logs-sakshee/Cowrie/Singapore/ \
--human-readable 2>/dev/null | tail -3

echo ""
echo "=== Done ==="
