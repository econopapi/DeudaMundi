COMPOSE ?= docker compose
DEV_COMPOSE := $(COMPOSE) -f docker-compose.yml
PROD_COMPOSE := $(COMPOSE) --env-file .env.production -f docker-compose.prod.yml

.DEFAULT_GOAL := help
.PHONY: help dev-init dev-up dev-down dev-build dev-logs dev-ps dev-migrate dev-etl dev-seed dev-test-api dev-test-web prod-init prod-build prod-up prod-down prod-restart prod-logs prod-ps prod-migrate prod-etl prod-backup-db

help: ## Muestra los comandos disponibles.
	@awk 'BEGIN {FS = ":.*##"}; /^[a-zA-Z0-9_-]+:.*##/ {printf "%-18s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

dev-init: ## Crea api/.env local si aún no existe.
	@test -f api/.env || cp api/.env.example api/.env
	@echo "Configuración local lista en api/.env"

dev-build: dev-init ## Construye las imágenes de desarrollo.
	$(DEV_COMPOSE) build

dev-up: dev-init ## Levanta el stack de desarrollo (Vite con HMR).
	$(DEV_COMPOSE) up -d --build

dev-down: ## Detiene el stack de desarrollo sin borrar datos.
	$(DEV_COMPOSE) down

dev-logs: ## Sigue los logs del stack de desarrollo.
	$(DEV_COMPOSE) logs -f --tail=100

dev-ps: ## Muestra el estado del stack de desarrollo.
	$(DEV_COMPOSE) ps

dev-migrate: ## Ejecuta migraciones en desarrollo.
	$(DEV_COMPOSE) exec api alembic upgrade head

dev-etl: ## Ejecuta el ETL global en desarrollo.
	$(DEV_COMPOSE) exec api deudamundi-etl-global

dev-seed: ## Carga/actualiza los gobiernos en desarrollo.
	$(DEV_COMPOSE) exec api deudamundi-seed-governments

dev-test-api: ## Ejecuta tests y lint del backend dentro de Docker.
	$(DEV_COMPOSE) exec api sh -c "ruff check app tests && pytest"

dev-test-web: ## Ejecuta tests del frontend dentro de Docker.
	$(DEV_COMPOSE) exec web npm test -- --runInBand

prod-init: ## Crea .env.production sin sobrescribir una configuración existente.
	@test -f .env.production || cp .env.production.example .env.production
	@echo "Revisa DOMAIN, CORS_ALLOWED_ORIGINS y los secretos en .env.production antes de desplegar."

prod-build: ensure-prod-env ## Construye las imágenes de producción.
	$(PROD_COMPOSE) build

prod-up: ensure-prod-env ## Despliega o actualiza el stack completo del VPS.
	$(PROD_COMPOSE) up -d --build --remove-orphans

prod-down: ensure-prod-env ## Detiene el stack productivo sin borrar datos.
	$(PROD_COMPOSE) down

prod-restart: ensure-prod-env ## Reinicia los servicios de producción.
	$(PROD_COMPOSE) restart

prod-logs: ensure-prod-env ## Sigue los logs del stack productivo.
	$(PROD_COMPOSE) logs -f --tail=100

prod-ps: ensure-prod-env ## Muestra el estado de producción.
	$(PROD_COMPOSE) ps

prod-migrate: ensure-prod-env ## Ejecuta las migraciones de producción manualmente.
	$(PROD_COMPOSE) exec api alembic upgrade head

prod-etl: ensure-prod-env ## Ejecuta el ETL global en producción.
	$(PROD_COMPOSE) exec api deudamundi-etl-global

prod-backup-db: ensure-prod-env ## Escribe un backup SQL comprimido en backups/ (crea la carpeta si hace falta).
	@mkdir -p backups
	$(PROD_COMPOSE) exec -T postgres sh -c 'pg_dump -U "$$POSTGRES_USER" "$$POSTGRES_DB"' | gzip > backups/deudamundi-$$(date +%Y%m%d-%H%M%S).sql.gz

ensure-prod-env:
	@test -f .env.production || (echo "Falta .env.production. Ejecuta 'make prod-init' y completa sus valores."; exit 1)
