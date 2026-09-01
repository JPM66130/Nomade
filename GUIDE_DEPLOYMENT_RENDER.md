# 🚀 Guide de déploiement sur Render

Ce guide explique **pas à pas** comment déployer l'API AllRoad's / Nomade sur [Render.com](https://render.com) — totalement gratuit, sans carte de crédit requise.

---

## 📋 Prérequis

- Un compte GitHub avec le dépôt `JPM66130/Nomade`
- Un navigateur web

Temps estimé : **5 à 10 minutes** ⏱️

---

## Étape 1 — Créer un compte Render

1. Ouvrez [https://render.com](https://render.com) dans votre navigateur.
2. Cliquez sur **"Get Started for Free"**.
3. Sélectionnez **"Continue with GitHub"** (recommandé).
4. Autorisez Render à accéder à votre compte GitHub.
5. Votre compte est créé ! 🎉

---

## Étape 2 — Créer un nouveau service Web

1. Dans le tableau de bord Render, cliquez sur **"+ New"** puis **"Web Service"**.
2. Choisissez **"Build and deploy from a Git repository"**.
3. Cliquez sur **"Connect account"** (GitHub) si ce n'est pas encore connecté.
4. Cherchez le dépôt **`JPM66130/Nomade`** dans la liste.
5. Cliquez sur **"Connect"** en face du dépôt.

---

## Étape 3 — Configurer le service

Remplissez les champs comme suit :

| Champ | Valeur |
|-------|--------|
| **Name** | `allroads-api` (ou ce que vous voulez) |
| **Region** | `Frankfurt (EU Central)` |
| **Branch** | `main` |
| **Runtime** | `Docker` |
| **Instance Type** | `Free` |

> Render détectera automatiquement le `Dockerfile` à la racine du projet.

---

## Étape 4 — Variables d'environnement

Dans la section **"Environment Variables"**, ajoutez :

| Clé | Valeur |
|-----|--------|
| `ENVIRONMENT` | `production` |
| `PORT` | `8000` |

> Ces variables sont déjà définies dans le fichier `render.yaml`. Render les lit automatiquement.

---

## Étape 5 — Lancer le déploiement

1. Cliquez sur **"Create Web Service"**.
2. Render va :
   - Cloner votre dépôt GitHub ✅
   - Construire l'image Docker ✅
   - Lancer l'API avec uvicorn ✅
3. Attendez environ **2 à 3 minutes**.
4. Une URL publique apparaît en haut de la page, par exemple :
   ```
   https://allroads-api.onrender.com
   ```

---

## Étape 6 — Tester l'API

Ouvrez votre navigateur et testez ces URLs :

| Endpoint | URL |
|----------|-----|
| 🏠 Accueil | `https://allroads-api.onrender.com/` |
| 📚 Documentation | `https://allroads-api.onrender.com/docs` |
| 🌍 Pays | `https://allroads-api.onrender.com/pays` |
| ⛽ Stations | `https://allroads-api.onrender.com/stations` |
| 🅿️ Parkings | `https://allroads-api.onrender.com/parkings` |
| 🏕️ Spots | `https://allroads-api.onrender.com/spots` |
| ⚠️ Alertes | `https://allroads-api.onrender.com/alertes` |

La réponse attendue pour `/` :
```json
{
  "status": "ok",
  "message": "API Nomade / AllRoad's opérationnelle"
}
```

---

## Étape 7 — Déploiement automatique (bonus)

Chaque fois que vous faites un `git push` sur la branche `main`, Render redéploie automatiquement votre API. Aucune action manuelle requise ! 🎉

---

## 🔧 Dépannage

### ❌ Le déploiement échoue (build error)

**Cause probable** : `requirements.txt` manquant ou erreur de syntaxe.

**Solution** :
1. Vérifiez que `requirements.txt` est bien à la racine du projet.
2. Vérifiez les logs de build dans Render (onglet **"Logs"**).
3. Corrigez l'erreur et faites un `git push`.

---

### ❌ L'API répond avec une erreur 502

**Cause probable** : L'API ne démarre pas sur le bon port.

**Solution** :
- Vérifiez que le `Dockerfile` contient bien :
  ```dockerfile
  CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
  ```
- Vérifiez que la variable `PORT=8000` est bien définie dans Render.

---

### ❌ L'API est lente au premier appel

**Cause** : Le plan gratuit Render "endort" le service après 15 minutes d'inactivité.

**Solution** :
- Attendez 30 secondes pour que le service se "réveille".
- Pour éviter ça, passez à un plan payant ($7/mois) ou utilisez un service de ping automatique.

---

### ❌ Mes modifications ne sont pas prises en compte

**Solution** :
1. Vérifiez que vous avez bien fait `git push origin main`.
2. Dans Render, cliquez sur **"Manual Deploy"** → **"Deploy latest commit"**.

---

## 📞 Besoin d'aide ?

- 📖 Documentation Render : [https://render.com/docs](https://render.com/docs)
- 💬 Issues GitHub : [https://github.com/JPM66130/Nomade/issues](https://github.com/JPM66130/Nomade/issues)
- 📧 Support Render : [https://render.com/support](https://render.com/support)

---

*Guide rédigé pour le projet AllRoad's / Nomade – Déploiement simplifié sur Render 🚀*
