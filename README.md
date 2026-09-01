# Nomade bêta

API FastAPI pour le calcul d’itinéraire voiture ou bus, avec moteur de routage de secours, gestion des coûts, historique local et arrêts bus sauvegardés.

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

- les deux modes disponibles sont `voiture` et `bus`
- le mode bus utilise actuellement le profil routier voiture ; les voies réservées et les contraintes spécifiques aux bus ne sont pas garanties

### Avec clé ORS réelle

Le géocodeur est réactivé et permet de convertir automatiquement une adresse en coordonnées.

## Endpoints principaux

- `GET /itineraire/calcul`
- `GET /itineraire/geocoder`
- `GET /itineraire/compteur`
- `GET /itineraire/`
- `PUT /itineraire/{itineraire_id}/tournee`
- `POST /itineraire/{itineraire_id}/arrets`
- `GET /pays/`
- `GET /stations/`
- `GET /alertes/`

## Points de vigilance

- La clé ORS doit être une vraie clé valide ; les valeurs type `VOTRE_...`, `CHANGE_ME` ou `REMPLACEZ_PAR_VOTRE_CLE_ORS` sont rejetées.
- Le token API doit être renseigné pour les appels protégés.
- L’interface locale peut lancer des appels sans token ; une instance publique reste protégée.
- Le fallback OSRM est la source de secours pour la route en mode sans clé ORS.
- Les vingt tournées les plus récentes sont conservées. Une tournée peut être nommée par le conducteur et contenir jusqu’à vingt arrêts bus ; chaque arrêt conserve sa position GPS, sa précision et le sens de l’itinéraire.

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
3. Le blueprint crée un disque persistant de 1 Go monté dans `/data` et configure `DATABASE_URL` pour conserver les tournées. Ce disque requiert l’offre Render Starter.
4. Saisissez les valeurs secrètes `ORS_API_KEY` et `GRAPHOPPER_API_KEY` dans Render. `API_ACCESS_TOKEN` est généré automatiquement.
5. Une fois le déploiement terminé, vérifiez l'URL HTTPS publique suivie de `/health`, puis ouvrez `/app/` sur le téléphone et autorisez la géolocalisation.

Le niveau gratuit Render peut mettre le service en veille et sa base SQLite n'est pas persistante. Pour une bêta multi-utilisateur ou à fort volume, remplacez SQLite par PostgreSQL via `DATABASE_URL` avant d'inviter largement des testeurs.
