FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    libjpeg-dev \
    zlib1g-dev \
    fonts-dejavu-core \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p /app/media/images /app/media/files /app/staticfiles
RUN chmod +x entrypoint.sh wait_for_migrations.sh

EXPOSE 8000

CMD ["sh", "entrypoint.sh"]
