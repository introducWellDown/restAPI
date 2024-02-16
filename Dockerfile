# Используем официальный образ Python 3.11.8
FROM python:3.11.8

# Создаём рабочую директорию внутри контейнера с нужным названием
WORKDIR /e-commet-server

# Копируем все файлы и папки из локального контекста сборки в рабочую директорию образа
COPY app/ ./app
COPY templates/ ./templates
COPY .env .
COPY requirements.txt .

# Устанавливаем зависимости
RUN pip install -r requirements.txt

EXPOSE 8000
# Переходим в папку с приложением
WORKDIR /e-commet-server/app

# Определяем команду для запуска приложения
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
