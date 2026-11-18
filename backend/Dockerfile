# Build from the repo root (docker-compose.yml does this) so models/ can be copied in.
FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /srv/backend

# dependencies first: this layer is reused until requirements.txt changes
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/app ./app
COPY backend/scripts ./scripts
# config.py looks for models/ next to backend/, i.e. /srv/models
COPY models /srv/models

# don't run as root inside the container
RUN useradd --create-home glyco
USER glyco

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]