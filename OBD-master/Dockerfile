FROM python:3.9-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY . .

# instala dependências (arquivo está na raiz)
RUN pip install --no-cache-dir -r requirements.txt

# agora entra no Django
WORKDIR /app/OBD-master

CMD sh -c "python manage.py migrate && gunicorn obd.wsgi:application --bind 0.0.0.0:$PORT --workers 2 --threads 4"

