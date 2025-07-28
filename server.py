from flask import Flask, request, jsonify, render_template_string
from datetime import datetime
import json
import os

app = Flask(__name__)

# HTML pour le formulaire web
html_form = '''
<!DOCTYPE html>
<html>
<head>
    <title>Vérification de licence</title>
</head>
<body>
    <h2>Vérifier une licence</h2>
    <form method="POST">
        <input type="text" name="key" placeholder="Entrez votre clé" required />
        <button type="submit">Vérifier</button>
    </form>
    {% if result %}
        <p><strong>Résultat :</strong> {{ result }}</p>
    {% endif %}
</body>
</html>
'''

def load_licenses():
    with open("licenses.json", "r") as f:
        return json.load(f)

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
            today = datetime.today()
            if today <= expires:
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
    today = datetime.today()

    if today <= expires:
        return jsonify({"status": "ok", "message": "Licence valide"}), 200
    else:
        return jsonify({"status": "expired", "message": "Licence expirée"}), 403

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)