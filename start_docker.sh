#!/bin/bash
# Script de démarrage Docker pour le bot de candidature avec interface web

set -e

echo "🚀 Démarrage du bot de candidature avec interface web Docker"

# Vérifier que Docker est installé
if ! command -v docker &> /dev/null; then
    echo "❌ Docker n'est pas installé. Veuillez l'installer d'abord."
    exit 1
fi

# Vérifier que Docker Compose est installé
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose n'est pas installé. Veuillez l'installer d'abord."
    exit 1
fi

# Vérifier que les fichiers nécessaires existent
if [ ! -f "config.yaml" ]; then
    echo "❌ Fichier config.yaml manquant. Veuillez le créer d'abord."
    exit 1
fi

if [ ! -f ".env" ]; then
    echo "❌ Fichier .env manquant. Veuillez le créer d'abord."
    exit 1
fi

# Arrêter les conteneurs existants
echo "🛑 Arrêt des conteneurs existants..."
docker-compose down 2>/dev/null || true

# Construire l'image
echo "🔨 Construction de l'image Docker..."
docker-compose build

# Démarrer les services
echo "🚀 Démarrage des services..."
docker-compose up -d

# Attendre que le service soit prêt
echo "⏳ Attente du démarrage du service..."
sleep 10

# Vérifier le statut
echo "📊 Vérification du statut des services..."
docker-compose ps

# Afficher les logs
echo "📋 Logs du service bot-candidature:"
docker-compose logs bot-candidature

echo ""
echo "🎉 Bot de candidature démarré avec succès !"
echo ""
echo "🌐 Interface web accessible sur: http://localhost:7001"
echo "📱 Dashboard de surveillance et contrôle du bot"
echo ""
echo "📋 Commandes utiles:"
echo "   Voir les logs: docker-compose logs -f bot-candidature"
echo "   Arrêter: docker-compose down"
echo "   Redémarrer: docker-compose restart bot-candidature"
echo "   Statut: docker-compose ps"
echo ""
echo "💡 Ouvrez http://localhost:7000 dans votre navigateur pour accéder au dashboard !"
