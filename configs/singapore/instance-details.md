# Singapore Instance — honeypot-sg-01

## Instance Details
- Instance ID: i-0fa87caadc3d7c3dc
- Region: ap-southeast-1 (Singapore)
- Instance type: t3.micro
- OS: Ubuntu 26.04 LTS
- Elastic IP: [your elastic IP]
- Port 22: management (your IP only)
- Port 2222: honeypot (open to all)

## Software
- Cowrie v3.0.5.dev63
- Python 3.14.4
- AWS CLI 2.31.35

## S3 Logging
- Bucket: honeypot-logs-sakshee
- Path: Cowrie/Singapore/
- Sync frequency: every 5 minutes via cron

## Cron Jobs
```bash
# S3 sync every 5 minutes
*/5 * * * * sudo -u cowrie aws s3 sync \
/home/cowrie/cowrie/var/log/cowrie/ \
s3://honeypot-logs-sakshee/Cowrie/Singapore/ --quiet

# Auto-restart on reboot
@reboot sleep 30 && sudo -u cowrie bash -c \
'cd /home/cowrie/cowrie && \
source cowrie-env/bin/activate && cowrie start'
```
