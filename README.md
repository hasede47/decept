# DECEPTR v1 MVP - Projet Final

Ce dossier contient le projet final propre de cyberdeception et honeypot pour la Chambre des Representants du Maroc.

Derniere validation technique: 2026-06-15.

## Architecture active

```text
T-Pot Runtime
  Cowrie SSH/Telnet (ports 22/23)
  -> Filebeat forwarder TLS 1.3
  -> DECEPTR Logstash 5044
  -> Redis queue
  -> Python pipeline
  -> Elasticsearch / MySQL / MinIO
  -> Kibana / FastAPI / DECEPTR Dashboard / ElastAlert
```

Services supplementaires de deception:

- Web honeypot intranet: `http://127.0.0.1:8082`
- Dionaea HTTP/FTP/SMB/MySQL decoy: `8081`, `2121`, `1445`, `13306`
- Canary/honeytokens via API: `/api/canary/trigger/{token}`

## Dossier

```text
D:\assir\Ismagi\PFA\DECEPTR-FINAL
```

## Demarrer

```powershell
cd D:\assir\Ismagi\PFA\DECEPTR-FINAL
powershell -ExecutionPolicy Bypass -File .\start.ps1
```

## Arreter

```powershell
cd D:\assir\Ismagi\PFA\DECEPTR-FINAL
powershell -ExecutionPolicy Bypass -File .\stop.ps1
```

## Acces

| Service | URL / Port | Identifiants |
|---|---:|---|
| Dashboard DECEPTR | http://127.0.0.1:8088/index.html?v=3 | `admin / deceptr2025` |
| Kibana | http://127.0.0.1:5601 | `elastic / deceptr2025` |
| API FastAPI | http://127.0.0.1:8000/docs | JWT via dashboard |
| Web honeypot | http://127.0.0.1:8082 | faux portail, n'importe quel login est capture |
| MinIO | http://127.0.0.1:9001 | `deceptr_admin / MotDePasseMinIO2026!` |
| Cowrie SSH | `ssh root@127.0.0.1 -p 22` | honeypot |
| Cowrie Telnet | `telnet 127.0.0.1 23` | honeypot |
| Dionaea FTP | `127.0.0.1:2121` | decoy |
| Dionaea SMB | `127.0.0.1:1445` | decoy |
| Dionaea MySQL | `127.0.0.1:13306` | decoy |

## Resultat de validation

Dernier smoke test E2E:

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

Validation manuelle confirmee:

- Dashboard DECEPTR: HTTP 200
- API health/docs: HTTP 200
- Kibana: HTTP 302 vers login
- Web honeypot: HTTP 200
- Dionaea HTTP: HTTP 200
- MinIO: HTTP 200
- Filebeat vers Logstash: TLS 1.3 OK
- GeoLite2: fichier `pipeline/data/GeoLite2-City.mmdb` charge
- Honeytoken: alerte CRITICAL, MITRE `T1039`, stockage Elasticsearch + MySQL

## Documents

- `docs/architecture-fonctionnelle.md`
- `docs/architecture-reseau.md`
- `docs/architecture-technique.md`
- `docs/architecture-fonctionnelle.pdf`
- `docs/architecture-reseau.pdf`
- `docs/architecture-technique.pdf`
- `docs/architectures-deceptr.pdf`
- `docs/DECEPTR_Guide_Complet_Installation_Configuration.pdf`

## Exclusions volontaires

Le dossier final ne contient que les composants utiles a l'architecture DECEPTR. Les projets non lies et les anciens essais DECEPTR/T-Pot ne font pas partie de ce dossier final.
