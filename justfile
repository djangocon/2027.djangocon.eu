# Task runner for local development (https://just.systems).
# Everything runs inside the compose services, so only Docker is needed on the host.
#
# Just does not yet manage signals for subprocesses reliably, which can lead to
# unexpected behavior; keep its use to local development.
# See https://github.com/casey/just/issues/2473 .

export COMPOSE_FILE := "compose.yml"

# List all available commands.
default:
    @just --list

# Create .envs/.django if missing, then build the images.
build *args:
    @python setup_env.py
    @echo "Building images..."
    @docker compose build {{ args }}

# Start the django (8000) and node/browser-sync (3000) containers.
up:
    @echo "Starting up containers..."
    @docker compose up -d --remove-orphans

# Stop containers.
down:
    @echo "Stopping containers..."
    @docker compose down

# Remove containers and their volumes.
prune *args:
    @echo "Killing containers and removing volumes..."
    @docker compose down -v {{ args }}

# Follow container logs (optionally for one service: `just logs django`).
logs *args:
    @docker compose logs -f {{ args }}

# Run a manage.py command: `just manage check`.
manage +args:
    @docker compose run --rm django python ./manage.py {{ args }}

# Open a shell in the django container.
shell:
    @docker compose run --rm django bash

# Run the test suite.
pytest *args:
    @docker compose run --rm django pytest {{ args }}

# Run every pre-commit hook (ruff, djlint, prettier, ...) against all files.
lint:
    @docker compose run --rm --no-deps django pre-commit run --all-files

# Compile SCSS/JS once (the node container does this continuously while `up`).
assets:
    @docker compose run --rm --no-deps node npm run build

# Collect static files the way production does (writes to ./staticfiles).
collectstatic:
    @docker compose run --rm -e DJANGO_SETTINGS_MODULE=config.settings.production -e DJANGO_SECRET_KEY=collectstatic -e DJANGO_ALLOWED_HOSTS=localhost django python ./manage.py collectstatic --no-input
