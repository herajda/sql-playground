# ─── Dockerfile (patched) ─────────────────────────────────────────
# syntax=docker/dockerfile:1

############################
# 1 Build the front-end SPA
############################
FROM node:20-alpine AS frontend-builder
WORKDIR /app/frontend

# install JS deps first (cache-friendly)
COPY frontend/package*.json ./
RUN npm ci

# copy the rest and build
COPY frontend .
RUN npm run build        # -> /app/frontend/dist

############################
# 2 Run the Python back-end
############################
FROM python:3.11-slim AS runtime
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app

# system libs
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc libsqlite3-dev && \
    rm -rf /var/lib/apt/lists/*

# Python deps
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt gunicorn

# project source
COPY . .

# **NEW** – pull the compiled SPA from the first stage
# (overwrites any old /app/static folder)
RUN rm -rf static
COPY --from=frontend-builder /app/frontend/dist/ ./app/static/

# optional: seed the default SQLite DB
RUN python init_db.py

EXPOSE 5000
ENV ADMIN_PASSWORD=admin123 FLASK_ENV=production
CMD ["gunicorn", "-b", "0.0.0.0:5000", "run:app"]
# ─────────────────────────────────────────────────────────────────

