# Переменные
DC = docker-compose
APP_NAME = schedule_bot

.PHONY: help build up down logs restart status clean shell

help: ## Показать справку по командам
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'

build: ## Собрать или пересобрать образ бота
	$(DC) build

up: ## Запустить бота в фоновом режиме
	$(DC) up -d

down: ## Остановить и удалить контейнеры
	$(DC) down

logs: ## Посмотреть логи бота (в реальном времени)
	$(DC) logs -f bot

restart: ## Перезапустить бота
	$(DC) restart bot

status: ## Показать статус контейнеров
	$(DC) ps

clean: ## Удалить неиспользуемые образы и контейнеры
	docker system prune -f

shell: ## Войти в терминал внутри контейнера
	$(DC) exec bot /bin/bash
