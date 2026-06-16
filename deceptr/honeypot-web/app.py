"""
DECEPTR — Faux portail intranet — Chambre des Représentants du Maroc
Web honeypot: captures all HTTP access attempts and logs them to Elasticsearch.
"""

import os
import json
import logging
import datetime
from flask import Flask, request, render_template_string, redirect, url_for
import requests as req_lib

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("deceptr.web-honeypot")

ES_HOST = os.getenv("ELASTICSEARCH_HOST", "elasticsearch:9200")
ES_INDEX = "deceptr-web-honeypot"


# ── Logging helper ────────────────────────────────────────────────────────────

def log_event(event_type: str, extra: dict = {}):
    ip = request.headers.get("X-Forwarded-For", request.remote_addr)
    ua = request.headers.get("User-Agent", "unknown")
    event = {
        "@timestamp": datetime.datetime.utcnow().isoformat() + "Z",
        "src_ip": ip,
        "user_agent": ua,
        "method": request.method,
        "path": request.path,
        "args": dict(request.args),
        "event_type": event_type,
        "sensor": "web-honeypot",
        **extra,
    }
    logger.warning(f"[WEB-HP] {event_type} from {ip} path={request.path}")
    try:
        req_lib.post(
            f"http://{ES_HOST}/{ES_INDEX}/_doc",
            json=event, timeout=2,
            auth=("elastic", os.getenv("ELASTIC_PASSWORD", ""))
        )
    except Exception:
        pass  # Never crash the honeypot because of logging failure


# ── Templates ─────────────────────────────────────────────────────────────────

LOGIN_TEMPLATE = """
<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="UTF-8">
  <title>Intranet — Chambre des Représentants</title>
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body { font-family: Arial, sans-serif; background: #f0f0f0; }
    .header { background: #006233; color: white; padding: 15px 30px; display: flex; align-items: center; }
    .header h1 { font-size: 1.2em; margin: 0; }
    .container { max-width: 400px; margin: 80px auto; background: white;
                 padding: 40px; border-radius: 4px; box-shadow: 0 2px 8px rgba(0,0,0,.2); }
    h2 { color: #006233; margin-bottom: 24px; }
    label { display: block; margin-bottom: 4px; font-weight: bold; font-size: .9em; color: #555; }
    input { width: 100%; padding: 10px; margin: 0 0 16px; border: 1px solid #ccc;
            border-radius: 3px; }
    button { width: 100%; padding: 12px; background: #006233; color: white;
             border: none; border-radius: 3px; cursor: pointer; font-size: 1em; }
    button:hover { background: #004d26; }
    .error { color: red; font-size: .9em; margin-bottom: 16px; }
    .footer { text-align: center; color: #888; font-size: .8em; margin-top: 20px; }
  </style>
</head>
<body>
  <div class="header">
    <h1>🇲🇦 Chambre des Représentants — Portail Intranet</h1>
  </div>
  <div class="container">
    <h2>Connexion sécurisée</h2>
    {% if error %}
    <p class="error">{{ error }}</p>
    {% endif %}
    <form method="POST" action="/login">
      <label>Identifiant</label>
      <input type="text" name="username" placeholder="nom.prénom@parl.ma" required>
      <label>Mot de passe</label>
      <input type="password" name="password" required>
      <button type="submit">Se connecter</button>
    </form>
    <p class="footer">Accès réservé au personnel autorisé.<br>Toute tentative non autorisée est enregistrée.</p>
  </div>
</body>
</html>
"""

FAKE_DASHBOARD = """
<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="UTF-8">
  <title>Intranet — Tableau de bord</title>
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body { font-family: Arial, sans-serif; background: #f5f5f5; }
    .header { background: #006233; color: white; padding: 15px 30px; }
    .content { max-width: 900px; margin: 40px auto; }
    .card { background: white; padding: 20px; margin: 16px 0;
            border-radius: 4px; box-shadow: 0 1px 4px rgba(0,0,0,.1); }
    h3 { color: #006233; margin-bottom: 12px; }
    ul { padding-left: 20px; }
    li { margin-bottom: 8px; }
    a { color: #006233; }
    .badge { background: #dc3545; color: white; padding: 2px 8px;
             border-radius: 10px; font-size: .8em; }
  </style>
</head>
<body>
  <div class="header"><h2>🇲🇦 Intranet — Bienvenue</h2></div>
  <div class="content">
    <div class="card">
      <h3>📁 Documents récents</h3>
      <ul>
        <li><a href="/docs/budget">Budget_2025_Confidentiel.xlsx</a> <span class="badge">CONFIDENTIEL</span></li>
        <li><a href="/docs/pv">PV_Session_Pleniere_Mars_2025.docx</a></li>
        <li><a href="/docs/rapport">Rapport_Commission_Finances_Q1.pdf</a></li>
        <li><a href="/docs/membres">Liste_Membres_Parlement_2025.xlsx</a> <span class="badge">INTERNE</span></li>
      </ul>
    </div>
    <div class="card">
      <h3>🔗 Accès rapide</h3>
      <ul>
        <li><a href="/admin">Panneau d'administration</a></li>
        <li><a href="/backup">Sauvegardes système</a></li>
        <li><a href="/users">Gestion des utilisateurs</a></li>
      </ul>
    </div>
  </div>
</body>
</html>
"""


# ── Routes ────────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    log_event("homepage_visit")
    return render_template_string(LOGIN_TEMPLATE)


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")
        log_event("login_attempt", {"username": username, "password": password})
        # Always fail — show fake dashboard to keep attacker engaged
        if len(username) > 0 and len(password) > 0:
            return render_template_string(FAKE_DASHBOARD)
        return render_template_string(LOGIN_TEMPLATE, error="Identifiants incorrects.")
    log_event("login_page_visit")
    return render_template_string(LOGIN_TEMPLATE)


@app.route("/admin")
def admin():
    log_event("admin_panel_access")
    return render_template_string(LOGIN_TEMPLATE, error="Session expirée. Veuillez vous reconnecter.")


@app.route("/docs/<doc_name>")
def fake_doc(doc_name):
    log_event("document_access", {"doc_name": doc_name})
    return "Chargement du document...", 200


@app.route("/backup")
def backup():
    log_event("backup_access_attempt")
    return "403 Forbidden", 403


@app.route("/users")
def users():
    log_event("user_management_access")
    return render_template_string(LOGIN_TEMPLATE, error="Accès refusé.")


# Catch-all — log every probe
@app.route("/<path:path>", methods=["GET", "POST", "PUT", "DELETE"])
def catch_all(path):
    log_event("unknown_path_probe", {"probed_path": f"/{path}"})
    return "404 Not Found", 404


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=False)
