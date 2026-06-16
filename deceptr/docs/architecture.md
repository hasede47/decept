# DECEPTR v1 - Architecture MVP Validee

Mise a jour: 2026-06-15.

## Schema general

```text
Attaquants / Bots / Scanners / Utilisateurs internes malveillants
   |
   +--> T-Pot Cowrie SSH/Telnet (22/23)
   |       -> Filebeat TLS 1.3
   |       -> Logstash 5044
   |
   +--> Web honeypot intranet (8082)
   |
   +--> Dionaea decoys FTP/HTTP/SMB/MySQL (2121/8081/1445/13306)
           |
           v
Redis Queue -> Python Pipeline
   |
   +--> Normalisation
   +--> GeoLite2 / VirusTotal / AbuseIPDB / Feodo
   +--> Correlation MITRE ATT&CK
   +--> Risk scoring
   +--> Detection et alertes
   |
   +--> Elasticsearch: cowrie-*, deceptr-events-*, deceptr-web-honeypot
   +--> MySQL: alerts, iocs, attackers, campaigns, honeytokens, users
   +--> MinIO: reports, backups, malware-samples, attachments
   |
   +--> Kibana / FastAPI / Dashboard DECEPTR / ElastAlert
```

## Pipeline

| # | Etape | Fichier | Role |
|---|---|---|---|
| 1 | Collecte | `collector.py` | Lit Redis `deceptr:events`, fallback `cowrie-*` |
| 2 | Normalisation | `normalizer.py` | Convertit les logs en schema DECEPTR |
| 3 | Enrichissement | `enricher.py` | GeoLite2, VirusTotal, AbuseIPDB, Feodo |
| 4 | Correlation | `correlator.py` | Campagnes, MITRE ATT&CK, contexte |
| 5 | Scoring | `risk_scorer.py` | Score de risque 0-100 |
| 6 | Detection | `detector.py` | Brute force, commandes, malware, honeytokens, web login |
| 7 | Sorties | `storage.py`, `alerter.py` | Elasticsearch, MySQL, MinIO, notifications |

## Stockage

**Elasticsearch**

- `cowrie-*`: logs bruts issus de T-Pot/Cowrie.
- `deceptr-events-*`: evenements enrichis par le pipeline.
- `deceptr-web-honeypot`: acces et tentatives sur le faux portail intranet.

**MySQL**

- `alerts`: alertes SOC.
- `iocs`: indicateurs par IP.
- `attackers`: profil des attaquants.
- `campaigns`: regroupement par IP et techniques.
- `honeytokens`: canary tokens declenches.
- `users`: comptes dashboard/API.
- `rapports_dgssi`: historique des rapports.

**MinIO**

- `reports`
- `backups`
- `malware-samples`
- `attachments`

## Ports actifs en lab

| Service | Port |
|---|---:|
| Cowrie SSH | 22 |
| Cowrie Telnet | 23 |
| Logstash Beats TLS | 5044 |
| Dashboard DECEPTR | 8088 |
| API FastAPI | 8000 |
| Kibana | 5601 |
| Elasticsearch | 9200 |
| Web honeypot | 8082 |
| Dionaea FTP | 2121 |
| Dionaea HTTP | 8081 |
| Dionaea SMB | 1445 |
| Dionaea MySQL | 13306 |
| MinIO API/Console | 9000/9001 |

## Validation

Dernier test E2E:

```json
{
  "status": "OK",
  "tpot_cowrie": "running",
  "tpot_forwarder_tls": "TLSv1.3",
  "raw_index": "cowrie-2026.06",
  "enriched_index": "deceptr-events-2026.06",
  "enriched_type": "login_attempt",
  "mitre": "T1110",
  "api_total_alerts": 161,
  "api_alerts_24h": 80
}
```

## Acces

| Service | URL | Identifiants |
|---|---|---|
| Dashboard | `http://127.0.0.1:8088/index.html?v=3` | `admin / deceptr2025` |
| Kibana | `http://127.0.0.1:5601` | `elastic / deceptr2025` |
| API Docs | `http://127.0.0.1:8000/docs` | JWT |
| Web honeypot | `http://127.0.0.1:8082` | faux login capture |
| MinIO | `http://127.0.0.1:9001` | `deceptr_admin / MotDePasseMinIO2026!` |

## Perspectives post-MVP

- Deploiement physique en DMZ avec pfSense/FortiGate.
- VPN/MFA obligatoire pour SOC et admin.
- SMTP reel pour notification.
- Cles API officielles VirusTotal et AbuseIPDB.
- Durcissement secrets via Vault ou gestionnaire equivalent.
