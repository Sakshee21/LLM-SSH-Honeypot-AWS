# Setup Log — LLM SSH Honeypot on AWS

A detailed journal of everything done, explained simply.
Written so that anyone (including future me) can understand
and reproduce this setup from scratch.

---

## Date: 24 June 2026

---

## What is SSH?

SSH stands for Secure Shell. It is a protocol that lets you
remotely control another computer through a terminal — as if
you were physically sitting in front of it.

Without SSH:
You physically sit at a server → type commands → server responds

With SSH:
You open terminal on laptop → connect over internet →
type commands → they run on remote server → you see output

Everything is encrypted so nobody can intercept your commands.

### How SSH Authentication Works

There are two ways to prove who you are:

Method 1 — Password (weak):
ssh user@server-ip
Enter password: ••••••••

Method 2 — Key Pair (what we use):
Private key (.pem file) → stays on YOUR laptop, never shared
Public key → lives on the server
When you connect, your laptop proves it has the private key
Server checks if it matches → access granted, no password needed

### Why Attackers Target SSH

SSH runs on port 22 on almost every Linux server in the world.
Attackers know this. Common attack patterns:

1. Credential Brute Force
   Bots fire thousands of username/password combinations:
   root/123456, root/password, admin/admin...
   hoping one works

2. Exploit Known Vulnerabilities
   Old SSH versions have known bugs
   Attacker checks your SSH version and tries known exploits

3. Stolen Key Attack
   Attacker finds a private key accidentally uploaded to GitHub
   Uses it to connect

### Two SSH Connections in This Project

Connection 1 — Me managing my server (real SSH):
You → WSL terminal → ssh -i honeypot-key.pem ubuntu@18.141.156.207
I am the admin, this is legitimate

Connection 2 — Attackers hitting the honeypot (fake SSH):
Bot → finds port 2222 open → tries credentials → gets in
They think they are in a real server
They are actually talking to Cowrie (a fake shell)
Everything they do is logged, nothing real is accessed

---

## What is AWS EC2?

EC2 stands for Elastic Compute Cloud.
It is basically a virtual computer you rent from Amazon.
It runs in Amazon's data centres around the world.
You pay per hour for as long as it runs.

### Instance Types

t3.micro:
├── 1 vCPU
├── 1 GB RAM
└── Free tier eligible (750 hours/month)

This is what we are using. Small but enough for a honeypot.

---

## EC2 Instance Setup

### What We Created
- Name: honeypot-sg-01
- Region: ap-southeast-1 (Singapore)
- OS: Ubuntu 26.04 LTS
- Instance type: t3.micro
- Key pair: honeypot-key-1.pem (saved locally, never share)
- Public IP: 18.141.156.207 (may change after restart)
- Instance ID: i-0fa87caadc3d7c3dc

### Security Group Rules (Firewall)
Name: honeypot-sg

Rule 1 — Management SSH:
Port: 22
Source: My IP only (106.192.167.222/32)
Reason: Only I can manage the server

Rule 2 — Honeypot:
Port: 2222
Source: Anywhere (0.0.0.0/0)
Reason: Attackers need to be able to find and connect to it

### Why Singapore?
Regional variation is a research signal.
SSH attack traffic differs by geographic region.
Singapore attracts different botnets than India or USA.
We will compare across regions later.

---

## How to SSH Into the Server

From WSL terminal on Windows laptop:

```bash
ssh -i ~/.ssh/honeypot-key-1.pem -o ServerAliveInterval=60 ubuntu@18.141.156.207
```

Breaking this down:
- ssh = the SSH command
- -i ~/.ssh/honeypot-key-1.pem = use this key file as identity
- -o ServerAliveInterval=60 = send keepalive every 60s (prevents timeout)
- ubuntu = username (Ubuntu EC2 instances use 'ubuntu')
- 18.141.156.207 = server IP (check AWS console after restart, may change)

First time connecting it asks:
"Are you sure you want to continue connecting?"
Type: yes

---

## What is Cowrie?

Cowrie is an open source SSH honeypot written in Python.
It pretends to be a real Ubuntu SSH server.
Attackers connect, think they are in a real system, run commands.
Cowrie logs everything — credentials tried, commands run, files downloaded.

### How Cowrie Works

1. Attacker finds port 2222 open
2. Tries: ssh root@18.141.156.207 -p 2222
3. Cowrie pretends to be Ubuntu, asks for password
4. Attacker tries common passwords (root/123456 etc)
5. Cowrie rejects a few, then accepts one (looks realistic)
6. Attacker thinks they are inside a real server
7. Attacker runs commands — Cowrie has a fake filesystem
8. Everything is logged to var/log/cowrie/

### Cowrie Installation Steps

```bash
# 1. Install system dependencies
sudo apt install -y git python3-virtualenv libssl-dev libffi-dev \
build-essential libpython3-dev python3-minimal authbind virtualenv python3-pip

# 2. Create dedicated user (never run as root)
sudo adduser --disabled-password cowrie

# 3. Switch to cowrie user
sudo su - cowrie

# 4. Download Cowrie
git clone http://github.com/cowrie/cowrie
cd cowrie

# 5. Create Python virtual environment
virtualenv --python=python3 cowrie-env
source cowrie-env/bin/activate

# 6. Install Python dependencies
pip install --upgrade pip
pip install -r requirements.txt

# 7. Install Cowrie as package
pip install -e .

# 8. Copy config file
cp src/cowrie/data/etc/cowrie.cfg.dist etc/cowrie.cfg

# 9. Start Cowrie
cowrie start

# 10. Verify
cowrie status
```

### How to Restart Cowrie After Instance Stop

```bash
# SSH into instance (check new IP in AWS console)
ssh -i ~/.ssh/honeypot-key-1.pem -o ServerAliveInterval=60 ubuntu@NEW-IP

# Switch to cowrie user
sudo su - cowrie

# Navigate to cowrie
cd cowrie

# Activate virtual environment
source cowrie-env/bin/activate

# Start cowrie
cowrie start

# Verify
cowrie status
```

### How to Watch Live Logs

```bash
tail -f var/log/cowrie/cowrie.log
```

Press Ctrl+C to stop watching.

---

## Next Steps

1. Set up Elastic IP (static IP that doesn't change on restart)
2. Set up S3 bucket for log storage
3. Configure CloudWatch log streaming
4. Collect baseline data for 1-2 weeks
5. Deploy Beelzebub + Gemini on new instance
6. Compare engagement metrics

---

## Date: 26 June 2026

---

## Updates — S3 Log Shipping and Elastic IP

### Elastic IP Setup
- Allocated Elastic IP from AWS console
- Associated with honeypot-sg-01 instance
- IP is now permanent and won't change on restart
- Location: EC2 → Network & Security → Elastic IPs

### IAM Role for S3 Access
Created IAM role to allow EC2 to write to S3:
- Role name: honeypot-ec2-s3-role
- Policy: AmazonS3FullAccess
- Attached to: honeypot-sg-01 instance
- This allows the instance to upload logs without API keys

### S3 Bucket Setup
- Bucket name: honeypot-logs-sakshee
- Region: ap-southeast-1 (Singapore)
- Folder structure: Cowrie/Singapore/
- All Cowrie logs sync here every 5 minutes

### AWS CLI Installation
```bash
sudo apt install -y awscli
aws --version
# Verify S3 access
aws s3 ls s3://honeypot-logs-sakshee/
```

### S3 Log Sync Setup
Since ubuntu user couldn't read cowrie user's files directly,
we use sudo -u cowrie to run the sync as the cowrie user:

```bash
# Manual sync command
sudo -u cowrie aws s3 sync /home/cowrie/cowrie/var/log/cowrie/ \
s3://honeypot-logs-sakshee/Cowrie/Singapore/

# Automated via cron job (runs every 5 minutes)
*/5 * * * * sudo -u cowrie aws s3 sync \
/home/cowrie/cowrie/var/log/cowrie/ \
s3://honeypot-logs-sakshee/Cowrie/Singapore/ --quiet
```

### Auto-restart on Reboot
Added cron job to start Cowrie automatically if instance reboots:
```bash
@reboot sleep 30 && sudo -u cowrie bash -c \
'cd /home/cowrie/cowrie && source cowrie-env/bin/activate && cowrie start'
```

### Current Status
- Cowrie running on port 2222
- Logs syncing to S3 every 5 minutes
- Elastic IP attached (permanent address)
- Instance left running overnight to collect attacker data

### How to Verify Everything is Working
```bash
# Check Cowrie is running
sudo su - cowrie
cd cowrie
source cowrie-env/bin/activate
cowrie status

# Check logs exist
ls var/log/cowrie/

# Check S3 sync works
exit
sudo -u cowrie aws s3 sync /home/cowrie/cowrie/var/log/cowrie/ \
s3://honeypot-logs-sakshee/Cowrie/Singapore/

# Verify files in S3
aws s3 ls s3://honeypot-logs-sakshee/Cowrie/Singapore/
```

### Security Group Note
If SSH stops working — your home IP may have changed.
Fix:
1. Go to whatismyip.com and note your current IP
2. EC2 → Security Groups → honeypot-sg → Edit inbound rules
3. Change port 22 source to My IP
4. Save rules