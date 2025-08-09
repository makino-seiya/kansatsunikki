.PHONY: up down build logs clean restart serena-init serena-env serena-up serena-build serena-down

# Start all services
up:
	# If Serena local config exists, generate env and use it
	@test -f .serena/config.yml && python3 scripts/serena_config_to_env.py || true
	@ENV_FILE_ARG=$$( [ -f .serena.env ] && echo '--env-file .serena.env' || echo '' ); \
		docker-compose $$ENV_FILE_ARG up -d

# Stop all services
down:
	@ENV_FILE_ARG=$$( [ -f .serena.env ] && echo '--env-file .serena.env' || echo '' ); \
		docker-compose $$ENV_FILE_ARG down

# Build and start all services
build:
	# If Serena local config exists, generate env and use it
	@test -f .serena/config.yml && python3 scripts/serena_config_to_env.py || true
	@ENV_FILE_ARG=$$( [ -f .serena.env ] && echo '--env-file .serena.env' || echo '' ); \
		docker-compose $$ENV_FILE_ARG up --build -d

# View logs
logs:
	@ENV_FILE_ARG=$$( [ -f .serena.env ] && echo '--env-file .serena.env' || echo '' ); \
		docker-compose $$ENV_FILE_ARG logs -f

# Clean up everything (including volumes)
clean:
	docker-compose down -v
	docker system prune -f

# Restart all services
restart:
	@ENV_FILE_ARG=$$( [ -f .serena.env ] && echo '--env-file .serena.env' || echo '' ); \
		docker-compose $$ENV_FILE_ARG restart

# Serena profile helpers
serena-init:
	mkdir -p .serena
	test -f .serena/config.yml || echo "Created .serena/config.yml with defaults" && touch .serena/config.yml

serena-env:
	python3 scripts/serena_config_to_env.py

serena-up: serena-env
	docker-compose --env-file .serena.env up -d

serena-build: serena-env
	docker-compose --env-file .serena.env up --build -d

serena-down:
	docker-compose --env-file .serena.env down

# Development specific commands
dev-frontend:
	@ENV_FILE_ARG=$$( [ -f .serena.env ] && echo '--env-file .serena.env' || echo '' ); \
		docker-compose $$ENV_FILE_ARG up frontend

dev-frontend-logs:
	@ENV_FILE_ARG=$$( [ -f .serena.env ] && echo '--env-file .serena.env' || echo '' ); \
		docker-compose $$ENV_FILE_ARG logs -f frontend

dev-frontend-restart:
	@ENV_FILE_ARG=$$( [ -f .serena.env ] && echo '--env-file .serena.env' || echo '' ); \
		docker-compose $$ENV_FILE_ARG restart frontend

# View specific service logs
logs-backend:
	@ENV_FILE_ARG=$$( [ -f .serena.env ] && echo '--env-file .serena.env' || echo '' ); \
		docker-compose $$ENV_FILE_ARG logs -f backend

logs-frontend:
	@ENV_FILE_ARG=$$( [ -f .serena.env ] && echo '--env-file .serena.env' || echo '' ); \
		docker-compose $$ENV_FILE_ARG logs -f frontend

logs-db:
	@ENV_FILE_ARG=$$( [ -f .serena.env ] && echo '--env-file .serena.env' || echo '' ); \
		docker-compose $$ENV_FILE_ARG logs -f database

logs-minio:
	@ENV_FILE_ARG=$$( [ -f .serena.env ] && echo '--env-file .serena.env' || echo '' ); \
		docker-compose $$ENV_FILE_ARG logs -f minio

# Execute commands in containers
backend-shell:
	@ENV_FILE_ARG=$$( [ -f .serena.env ] && echo '--env-file .serena.env' || echo '' ); \
		docker-compose $$ENV_FILE_ARG exec backend bash

frontend-shell:
	@ENV_FILE_ARG=$$( [ -f .serena.env ] && echo '--env-file .serena.env' || echo '' ); \
		docker-compose $$ENV_FILE_ARG exec frontend sh

db-shell:
	@ENV_FILE_ARG=$$( [ -f .serena.env ] && echo '--env-file .serena.env' || echo '' ); \
		docker-compose $$ENV_FILE_ARG exec database mysql -u app_user -p plant_tracker