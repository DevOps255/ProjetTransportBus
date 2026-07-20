# ProjetTransportBus — Gestion du transport en bus (Université de Kara)

Description
-----------
Application web en phase initiale pour gérer le transport en bus des étudiants de l'Université de Kara. Le projet contient déjà :
- Les entités (modèles) du domaine : utilisateurs, bus, trajets, tickets, etc.
- La logique métier empêchant les transitions de tickets illégales (workflow/validations).

Statut
------
Phase initiale — développement actif. Priorités à court terme : exposer les endpoints API, ajouter l'authentification, tests et interface utilisateur.

Technologies principales
-----------------------
- Python 3.10+
- Uvicorn (ASGI server)
- ORM (ex. SQLAlchemy) + Alembic pour les migrations
- Mako pour templates (présent)
- Dockerfile pour conteneurisation

Prérequis
---------
- Git
- Python 3.10 ou supérieur
- Une base de données (Postgres recommandé)
- Docker (optionnel)

Installation et démarrage — Développement (Linux / macOS)
---------------------------------------------------------
1. Cloner le dépôt
   git clone https://github.com/DevOps255/ProjetTransportBus-pas-encore-de-nom-.git
   cd ProjetTransportBus-pas-encore-de-nom-

2. Créer et activer l'environnement virtuel
   python -m venv .venv
   source .venv/bin/activate

3. Mettre pip à jour puis installer les dépendances
   python -m pip install --upgrade pip
   pip install -r requirements.txt

4. Copier et adapter le fichier d'environnement
   cp .env.example .env
   # Modifier .env avec :
   # DATABASE_URL=postgresql://user:password@localhost:5432/projet_transport
   # SECRET_KEY=change_this_secret
   # AUTRES_VARS=...

5. Appliquer les migrations (Alembic)
   # Si alembic est installé et configuré :
   alembic upgrade head

6. Lancer l'application en mode développement
   # Remplacer `app.main:app` par le module ASGI réel si nécessaire
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

7. Accéder à l'API
   - API : http://127.0.0.1:8000
   - Docs interactives (Swagger) : http://127.0.0.1:8000/docs
   - ReDoc : http://127.0.0.1:8000/redoc

Installation et démarrage — Windows (PowerShell)
------------------------------------------------
1. git clone https://github.com/DevOps255/ProjetTransportBus-pas-encore-de-nom-.git
   cd ProjetTransportBus-pas-encore-de-nom-

2. python -m venv .venv
   .\.venv\Scripts\Activate.ps1

3. python -m pip install --upgrade pip
   pip install -r requirements.txt

4. Copier et éditer .env
   copy .env.example .env
   # Éditer .env comme indiqué ci-dessus

5. alembic upgrade head

6. uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

Commandes utiles
----------------
- Linter (ex. flake8 / ruff) :
  python -m ruff check .
  python -m flake8

- Tests (pytest) :
  pytest -q

- Migration (générer) :
  alembic revision --autogenerate -m "message"
  alembic upgrade head

- Exécuter avec des variables d'environnement sans .env (ex. Linux) :
  export DATABASE_URL="postgresql://user:pass@localhost:5432/projet_transport"
  export SECRET_KEY="ma_cle_secrete"
  uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

Démarrage avec Docker
---------------------
1. Construire l'image
   docker build -t projet-transport-bus .

2. Lancer en mode simple (passer la DATABASE_URL)
   docker run --rm -e DATABASE_URL="postgresql://user:pass@host:5432/projet_transport" \
     -e SECRET_KEY="ma_cle_secrete" -p 8000:8000 projet-transport-bus

3. Lancer en utilisant un fichier .env
   docker run --rm --env-file .env -p 8000:8000 projet-transport-bus

4. Exemple docker-compose minimal (à ajouter si utile)
   version: "3.8"
   services:
     web:
       build: .
       ports:
         - "8000:8000"
       env_file:
         - .env
       depends_on:
         - db
     db:
       image: postgres:15
       environment:
         POSTGRES_USER: user
         POSTGRES_PASSWORD: pass
         POSTGRES_DB: projet_transport
       volumes:
         - pgdata:/var/lib/postgresql/data
   volumes:
     pgdata:

Sécurité et configuration
-------------------------
- Ne jamais committer les secrets (.env) dans le dépôt.
- Utiliser des variables d'environnement pour DATABASE_URL et SECRET_KEY.
- Pour la production, configurer un process manager (uvicorn + gunicorn / systemd) et HTTPS (reverse proxy Nginx).

Bonnes pratiques recommandées
------------------------------
- Ajouter des tests unitaires et d'intégration surtout pour la logique de transitions de tickets.
- Documenter les endpoints (OpenAPI) et les modèles de données.
- Mettre en place CI (lint, tests) avant merge des PRs.
- Rédiger une roadmap / issues pour prioriser UI, authentification et gestion des trajets.

Contribution
------------
- Ouvrir une issue pour tout bug ou proposition.
- Faire des PRs petites et ciblées avec description et tests.
- Respecter le style de code et ajouter des tests pour toute nouvelle logique métier.

Structure du dépôt (emplacement des dossiers et fichiers importants)
------------------------------------------------------------------
Voici une arborescence recommandée et les emplacements habituels des fichiers et dossiers dans ce type de projet :

- README.md                        # à la racine (ce fichier)
- LICENSE                          # à la racine (fichier de licence)
- .env.example                     # à la racine (exemple de variables d'environnement)
- requirements.txt                 # à la racine (dépendances Python)
- Dockerfile                       # à la racine (image de conteneur)
- docker-compose.yml               # à la racine (si présent)
- app/                             # code source principal (ASGI app)
  - main.py                        # point d'entrée ASGI (`app.main:app`) ou autre
  - api/                           # routes / endpoints
  - core/                          # configuration, settings
  - models/                        # modèles / entités
  - db/                            # initialisation DB, session, migrations
  - services/                      # logique métier
  - templates/                     # templates Mako (si utilisés)
- alembic/                         # configuration et versions de migration (si Alembic)
- tests/                           # suites de tests
- scripts/                         # scripts utilitaires (initialisation, fixtures)

Remarques :
- Le fichier LICENSE doit être placé à la racine du dépôt pour être détecté automatiquement par GitHub et les outils.
- Les secrets et fichiers locaux (.env, .venv/) ne doivent pas être committés.

Licence
-------
À définir — ajouter un fichier LICENSE (ex. MIT) à la racine si vous souhaitez ouvrir le projet.

Contact
-------
Mainteneur : DevOps255
