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

# start da aplicação
CMD ["sh", "-c", "gunicorn obd.wsgi:application --bind 0.0.0.0:${PORT} --log-file -"]
