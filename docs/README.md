# Documents DECEPTR v1 MVP

Ce dossier contient les livrables documentaires du projet final DECEPTR.

Mise a jour: 2026-06-15, apres validation du stack complet T-Pot/Cowrie, Filebeat TLS 1.3, Logstash, Redis, pipeline, Elasticsearch, MySQL, MinIO, Kibana, API, dashboard, web honeypot, Dionaea et honeytokens.

| Document | Description |
|---|---|
| `architecture-fonctionnelle.md` | Couches fonctionnelles, pipeline de traitement, flux de donnees et acteurs |
| `architecture-reseau.md` | Zones reseau, ports, flux autorises et correspondance Docker |
| `architecture-technique.md` | Services Docker, images, ports, stockage, fichiers et commandes |

Versions PDF:

| PDF | Description |
|---|---|
| `architecture-fonctionnelle.pdf` | Architecture fonctionnelle |
| `architecture-reseau.pdf` | Architecture reseau |
| `architecture-technique.pdf` | Architecture technique |
| `architectures-deceptr.pdf` | Document combine avec les trois architectures |
| `DECEPTR_Guide_Complet_Installation_Configuration.pdf` | Guide complet type dossier projet: build de zero, architecture, installation manuelle, configuration manuelle, tests, exploitation et checklist |

Ces documents correspondent au dossier final:

```text
D:\assir\Ismagi\PFA\DECEPTR-FINAL
```

Acces principaux valides:

| Service | URL |
|---|---|
| Dashboard DECEPTR | http://127.0.0.1:8088/index.html?v=3 |
| Kibana | http://127.0.0.1:5601 |
| API Docs | http://127.0.0.1:8000/docs |
| Web honeypot | http://127.0.0.1:8082 |
| MinIO | http://127.0.0.1:9001 |

Regenerer les PDF:

```powershell
cd D:\assir\Ismagi\PFA\DECEPTR-FINAL\docs
node .\build-pdfs.js
python .\generate-visual-architecture-pdfs.py
python .\build-deceptr-complete-guide.py
python .\docx-guide-to-reportlab-pdf.py
```
