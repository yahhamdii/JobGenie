# Dockerfile pour le bot de candidature automatique
# Utilise l'image Playwright officielle avec Python et navigateurs préinstallés
FROM mcr.microsoft.com/playwright/python:v1.40.0-jammy

# Métadonnées
LABEL maintainer="Bot Candidature"
LABEL description="Bot de candidature automatique pour sites d'emploi"
LABEL version="1.0.0"

# Variables d'environnement
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV DEBIAN_FRONTEND=noninteractive

# Dépendances système déjà gérées par l'image Playwright

# Création du répertoire de travail
WORKDIR /jobgenie

# Copie des fichiers de dépendances
COPY requirements.txt .

# Installation des dépendances Python
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Navigateurs déjà installés dans l'image Playwright

# Copie du code source
COPY . .

# Création des dossiers nécessaires et permissions
RUN mkdir -p logs outbox temp cv_letters && \
    chown -R pwuser:pwuser /jobgenie

# Utilisateur non-root par défaut dans l'image: pwuser
USER pwuser

# Exposition du port (optionnel, pour une interface web future)
EXPOSE 8000

# Exposer le port 7001 pour l'interface web
EXPOSE 7001

# Commande par défaut - lance l'interface web
CMD ["python", "web_interface.py"]
