FROM python:3.9-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# deps do sistema (psycopg2, pillow, etc. costumam precisar)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# copia projeto
COPY . .

# entra no diretório do django
WORKDIR /app/OBD-master

# instala deps
RUN ls -la
RUN pip install --no-cache-dir -r requirements.txt

# opcional: collectstatic (se você estiver com whitenoise ou servir static)
# RUN python manage.py collectstatic --noinput

# start
CMD ["sh", "-c", "gunicorn obd.wsgi:application --bind 0.0.0.0:${PORT} --log-file -"]
