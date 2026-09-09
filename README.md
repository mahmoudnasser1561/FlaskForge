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

### Seed demo data (optional)

The app starts empty — no fake users, posts, or comments are created
automatically. To populate it with demo content so the site looks live
when you browse it, run this once after the stack is up:
```
docker compose exec web flask seed
```
This creates 50 fake users, 100 posts, follow relationships between
users, and 200 comments. To customize the amounts:
```
docker compose exec web flask seed --users 20 --posts 50 --comments 80
```
Re-running `flask seed` is safe for users and follows (duplicates are
skipped), but will add *more* posts and comments each time rather than
replacing them.

## Security

Login (`/auth/login`) and registration (`/auth/register`) are rate
limited per IP address (10 login attempts/minute, 5 registrations/hour;
only `POST` submissions count, so browsing the pages freely never trips
it) to slow down password-guessing and mass account creation. The limiter
is backed by Redis (the `redis` service in `docker-compose.yml`) so the
limit is enforced correctly across gunicorn's multiple worker processes —
without a shared backend, each worker would track its own count and the
real limit would silently be higher than configured. Set `REDIS_URL` to
point elsewhere in production; running `flask run` locally without Redis
falls back to in-memory storage automatically (fine for a single dev
process).
