#!/bin/bash

# Script de démarrage pour le bot de candidature automatique
# Usage: ./start.sh [option]

set -e

# Couleurs pour l'affichage
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Fonction d'affichage des messages
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Fonction d'aide
show_help() {
    echo "Usage: $0 [option]"
    echo ""
    echo "Options:"
    echo "  test       - Exécute les tests de vérification"
    echo "  once       - Lance le bot une seule fois"
    echo "  daemon     - Lance le bot en mode daemon (recommandé)"
    echo "  docker     - Lance avec Docker Compose"
    echo "  install    - Installe les dépendances"
    echo "  setup      - Configuration initiale"
    echo "  help       - Affiche cette aide"
    echo ""
    echo "Exemples:"
    echo "  $0 test     # Teste l'installation"
    echo "  $0 once     # Lance une collecte unique"
    echo "  $0 daemon   # Lance le bot en continu"
    echo "  $0 docker   # Lance avec Docker"
}

# Vérification de Python
check_python() {
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 n'est pas installé"
        exit 1
    fi
    
    python_version=$(python3 --version | cut -d' ' -f2)
    print_info "Python version: $python_version"
}

# Vérification des dépendances
check_dependencies() {
    print_info "Vérification des dépendances..."
    
    if [ ! -f "requirements.txt" ]; then
        print_error "Fichier requirements.txt non trouvé"
        exit 1
    fi
    
    if [ ! -f "config.yaml" ]; then
        print_warning "Fichier config.yaml non trouvé, création d'un exemple..."
        python3 test_bot.py
    fi
}

# Installation des dépendances
install_dependencies() {
    print_info "Installation des dépendances Python..."
    pip3 install -r requirements.txt
    
    print_info "Installation de Playwright..."
    playwright install chromium
    playwright install-deps chromium
    
    print_success "Dépendances installées avec succès"
}

# Configuration initiale
setup_initial() {
    print_info "Configuration initiale..."
    
    # Création des dossiers
    mkdir -p logs outbox temp cv_letters
    
    # Vérification du CV
    if [ ! -f "cv.pdf" ]; then
        print_warning "CV non trouvé (cv.pdf)"
        print_info "Placez votre CV au format PDF dans le dossier racine"
    fi
    
    # Test de la configuration
    print_info "Test de la configuration..."
    python3 test_bot.py
    
    print_success "Configuration initiale terminée"
}

# Test du bot
test_bot() {
    print_info "Exécution des tests..."
    python3 test_bot.py
}

# Lancement unique
run_once() {
    print_info "Lancement du bot en mode unique..."
    python3 bot.py --once
}

# Lancement en daemon
run_daemon() {
    print_info "Lancement du bot en mode daemon..."
    print_info "Le bot s'exécutera toutes les 6 heures et à 9h/18h"
    print_info "Appuyez sur Ctrl+C pour arrêter"
    
    python3 bot.py
}

# Lancement avec Docker
run_docker() {
    if ! command -v docker &> /dev/null; then
        print_error "Docker n'est pas installé"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose n'est pas installé"
        exit 1
    fi
    
    print_info "Lancement avec Docker Compose..."
    
    # Construction de l'image
    docker-compose build
    
    # Lancement des services
    docker-compose up -d
    
    print_success "Services Docker lancés"
    print_info "Logs: docker-compose logs -f bot-candidature"
    print_info "Arrêt: docker-compose down"
}

# Fonction principale
main() {
    case "${1:-help}" in
        "test")
            check_python
            check_dependencies
            test_bot
            ;;
        "once")
            check_python
            check_dependencies
            run_once
            ;;
        "daemon")
            check_python
            check_dependencies
            run_daemon
            ;;
        "docker")
            run_docker
            ;;
        "install")
            check_python
            install_dependencies
            ;;
        "setup")
            check_python
            install_dependencies
            setup_initial
            ;;
        "help"|*)
            show_help
            ;;
    esac
}

# Vérification des arguments
if [ $# -gt 1 ]; then
    print_error "Trop d'arguments"
    show_help
    exit 1
fi

# Exécution
main "$@"
