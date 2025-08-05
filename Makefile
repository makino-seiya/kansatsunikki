.PHONY: up down build logs clean restart

# Start all services
up:
	docker-compose up -d

# Stop all services
down:
	docker-compose down

# Build and start all services
build:
	docker-compose up --build -d

# View logs
logs:
	docker-compose logs -f

# Clean up everything (including volumes)
clean:
	docker-compose down -v
	docker system prune -f

# Restart all services
restart:
	docker-compose restart

# Development specific commands
dev-frontend:
	docker-compose up frontend

dev-frontend-logs:
	docker-compose logs -f frontend

dev-frontend-restart:
	docker-compose restart frontend

# View specific service logs
logs-backend:
	docker-compose logs -f backend

logs-frontend:
	docker-compose logs -f frontend

logs-db:
	docker-compose logs -f database

logs-minio:
	docker-compose logs -f minio

# Execute commands in containers
backend-shell:
	docker-compose exec backend bash

frontend-shell:
	docker-compose exec frontend sh

db-shell:
	docker-compose exec database mysql -u app_user -p plant_tracker