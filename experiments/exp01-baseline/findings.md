# Experiment 01 — Static Cowrie Baseline

## Setup
- Honeypot: Cowrie v3.0.5 (no LLM)
- Region: Singapore (ap-southeast-1)
- Start date: 24 June 2026
- Instance: t3.micro

## Purpose
Establish baseline engagement metrics before
introducing LLM-powered responses.
This is the control group for the experiment.

## Metrics Being Collected
- Unique IPs per day
- Session duration
- Login attempts
- Commands executed
- Client versions / HASSH fingerprints
- Geographic distribution

## Day 1 Results (27 June 2026)
- Unique IPs: 5
- Total sessions: 8
- Successful logins: 0
- Commands: 0
- Notable: MGLNDD fingerprinting detected
- Notable: 120s timeout = Cowrie fingerprint
  (fixed: changed to 137s)

## Ongoing Observations
(Update daily as data comes in)
