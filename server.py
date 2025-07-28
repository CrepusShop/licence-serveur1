from flask import Flask, request, jsonify, render_template_string, redirect, url_for, session
from datetime import datetime
import json
import os
import secrets

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)  # clé secrète pour la session

ADMIN_PASSWORD = "admin123"  # 🔒 change ce mot de passe ici

# HTML : Page d'accueil (formulaire de vérification)
html_form = '''
<!DOCTYPE html>
<html>
<head><title>Vérification de licence</title></head>
<body>
    <h2>Vérifier une licence</h2>
    <form method="POST">
        <input type="text" name="key" placeholder="Entrez votre clé" required />
        <button type="submit">Vérifier</button>
    </form>
    {% if result %}
        <p><strong>Résultat :</strong> {{ result }}</p>
    {% endif %}
    <p><a href="/admin">Accès Admin 🔐</a></p>
</body>
</html>
'''

# HTML : Login admin
html_login = '''
<h2>Connexion Admin</h2>
<form method="POST">
    <input type="password" name="password" placeholder="Mot de passe" required />
    <button type="submit">Connexion</button>
</form>
{% if error %}<p style="color:red">{{ error }}</p>{% endif %}
'''

# HTML : Panneau Admin
html_admin = '''
<h2>Panneau Admin</h2>
<form method="POST">
    <input type="text" name="key" placeholder="Nouvelle clé" required />
    <input type="text" name="user" placeholder="Nom d'utilisateur" required />
    <input type="date" name="expires" required />
    <button type="submit">Ajouter la clé</button>
</form>
{% if message %}
<p style="color:green">{{ message }}</p>
{% endif %}
<h3>Licences enregistrées :</h3>
<ul>
{% for k, v in licenses.items() %}
    <li><strong>{{ k }}</strong> – {{ v.user }} – expire le {{ v.expires }}</li>
{% endfor %}
</ul>
<p><a href="/">Retour</a></p>
'''

def load_licenses():
    with open("licenses.json", "r") as f:
        return json.load(f)

def save_licenses(licenses):
    with open("licenses.json", "w") as f:
        json.dump(licenses, f, indent=2)

@app.route("/", methods=["GET", "POST"])
def home():
    result = None
    if request.method == "POST":
        key = request.form.get("key")
        licenses = load_licenses()
        if key not in licenses:
            result = "❌ Clé inconnue"
        else:
            expires = datetime.strptime(licenses[key]["expires"], "%Y-%m-%d")
            if datetime.today() <= expires:
                result = "✅ Licence valide"
            else:
                result = "❌ Licence expirée"
    return render_template_string(html_form, result=result)

@app.route("/check", methods=["POST"])
def check_license():
    licenses = load_licenses()
    data = request.get_json()
    key = data.get("key")
    if key not in licenses:
        return jsonify({"status": "error", "message": "Clé inconnue"}), 404
    expires = datetime.strptime(licenses[key]["expires"], "%Y-%m-%d")
    if datetime.today() <= expires:
        return jsonify({"status": "ok", "message": "Licence valide"}), 200
    else:
        return jsonify({"status": "expired", "message": "Licence expirée"}), 403

@app.route("/admin", methods=["GET", "POST"])
def admin():
    if not session.get("logged_in"):
        return redirect(url_for("admin_login"))
    licenses = load_licenses()
    message = None
    if request.method == "POST":
        key = request.form.get("key")
        user = request.form.get("user")
        expires = request.form.get("expires")
        licenses[key] = {"user": user, "expires": expires}
        save_licenses(licenses)
        message = f"✅ Clé '{key}' ajoutée."
    return render_template_string(html_admin, licenses=licenses, message=message)

@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    error = None
    if request.method == "POST":
        password = request.form.get("password")
        if password == ADMIN_PASSWORD:
            session["logged_in"] = True
            return redirect(url_for("admin"))
        else:
            error = "❌ Mot de passe incorrect"
    return render_template_string(html_login, error=error)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)