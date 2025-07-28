# Serveur de Licence (avec interface Web)

## Contenu
- `server.py` : serveur Flask
- `licenses.json` : liste des licences valides
- `requirements.txt` : dépendances Python

## Interface
- `/` : formulaire simple pour tester une clé
- `/check` : endpoint API POST pour vérifier une clé

## Déploiement Render
1. Crée un repo GitHub et upload les fichiers
2. Va sur [render.com](https://render.com) > New > Web Service
3. Remplis :
   - Build Command : `pip install -r requirements.txt`
   - Start Command : `python server.py`
4. Déploie

🔗 Utilise : `https://tonprojet.onrender.com/`