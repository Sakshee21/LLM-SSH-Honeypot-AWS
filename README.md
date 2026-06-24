# LLM-SSH-Honeypot-AWS

# LLM-SSH-Honeypot-AWS

A research project deploying adaptive LLM-powered SSH honeypots 
on AWS to study real-world attacker behaviour, compare LLM backends, 
and evaluate deception effectiveness across geographic regions.

Built as part of the Cyber Defenders Internship — Track 5.

---

## What This Project Does

Deploys fake SSH servers (honeypots) on AWS that lure real attackers
and log everything they do. Unlike traditional static honeypots,
this system uses Large Language Models (LLMs) to generate realistic
dynamic responses, making the deception more convincing and collecting
richer threat intelligence.

---

## Research Questions

1. Do LLM-powered honeypots produce richer telemetry than static ones?
2. Does a smarter LLM (Claude Haiku) outperform a free one (Gemini)?
3. Do SSH attack patterns differ across geographic regions?
4. Does cross-session persistence increase attacker engagement?

---

## Tech Stack

| Component | Tool |
|---|---|
| Cloud | AWS EC2 |
| Honeypot Framework | Cowrie (baseline) → Beelzebub (LLM) |
| LLM Backend | Gemini API (free) / Claude Haiku |
| Session State | Redis |
| Logging | CloudWatch + S3 |
| Dashboard | Grafana |
| Language | Python |

---

## Related Work

- Otal & Canbaz (2024) — LLM Honeypot
- Malhotra (2025) — LLMHoney
- Wang et al. (2024) — HoneyGPT
- Var Naseri et al. (2026) — Q-Cowrie
- Sladic et al. (2025) — VelLMes

## Contributor

Sakshee Ujjwal Kumat