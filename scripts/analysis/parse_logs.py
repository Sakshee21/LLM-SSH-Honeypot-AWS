#!/usr/bin/env python3
"""
Cowrie Log Analyser
Parses Cowrie JSON logs and produces a summary report.
Usage: python3 parse_logs.py <path-to-cowrie.json>
"""

import json
import sys
from collections import defaultdict
from datetime import datetime

def parse_cowrie_json(filepath):
    events = []
    with open(filepath, 'r') as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    events.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    return events

def analyse(events):
    # Counters
    connections = defaultdict(list)
    login_attempts = []
    commands = []
    client_versions = defaultdict(int)
    fingerprints = defaultdict(int)

    for event in events:
        eventid = event.get('eventid', '')
        src_ip = event.get('src_ip', 'unknown')

        if eventid == 'cowrie.session.connect':
            connections[src_ip].append(event)

        elif eventid == 'cowrie.login.failed':
            login_attempts.append({
                'ip': src_ip,
                'username': event.get('username'),
                'password': event.get('password'),
                'timestamp': event.get('timestamp')
            })

        elif eventid == 'cowrie.login.success':
            login_attempts.append({
                'ip': src_ip,
                'username': event.get('username'),
                'password': event.get('password'),
                'timestamp': event.get('timestamp'),
                'success': True
            })

        elif eventid == 'cowrie.command.input':
            commands.append({
                'ip': src_ip,
                'command': event.get('input'),
                'timestamp': event.get('timestamp')
            })

        elif eventid == 'cowrie.client.version':
            version = event.get('version', 'unknown')
            client_versions[version] += 1

        elif eventid == 'cowrie.client.kex':
            hassh = event.get('hassh', 'unknown')
            fingerprints[hassh] += 1

    return {
        'connections': connections,
        'login_attempts': login_attempts,
        'commands': commands,
        'client_versions': client_versions,
        'fingerprints': fingerprints
    }

def print_report(data, filepath):
    connections = data['connections']
    login_attempts = data['login_attempts']
    commands = data['commands']
    client_versions = data['client_versions']
    fingerprints = data['fingerprints']

    print("=" * 60)
    print("COWRIE HONEYPOT — ANALYSIS REPORT")
    print(f"File: {filepath}")
    print(f"Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}")
    print("=" * 60)

    print(f"\nCONNECTIONS")
    print(f"   Unique IPs:        {len(connections)}")
    print(f"   Total sessions:    {sum(len(s) for s in connections.values())}")

    print(f"\nATTACKING IPs")
    for ip, sessions in sorted(connections.items(),
                                key=lambda x: len(x[1]),
                                reverse=True):
        print(f"   {ip:<20} {len(sessions)} session(s)")

    print(f"\nLOGIN ATTEMPTS: {len(login_attempts)}")
    if login_attempts:
        successful = [l for l in login_attempts if l.get('success')]
        print(f"   Successful:  {len(successful)}")
        print(f"   Failed:      {len(login_attempts) - len(successful)}")
        print(f"\n   Top credentials tried:")
        cred_count = defaultdict(int)
        for attempt in login_attempts:
            key = f"{attempt['username']} / {attempt['password']}"
            cred_count[key] += 1
        for cred, count in sorted(cred_count.items(),
                                   key=lambda x: x[1],
                                   reverse=True)[:10]:
            print(f"   {count:>3}x  {cred}")

    print(f"\nCOMMANDS EXECUTED: {len(commands)}")
    if commands:
        cmd_count = defaultdict(int)
        for cmd in commands:
            cmd_count[cmd['command']] += 1
        print(f"   Top commands:")
        for cmd, count in sorted(cmd_count.items(),
                                  key=lambda x: x[1],
                                  reverse=True)[:10]:
            print(f"   {count:>3}x  {cmd}")

    print(f"\nCLIENT VERSIONS")
    for version, count in sorted(client_versions.items(),
                                  key=lambda x: x[1],
                                  reverse=True):
        print(f"   {count:>3}x  {version}")

    print(f"\nHASSH FINGERPRINTS")
    for hassh, count in sorted(fingerprints.items(),
                                key=lambda x: x[1],
                                reverse=True):
        print(f"   {count:>3}x  {hassh}")

    print("\n" + "=" * 60)

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 parse_logs.py <cowrie.json>")
        sys.exit(1)

    filepath = sys.argv[1]
    events = parse_cowrie_json(filepath)
    data = analyse(events)
    print_report(data, filepath)

if __name__ == '__main__':
    main()
