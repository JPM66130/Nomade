# Nomade bêta

API FastAPI pour le calcul d’itinéraire, avec moteur de routage de secours, gestion des coûts et historique local.

## Prérequis

- Python 3.11+
- Virtualenv / venv
- Accès internet pour OSRM et les prix carburants

## Installation

```bash
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```

## Variables d’environnement

En local, le projet peut lire `clé.env`. En hébergement, configurez les variables dans la plateforme et ne transférez jamais ce fichier. Un fichier `.env` local est également pris en charge.

`API_ACCESS_TOKEN` est facultatif pour les appels effectués depuis `127.0.0.1` ou `::1`. Il reste requis pour les requêtes externes lorsque cette variable est définie.

Exemple :

```env
API_ACCESS_TOKEN=mon_token_secret
ORS_API_KEY=REMPLACEZ_PAR_VOTRE_CLE_ORS
GRAPHOPPER_API_KEY=REMPLACEZ_PAR_VOTRE_CLE_GRAPHOPPER
DATABASE_URL=sqlite:///./database.db
ENVIRONMENT=development
RATE_LIMIT_PER_MINUTE=20
```

Pour une instance publique, définissez `ENVIRONMENT=production` et un `API_ACCESS_TOKEN` robuste. L'application refuse de démarrer en production si ce token est absent.
Par défaut, les requêtes API externes sont limitées à 20 par minute et par adresse IP. Ajustez `RATE_LIMIT_PER_MINUTE` selon les quotas de vos fournisseurs de routage.

## Démarrage

```bash
.\.venv\Scripts\python.exe -m uvicorn main:app --host 0.0.0.0 --port 8000
```

Puis ouvrir :

- http://127.0.0.1:8000/
- http://127.0.0.1:8000/docs
- http://127.0.0.1:8000/app/

## Fonctionnement

### Sans clé de routage

Le projet fonctionne en mode dégradé avec le fallback OSRM lorsque GraphHopper et ORS sont indisponibles.

- le calcul d’itinéraire continue et reste exploitable
- les prix carburant peuvent être chargés
- le géocodeur par adresse reste désactivé tant qu’aucune clé ORS valide n’est fournie
- l’interface affiche un message clair pour indiquer ce mode de fonctionnement

### Avec une clé GraphHopper réelle

GraphHopper devient le moteur de routage prioritaire. En cas d’indisponibilité, le projet essaie ensuite ORS puis OSRM.

- les profils vélo et voiture utilisent les véhicules GraphHopper correspondants
- les profils camping-car, poids lourd et convoi exceptionnel utilisent actuellement le profil voiture, sans restrictions de gabarit spécifiques

### Avec clé ORS réelle

Le géocodeur est réactivé et permet de convertir automatiquement une adresse en coordonnées.

## Endpoints principaux

- `GET /itineraire/calcul`
- `GET /itineraire/geocoder`
- `GET /itineraire/compteur`
- `GET /itineraire/`
- `GET /pays/`
- `GET /stations/`
- `GET /alertes/`

## Points de vigilance

- La clé ORS doit être une vraie clé valide ; les valeurs type `VOTRE_...`, `CHANGE_ME` ou `REMPLACEZ_PAR_VOTRE_CLE_ORS` sont rejetées.
- Le token API doit être renseigné pour les appels protégés.
- L’interface ne lance pas d’appels API sans token.
- Le fallback OSRM est la source de secours pour la route en mode sans clé ORS.

## État actuel

Le flux principal de calcul est validé et fonctionne en utilisation réelle dans le navigateur avec le fallback OSRM actif.

## Déploiement bêta

Une image Docker est fournie pour les plateformes qui acceptent un Dockerfile (Render, Railway, Fly.io, VPS). Pour une bêta à faible trafic, la base SQLite peut être conservée sur un volume persistant monté dans `/data` :

```env
DATABASE_URL=sqlite:////data/database.db
ENVIRONMENT=production
API_ACCESS_TOKEN=un_token_long_aleatoire
ORS_API_KEY=votre_cle_ors
GRAPHOPPER_API_KEY=votre_cle_graphhopper
```

Construire et lancer localement l'image :

```bash
docker build -t itineraire-c25 .
docker run --rm -p 8000:8000 --env-file .env -v itineraire-c25-data:/data itineraire-c25
```

En production multi-utilisateurs, préférez PostgreSQL et renseignez la chaîne fournie par l'hébergeur dans `DATABASE_URL`. Le pilote PostgreSQL est inclus dans `requirements.txt`.

### Déploiement Render

1. Publiez ce dossier dans un dépôt GitHub privé ou public, sans `clé.env` ni `.env`.
2. Dans Render, créez un service depuis ce dépôt et laissez Render détecter `render.yaml`.
3. Saisissez les valeurs secrètes `ORS_API_KEY` et `GRAPHOPPER_API_KEY` dans Render. `API_ACCESS_TOKEN` est généré automatiquement.
4. Une fois le déploiement terminé, vérifiez l'URL publique suivie de `/health`, puis ouvrez `/app/`.

Le niveau gratuit Render peut mettre le service en veille et sa base SQLite n'est pas persistante. Pour une bêta avec historique durable, configurez PostgreSQL via `DATABASE_URL` avant d'inviter largement des testeurs.
