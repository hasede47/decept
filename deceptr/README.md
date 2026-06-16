# DECEPTR v1 - Plateforme de Cyberdeception

Projet PFA - ISMAGI Rabat - Chambre des Representants du Maroc.

Etat valide: 2026-06-15.

## Stack technique

- Honeypots: T-Pot/Cowrie SSH-Telnet, web honeypot intranet, Dionaea.
- Collecte: Filebeat, Logstash TLS 1.3.
- Queue: Redis.
- Pipeline: Python 3.11, normalisation, enrichissement, MITRE, scoring, detection.
- Threat intelligence: GeoLite2, VirusTotal, AbuseIPDB, Feodo Tracker, MITRE ATT&CK.
- Stockage: Elasticsearch, MySQL 8, MinIO.
- Visualisation: Kibana, dashboard HTML DECEPTR.
- Alerting: ElastAlert 2 et alerter pipeline.
- API: FastAPI avec JWT.
- Deploiement: Docker Compose.

## Demarrage recommande

Depuis le dossier final:

```powershell
cd D:\assir\Ismagi\PFA\DECEPTR-FINAL
powershell -ExecutionPolicy Bypass -File .\start.ps1
```

Arret:

```powershell
cd D:\assir\Ismagi\PFA\DECEPTR-FINAL
powershell -ExecutionPolicy Bypass -File .\stop.ps1
```

## Acces

| Service | URL / Port | Identifiants |
|---|---|---|
| Dashboard | http://127.0.0.1:8088/index.html?v=3 | `admin / deceptr2025` |
| API Docs | http://127.0.0.1:8000/docs | JWT |
| Kibana | http://127.0.0.1:5601 | `elastic / deceptr2025` |
| MinIO | http://127.0.0.1:9001 | `deceptr_admin / MotDePasseMinIO2026!` |
| Web honeypot | http://127.0.0.1:8082 | faux login capture |
| Cowrie SSH | `ssh root@127.0.0.1 -p 22` | honeypot |
| Cowrie Telnet | `telnet 127.0.0.1 23` | honeypot |
| Dionaea FTP | `127.0.0.1:2121` | decoy |
| Dionaea HTTP | http://127.0.0.1:8081 | decoy |
| Dionaea SMB | `127.0.0.1:1445` | decoy |
| Dionaea MySQL | `127.0.0.1:13306` | decoy |

## Fichiers importants

```text
deceptr/
  docker-compose.yml
  docker-compose.tpot.yml
  honeypot-web/
  dionaea/
  elk/
  mysql/
  pipeline/
  dashboard/
  scripts/e2e-smoke.ps1
  docs/
```

Le dossier ancien `web-honeypot` n'est plus utilise. Le service actif est `honeypot-web`.

## GeoLite2

Le fichier GeoLite2 est place ici:

```text
pipeline/data/GeoLite2-City.mmdb
```

Il a ete teste dans le conteneur pipeline et permet l'enrichissement geographique local.

## Tests

Test complet:

```powershell
cd D:\assir\Ismagi\PFA\DECEPTR-FINAL\deceptr
powershell -ExecutionPolicy Bypass -File .\scripts\e2e-smoke.ps1 -ProjectRoot . -TpotRoot ..\tpot-runtime -WaitSeconds 45
```

Resultat attendu:

```json
{
  "status": "OK",
  "tpot_cowrie": "running",
  "tpot_forwarder_tls": "TLSv1.3",
  "raw_index": "cowrie-2026.06",
  "enriched_index": "deceptr-events-2026.06",
  "enriched_type": "login_attempt",
  "mitre": "T1110"
}
```

Test canary:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/api/canary/trigger/test-canary
```

Un evenement `honeytoken_triggered` doit apparaitre avec severite `CRITICAL` et MITRE `T1039`.

## Documents

Les livrables sont dans:

```text
D:\assir\Ismagi\PFA\DECEPTR-FINAL\docs
```

Ils contiennent l'architecture fonctionnelle, reseau, technique et le guide complet d'installation/configuration.
