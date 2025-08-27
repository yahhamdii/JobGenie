# Dockerfile pour le bot de candidature automatique
FROM python:3.11-slim

# Métadonnées
LABEL maintainer="Bot Candidature"
LABEL description="Bot de candidature automatique pour sites d'emploi"
LABEL version="1.0.0"

# Variables d'environnement
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV DEBIAN_FRONTEND=noninteractive

# Installation des dépendances système
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    ca-certificates \
    procps \
    libxss1 \
    libnss3 \
    libatk-bridge2.0-0 \
    libdrm2 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    libgbm1 \
    libasound2 \
    libxshmfence1 \
    libx11-xcb1 \
    libxcb-dri3-0 \
    libxcb1 \
    libxss1 \
    libxrandr2 \
    libxcomposite1 \
    libxdamage1 \
    libxext6 \
    libxfixes3 \
    libxrender1 \
    libxtst6 \
    libxi6 \
    libxrandr2 \
    libxss1 \
    libxcomposite1 \
    libxdamage1 \
    libxext6 \
    libxfixes3 \
    libxrender1 \
    libxtst6 \
    libxi6 \
    && rm -rf /var/lib/apt/lists/*

# Création du répertoire de travail
WORKDIR /jobgenie

# Copie des fichiers de dépendances
COPY requirements.txt .

# Installation des dépendances Python
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Installation de Playwright
RUN playwright install chromium
RUN playwright install-deps chromium

# Copie du code source
COPY . .

# Création des dossiers nécessaires
RUN mkdir -p logs outbox temp cv_letters

# Création d'un utilisateur non-root
RUN useradd --create-home --shell /bin/bash botuser && \
    chown -R botuser:botuser /app

# Changement vers l'utilisateur non-root
USER botuser

# Exposition du port (optionnel, pour une interface web future)
EXPOSE 8000

# Exposer le port 7001 pour l'interface web
EXPOSE 7001

# Commande par défaut - lance l'interface web
CMD ["python", "web_interface.py"]
