# ⚽ Ligue 1 Analytics - Plateforme de Scraping et Visualisation

## 📋 Description du Projet

Plateforme complète d'analyse et de visualisation des données du championnat de France de football (Ligue 1). Le projet combine un système de scraping automatisé avec un dashboard interactif pour suivre en temps réel le classement et les statistiques des équipes.

### Fonctionnalités principales

- 🕷️ **Scraping automatisé** : Collecte périodique des données depuis Wikipedia
- 📊 **Dashboard interactif** : Visualisation en temps réel via Dash/Plotly
- 💾 **Stockage MongoDB** : Base de données NoSQL pour la persistance
- 🐳 **Architecture containerisée** : Déploiement facile avec Docker Compose
- 🔄 **Mise à jour automatique** : Scheduler configurable pour les scraping périodiques
- 📈 **Analytics avancés** : Graphiques, tableaux et statistiques détaillées

---

## 🏗️ Architecture Technique

### Stack Technologique

| Composant | Technologie | Version | Rôle |
|-----------|------------|---------|------|
| **Web Scraping** | Scrapy | 2.11.0 | Framework de scraping |
| **Scheduler** | Schedule | 1.2.0 | Planification des tâches |
| **Base de données** | MongoDB | 7.0 | Stockage NoSQL |
| **Backend** | Python | 3.x | Logique métier |
| **Frontend** | Dash | 2.14.2 | Framework web interactif |
| **Visualisation** | Plotly | 5.18.0 | Graphiques interactifs |
| **Containerisation** | Docker | - | Orchestration des services |
| **ODM** | PyMongo | 4.6.1 | Driver MongoDB |

### Architecture des Services

```
┌─────────────────────────────────────────────────────────┐
│                   Docker Compose                         │
├─────────────────┬─────────────────┬─────────────────────┤
│   Spider        │    MongoDB      │    Dashboard        │
│   Container     │    Container    │    Container        │
├─────────────────┼─────────────────┼─────────────────────┤
│ - Scrapy        │ - Mongo 7.0     │ - Dash/Plotly       │
│ - Scheduler     │ - Port: 27017   │ - Port: 8050        │
│ - Python        │ - Volumes       │ - MongoDB Client    │
└─────────────────┴─────────────────┴─────────────────────┘
        │                  │                  │
        └──────────────────┼──────────────────┘
                           │
                   ligue1-network
```

### Structure du Projet

```
DataEngineering/
├── docker-compose.yml          # Orchestration des services
├── health_check.py             # Script de vérification des services
│
├── scraper/                    # Service de scraping
│   ├── Dockerfile              # Image Docker du spider
│   ├── requirements.txt        # Dépendances Python
│   ├── scheduler.py            # Scheduler de scraping
│   ├── scrapy.cfg              # Configuration Scrapy
│   └── ligue1_scraper/         # Projet Scrapy
│       ├── __init__.py
│       ├── items.py            # Définition des items
│       ├── pipelines.py        # Pipeline MongoDB
│       ├── settings.py         # Configuration Scrapy
│       └── spiders/
            └── __init__.py
│           └── ligue1_spider.py  # Spider principal
│
└── webapp/                     # Service dashboard
    ├── Dockerfile              # Image Docker du dashboard
    ├── requirements.txt        # Dépendances Python
    ├── app.py                  # Application Dash
    └── mongo_client.py         # Client MongoDB
```

---

## 🚀 Installation et Lancement

### Prérequis

- **Docker** >= 20.10
- **Docker Compose** >= 2.0
- **Git** (pour cloner le projet)
- **Ports disponibles** : 27017 (MongoDB), 8050 (Dashboard)

### 1. Cloner le Projet

```bash
git clone https://github.com/Sachachen/DataEngineering.git
cd DataEngineering
```

### 2. Configuration de l'Environnement

```bash
# Créer un environnement virtuel Python
python -m venv venv

# Activer l'environnement (Windows)
venv\Scripts\activate

# Activer l'environnement (Linux/Mac)
source venv/bin/activate

### 3. Lancer l'Application

```bash
# Démarrage de tous les services
docker-compose up -d
```

#### Méthode détaillée

```bash
# Construction des images Docker
docker-compose build

# Lancement des services en arrière-plan
docker-compose up -d

# Consultation des logs en temps réel
docker-compose logs -f
```

### 4. Vérification du Déploiement

```bash
# Vérifier l'état des conteneurs
docker-compose ps

# Vérifier les logs de chaque service
docker-compose logs mongodb
docker-compose logs spider
docker-compose logs webapp

# Lancer le health check
python health_check.py
```

### 5. Accès au Dashboard

Le dashboard est accessible via navigateur à l'adresse : **http://localhost:8050**

---


### Variables d'Environnement

#### MongoDB
- `MONGO_INITDB_ROOT_USERNAME` : admin
- `MONGO_INITDB_ROOT_PASSWORD` : password123
- `MONGO_INITDB_DATABASE` : ligue1_db

#### Spider
- `MONGO_URI` : URI de connexion MongoDB
- `LOG_LEVEL` : Niveau de logs (INFO, DEBUG, WARNING)

#### Webapp
- `MONGO_URI` : URI de connexion MongoDB

### Configuration du Scheduler

Le spider peut être configuré avec différents paramètres :

```bash
# Lancer immédiatement puis toutes les heures
docker-compose up -d  # Par défaut : --immediate --interval 1

# Modifier l'intervalle de scraping
# Editer docker-compose.yml ligne :
command: python scheduler.py --immediate --interval 2  # Toutes les 2 heures
```

Options du scheduler :
- `--immediate` : Lance un scraping au démarrage
- `--interval N` : Interval en heures entre chaque scraping (défaut: 1)

---

## 📊 Fonctionnement Détaillé

### 1. Service de Scraping (Spider)

#### Source de Données
- URL : `https://fr.wikipedia.org/wiki/Championnat_de_France_de_football_2025-2026`
- Parser : HTML via Scrapy CSS Selectors

#### Données Collectées

**Pour chaque équipe :**
- Position au classement
- Nom de l'équipe
- Nombre de matchs joués
- Victoires / Nuls / Défaites
- Buts pour / Buts contre
- Différence de buts
- Points
- Date de scraping

**Statistiques globales :**
- Saison en cours
- Journée actuelle
- Nombre total d'équipes
- Date de collecte

#### Pipeline de Traitement

1. **Scraping** : Le spider parcourt la page Wikipedia
2. **Parsing** : Extraction des données du tableau de classement
3. **Validation** : Vérification de la cohérence des données
4. **Stockage** : Insertion dans MongoDB via le pipeline
5. **Mise à jour** : Upsert basé sur la saison et l'équipe

#### Scheduler

Le fichier `scheduler.py` utilise la bibliothèque `schedule` pour :
- Lancer le spider immédiatement au démarrage (si `--immediate`)
- Planifier des exécutions périodiques (toutes les N heures)
- Logger toutes les opérations
- Gérer les erreurs et timeouts (max 5 minutes par scraping)

### 2. Base de Données MongoDB

#### Collections

**`ligue1_teams`** : Données des équipes
```javascript
{
  "saison": "2025-2026",
  "equipe": "Paris Saint-Germain",
  "position": 1,
  "matchs_joues": 20,
  "victoires": 15,
  "nuls": 3,
  "defaites": 2,
  "buts_pour": 45,
  "buts_contre": 18,
  "difference_buts": 27,
  "points": 48,
  "scraped_date": ISODate("2026-02-13T10:30:00Z")
}
```

**`ligue1_stats`** : Statistiques globales
```javascript
{
  "saison": "2025-2026",
  "journee": 20,
  "total_equipes": 18,
  "total_matchs": 180,
  "scraped_date": ISODate("2026-02-13T10:30:00Z")
}
```

#### Indexation
- Index unique sur `{saison, equipe}` pour éviter les doublons
- Index sur `scraped_date` pour les requêtes temporelles

### 3. Dashboard Web (Webapp)

#### Technologies
- **Framework** : Dash (Python web framework)
- **Graphiques** : Plotly Express et Graph Objects
- **Styling** : CSS custom avec thème sombre

#### Composants Visuels

1. **Header** : Titre et informations de saison
2. **Métriques clés** : 
   - Nombre d'équipes
   - Total de matchs
   - Dernière mise à jour
3. **Graphiques** :
   - Classement général (bar chart)
   - Distribution des points (histogram)
   - Buts pour vs Buts contre (scatter plot)
   - Évolution des performances (line chart)
4. **Tableau détaillé** : Liste complète avec toutes les statistiques
5. **Auto-refresh** : Mise à jour toutes les 5 minutes

#### Palettes de Couleurs
```python
COLORS = {
    'background': '#0e1117',   # Fond sombre
    'card': '#1e2130',         # Cartes
    'text': '#ffffff',         # Texte blanc
    'primary': '#00d4ff',      # Bleu primaire
    'secondary': '#ff4b4b',    # Rouge secondaire
    'success': '#00ff88',      # Vert succès
    'warning': '#ffaa00',      # Orange warning
}
```

---

## 🛠️ Commandes Utiles

### Gestion des Conteneurs

```bash
# Démarrer tous les services
docker-compose up -d

# Arrêter tous les services
docker-compose down

# Redémarrer un service spécifique
docker-compose restart spider
docker-compose restart webapp
docker-compose restart mongodb

# Voir les logs en temps réel
docker-compose logs -f spider
docker-compose logs -f webapp --tail 50

# Reconstruire les images
docker-compose build
docker-compose build --no-cache  # Sans cache
```

### Accès aux Conteneurs

```bash
# Shell dans le conteneur spider
docker-compose exec spider /bin/bash

# Shell dans le conteneur webapp
docker-compose exec webapp /bin/bash

# Accès MongoDB
docker-compose exec mongodb mongosh -u admin -p password123
```

### MongoDB - Requêtes Manuelles

```bash
# Connexion à MongoDB
docker-compose exec mongodb mongosh -u admin -p password123 --authenticationDatabase admin

# Dans le shell MongoDB :
use ligue1_db

# Compter les équipes
db.ligue1_teams.countDocuments()

# Voir le classement
db.ligue1_teams.find().sort({position: 1}).limit(5)

# Voir les dernières données
db.ligue1_teams.find().sort({scraped_date: -1}).limit(1)

# Supprimer toutes les données
db.ligue1_teams.deleteMany({})
db.ligue1_stats.deleteMany({})
```

### Débogage

```bash
# Vérifier la santé des services
python health_check.py

# Lancer manuellement le spider (dans le conteneur)
docker-compose exec spider scrapy crawl ligue1

# Tester la connexion MongoDB
docker-compose exec spider python -c "from pymongo import MongoClient; print(MongoClient('mongodb://admin:password123@mongodb:27017/').server_info())"
```

---

## 🎯 Choix Technologiques

### 1. Scrapy pour le Web Scraping

**Avantages :**
- Parsing HTML optimisé avec sélecteurs CSS
- Système de pipeline extensible et modulaire
- Gestion automatique des erreurs et retry mechanism
- Performance élevée grâce à l'architecture asynchrone
- Middleware personnalisable pour étendre les fonctionnalités

**Alternative considérée :** BeautifulSoup + Requests, solution moins performante et sans système de pipeline intégré

### 2. MongoDB comme Base de Données

**Avantages :**
- Schéma flexible adapté aux données de scraping évolutives
- Performance optimale pour les opérations d'agrégation
- Opération upsert native pour éviter les doublons
- Solution idéale pour le stockage de données semi-structurées

**Alternative considérée :** PostgreSQL, nécessitant un schéma rigide moins adapté aux données de scraping

### 3. Dash/Plotly pour le Dashboard

**Avantages de Dash :**
- Framework entièrement en Python, éliminant la nécessité de développer en JavaScript
- Bibliothèque de graphiques interactifs haute performance
- Système de callbacks réactifs intuitif et efficace
- Développement rapide grâce à une API de haut niveau
- Interface responsive et moderne par défaut

**Alternative considérée :** Flask + Chart.js, nécessitant cependant plus de développement frontend et une architecture plus complexe

### 4. Docker Compose pour l'Orchestration

**Avantages de Docker Compose :**
- Garantie de reproductibilité de l'environnement sur toutes les plateformes
- Isolation des services pour éviter les conflits de dépendances
- Automatisation complète de l'installation des dépendances
- Réseau interne permettant la communication inter-conteneurs
- Persistance des données via volumes Docker
- Surveillance de l'état des services avec health checks intégrés

**Alternative :** Installation manuelle nécessitant une configuration complexe et une gestion individuelle de chaque dépendance

### 5. Schedule pour la Planification

**Avantages de Schedule :**
- Bibliothèque légère avec faible empreinte mémoire
- API simple et intuitive
- Indépendant des utilitaires système (cron, systemd)
- Compatibilité multiplateforme (Windows, Linux, macOS)
- Solution adaptée aux besoins de planification périodique du projet

**Alternative considérée :** Celery + Redis, solution plus complexe offrant des fonctionnalités avancées non nécessaires pour ce cas d'usage

---

## 🔍 Guide de Dépannage

### Problème de démarrage des conteneurs

```bash
# Vérifier les ports occupés
netstat -ano | findstr :27017  # MongoDB
netstat -ano | findstr :8050   # Dashboard

# Vérifier les logs
docker-compose logs

# Nettoyer et redémarrer
docker-compose down -v
docker-compose up -d --force-recreate
```

### Erreur du service de scraping

```bash
# Vérifier les logs du spider
docker-compose logs spider --tail 100

# Lancer manuellement
docker-compose exec spider scrapy crawl ligue1

# Vérifier la connexion MongoDB depuis le spider
docker-compose exec spider python -c "
from pymongo import MongoClient
client = MongoClient('mongodb://admin:password123@mongodb:27017/')
print(client.server_info())
"
```

### Problème : Le dashboard affiche "No data"

```bash
# Vérifier si des données existent dans MongoDB
docker-compose exec mongodb mongosh -u admin -p password123 --eval "
  use ligue1_db;
  db.ligue1_teams.countDocuments();
"

# Si vide, lancer un scraping manuel
docker-compose exec spider scrapy crawl ligue1
```

### Problème de connexion MongoDB

```bash
# Vérifier le health check
docker-compose ps

# Redémarrer MongoDB
docker-compose restart mongodb

# Vérifier les credentials
docker-compose exec mongodb mongosh -u admin -p password123 --authenticationDatabase admin
```

---

## 📈 Roadmap et Évolutions Futures

### Court terme
- [ ] Implémentation de tests unitaires et d'intégration
- [ ] Système de notifications (Discord/Slack) pour les événements sportifs
- [ ] Graphiques d'évolution temporelle sur la saison
- [ ] API REST avec FastAPI pour l'accès programmatique aux données
- [ ] Intégration du calendrier des matchs

### Moyen terme
- [ ] Diversification des sources de données (L'Équipe, LFP)
- [ ] Extension aux statistiques individuelles des joueurs
- [ ] Implémentation d'un cache Redis pour optimisation des performances
- [ ] Fonctionnalités d'export (PDF, Excel, CSV)
- [ ] Système d'authentification et de gestion des utilisateurs

### Long terme
- [ ] Modèles prédictifs basés sur l'apprentissage automatique
- [ ] Migration vers Kubernetes pour scalabilité
- [ ] Développement d'une application mobile
- [ ] Extension à d'autres championnats européens
- [ ] Plateforme de pronostics collaborative

---

## 📝 Maintenance

### Mise à jour des Dépendances

```bash
# Dans scraper/
pip install --upgrade scrapy pymongo

# Dans webapp/
pip install --upgrade dash plotly pandas

# Mettre à jour les requirements.txt
pip freeze > requirements.txt
```

### Sauvegarde MongoDB

```bash
# Backup
docker-compose exec mongodb mongodump --username admin --password password123 --authenticationDatabase admin --out /data/backup

# Restore
docker-compose exec mongodb mongorestore --username admin --password password123 --authenticationDatabase admin /data/backup
```

---

## 👥 Contribution

Les contributions sont les bienvenues. Pour contribuer au projet :

1. Forkez le repository
2. Créez votre branche de fonctionnalité (`git checkout -b feature/NouvelleFonctionnalite`)
3. Committez vos modifications (`git commit -m 'Ajout d'une nouvelle fonctionnalité'`)
4. Pushez vers la branche (`git push origin feature/NouvelleFonctionnalite`)
5. Ouvrez une Pull Request

Toutes les contributions, qu'elles soient mineures ou majeures, sont appréciées.

---

## 📄 Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

---

## 🙏 Remerciements

- **Wikipedia** pour les données publiques
- **Scrapy Project** pour le framework de scraping
- **Plotly/Dash** pour les outils de visualisation
- **MongoDB** pour la base de données

---

## 📞 Contact

Pour toute question ou suggestion :
- **GitHub** : 
[Antoine Chen](https://github.com/Sachachen) et
[Adam Nouari](https://github.com/adam-nouari)
- **Repository** : [DataEngineering](https://github.com/Sachachen/DataEngineering)

---

**Développé avec passion pour l'analyse sportive et les données du football français**

*Note : Si ce projet vous a été utile, n'hésitez pas à lui attribuer une étoile ⭐ sur GitHub.*

