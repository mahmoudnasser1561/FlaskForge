# FlaskForge Microblog
FlaskForge Microblog is a full-stack MicroBlog application built with Flask, offering a complete set of features for user interaction and content sharing. 
This project demonstrates modern Flask practices — including authentication, user roles, admin control, databases, pagination.

## Features
1. User registration & authentication (login/logout)
2. User profiles and avatar images via Gravatar
4. Create, edit, and delete blog posts
5. Pagination for posts
6. Admin control
7. Email notifications & password reset
8. Database migrations with Flask-Migrate
9. Unit tests for core functionality

<img width="841" height="210" alt="Untitled Diagram-Page-3 drawio(5)" src="https://github.com/user-attachments/assets/5a66e4e9-7648-4a09-80a3-5152b5107d75" />

<img width="201" height="370" alt="Untitled Diagram-Page-3 drawio(6)" src="https://github.com/user-attachments/assets/0e592505-1797-4679-9096-460115c81315" />

## Getting Started

1. Create a virtual environment and install dependencies:
   ```
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements/dev.txt
   ```
2. Set the required environment variables (e.g. in a `.env` file):
   ```
   FLASK_APP=app.py
   SECRET_KEY=<your-secret-key>
   FLASKY_ADMIN=<your-admin-email>
   ```
3. Run the deployment task to create the database schema and seed the
   default user roles — this step is required before the app can be used,
   otherwise newly registered users won't have a role or any permissions:
   ```
   flask deploy
   ```
4. Start the app:
   ```
   flask run
   ```

## Run with Docker

1. Copy `.env.example` to `.env` and fill in your own values (at minimum
   `SECRET_KEY`; fill in the `MAIL_*` fields too if you want confirmation
   emails to actually send — see the comments in `.env.example` for how to
   get a Gmail App Password). `.env` is git-ignored, so your real values
   never get committed.
2. Run:
   ```
   docker compose up --build
   ```
   Then open http://localhost:5000 in your browser. The `web` container
   runs `flask deploy` (migrations + role seeding) automatically before
   starting, so it's ready to use as soon as the containers are up.

Data persists in a named volume across restarts; use
`docker compose down -v` to also remove the database volume.

