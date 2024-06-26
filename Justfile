# Lists available commands and their descriptions
help:
    just --list

# Starts the Docker containers and builds the project
up:
    docker compose up -d --build

# Stops Docker containers without removing them
stop:
    docker compose stop

# Stops and removes Docker containers
down:
    docker compose down -v

# Rebuilds the base Docker images
rebuild:
    docker compose down --remove-orphans
    docker compose build --no-cache

# View and follow logs for the entire Docker Compose setup or a specific service without prefix
logs service="app":
    sh -c "if [ -z '{{service}}' ]; then docker compose logs --no-log-prefix -f; else docker compose logs --no-log-prefix -f {{service}}; fi"

# Access the shell of the specified container
shell service:
    docker compose exec {{service}} bash

# Define the exec command to execute arbitrary commands in the app container
exec command:
  docker compose -f docker-compose.yml exec app sh -c "{{command}}"

# Define the watch command to watch static files
watch:
  docker compose -f docker-compose.yml exec app bun run watch:css

# Format the codebase using Ruff
format:
  ruff check --exit-zero --fix | ruff format
