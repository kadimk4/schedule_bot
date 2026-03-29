FROM python:3.12-slim

# Установка uv для быстрой работы с зависимостями
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Установка рабочей директории
WORKDIR /app

# Копируем файлы зависимостей
COPY pyproject.toml uv.lock ./

# Устанавливаем зависимости (без создания venv внутри контейнера для простоты)
RUN uv pip install --system --no-cache -r pyproject.toml

# Копируем весь код проекта
COPY . .

# Создаем папку для данных, если её нет (для volumes)
RUN mkdir -p /app/data

# Запуск бота
CMD ["python", "bot.py"]
