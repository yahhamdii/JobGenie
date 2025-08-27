#!/bin/bash
# Script de test Docker pour le bot de candidature

set -e

echo "🧪 Test Docker - Bot de Candidature Automatique"
echo "================================================"

# Vérifier Docker
echo "🔍 Vérification de Docker..."
if ! command -v docker &> /dev/null; then
    echo "❌ Docker n'est pas installé"
    exit 1
fi
echo "✅ Docker installé: $(docker --version)"

# Vérifier Docker Compose
echo "🔍 Vérification de Docker Compose..."
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose n'est pas installé"
    exit 1
fi
echo "✅ Docker Compose installé: $(docker-compose --version)"

# Vérifier les fichiers nécessaires
echo "🔍 Vérification des fichiers de configuration..."
if [ ! -f "config.yaml" ]; then
    echo "❌ config.yaml manquant"
    exit 1
fi
echo "✅ config.yaml trouvé"

if [ ! -f ".env" ]; then
    echo "❌ .env manquant"
    exit 1
fi
echo "✅ .env trouvé"

if [ ! -f "Dockerfile" ]; then
    echo "❌ Dockerfile manquant"
    exit 1
fi
echo "✅ Dockerfile trouvé"

if [ ! -f "docker-compose.yml" ]; then
    echo "❌ docker-compose.yml manquant"
    exit 1
fi
echo "✅ docker-compose.yml trouvé"

# Vérifier la configuration Docker Compose
echo "🔍 Validation de la configuration Docker Compose..."
if ! docker-compose config > /dev/null 2>&1; then
    echo "❌ Erreur dans docker-compose.yml"
    docker-compose config
    exit 1
fi
echo "✅ Configuration Docker Compose valide"

# Vérifier que le port 7001 est libre
echo "🔍 Vérification du port 7001..."
if lsof -i :7001 > /dev/null 2>&1; then
    echo "⚠️ Port 7001 déjà utilisé par:"
    lsof -i :7001
    echo "Arrêtez le processus ou changez le port"
    exit 1
fi
echo "✅ Port 7001 libre"

# Test de construction de l'image
echo "🔨 Test de construction de l'image Docker..."
if ! docker-compose build --no-cache > /dev/null 2>&1; then
    echo "❌ Erreur lors de la construction de l'image"
    docker-compose build --no-cache
    exit 1
fi
echo "✅ Image Docker construite avec succès"

# Test de démarrage des services
echo "🚀 Test de démarrage des services..."
if ! docker-compose up -d > /dev/null 2>&1; then
    echo "❌ Erreur lors du démarrage des services"
    docker-compose up -d
    exit 1
fi
echo "✅ Services démarrés"

# Attendre que le service soit prêt
echo "⏳ Attente du démarrage du service..."
sleep 15

# Vérifier le statut des services
echo "📊 Statut des services:"
docker-compose ps

# Test de l'interface web
echo "🌐 Test de l'interface web..."
if curl -s -f http://localhost:7001 > /dev/null; then
    echo "✅ Interface web accessible sur http://localhost:7001"
else
    echo "❌ Interface web non accessible"
    echo "Logs du service:"
    docker-compose logs bot-candidature
    exit 1
fi

# Test de l'API
echo "🔌 Test de l'API..."
if curl -s -f http://localhost:7001/api/status > /dev/null; then
    echo "✅ API accessible"
else
    echo "❌ API non accessible"
fi

# Affichage des informations
echo ""
echo "🎉 Tests Docker réussis !"
echo ""
echo "📋 Informations:"
echo "   🌐 Interface web: http://localhost:7001"
echo "   📊 Statut: docker-compose ps"
echo "   📋 Logs: docker-compose logs -f bot-candidature"
echo "   🛑 Arrêt: docker-compose down"
echo ""
echo "💡 Ouvrez http://localhost:7001 dans votre navigateur !"

# Optionnel: arrêter les services après le test
read -p "Voulez-vous arrêter les services après le test ? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🛑 Arrêt des services..."
    docker-compose down
    echo "✅ Services arrêtés"
fi
