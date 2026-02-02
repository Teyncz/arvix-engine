Arvix Finance Engine est une infrastructure backend conçue pour l'acquisition, le traitement et la distribution de données financières (Crypto, Forex, Indices).

🚧 **Status : Work in Progress**

- Ce projet est actuellement en développement.

**Stack Technique**

- Langage : Python 3.14

- Framework API : FastAPI

- Base de données : PostgreSQL

- ORM & Migrations : SQLAlchemy & Alembic

**Structure du Projet**

```
├── api/             # Endpoints FastAPI et logique des routes
├── acquisition/     # Scripts de scraping et Scheduler de tâches
├── database/        # Modèles SQLAlchemy, CRUD et gestion des sessions
├── core/            # Configuration globale et sécurité (Pydantic)
├── alembic/         # Historique des migrations de la base de données
└── utils/           # Fonctions utilitaires (Time, Tickers, etc.)
```
