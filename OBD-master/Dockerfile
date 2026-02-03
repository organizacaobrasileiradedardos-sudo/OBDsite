FROM python:3.9-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# dependências do sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# copia o projeto
COPY . .


# instala dependências Python
RUN pip install --no-cache-dir -r requirements.txt

# entra no diretório do django
# WORKDIR /app/OBD-master

# instala deps
RUN pwd && ls -la

# start da aplicação
CMD sh -c "python manage.py migrate && gunicorn obd.wsgi:application --bind 0.0.0.0:$PORT --workers 2 --threads 4"
