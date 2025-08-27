#!/usr/bin/env python3
"""
Script de test pour vérifier le bon fonctionnement du bot de candidature
Teste les composants principaux sans effectuer de vraies candidatures
"""

import os
import sys
import logging
from pathlib import Path

# Configuration du logging pour les tests
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_imports():
    """Teste l'importation de tous les modules"""
    logger.info("=== Test des imports ===")
    
    try:
        from config_manager import ConfigManager
        logger.info("✅ ConfigManager importé avec succès")
    except ImportError as e:
        logger.error(f"❌ Erreur import ConfigManager: {e}")
        return False
    
    try:
        from sources.france_travail import FranceTravailSource
        logger.info("✅ FranceTravailSource importé avec succès")
    except ImportError as e:
        logger.error(f"❌ Erreur import FranceTravailSource: {e}")
        return False
    
    try:
        from sources.linkedin import LinkedInSource
        logger.info("✅ LinkedInSource importé avec succès")
    except ImportError as e:
        logger.error(f"❌ Erreur import LinkedInSource: {e}")
        return False
    
    try:
        from sources.indeed import IndeedSource
        logger.info("✅ IndeedSource importé avec succès")
    except ImportError as e:
        logger.error(f"❌ Erreur import IndeedSource: {e}")
        return False
    
    try:
        from nlp.matcher import JobMatcher
        logger.info("✅ JobMatcher importé avec succès")
    except ImportError as e:
        logger.error(f"❌ Erreur import JobMatcher: {e}")
        return False
    
    try:
        from nlp.generator import LetterGenerator
        logger.info("✅ LetterGenerator importé avec succès")
    except ImportError as e:
        logger.error(f"❌ Erreur import LetterGenerator: {e}")
        return False
    
    try:
        from candidature_manager import CandidatureManager
        logger.info("✅ CandidatureManager importé avec succès")
    except ImportError as e:
        logger.error(f"❌ Erreur import CandidatureManager: {e}")
        return False
    
    try:
        from notification_manager import NotificationManager
        logger.info("✅ NotificationManager importé avec succès")
    except ImportError as e:
        logger.error(f"❌ Erreur import NotificationManager: {e}")
        return False
    
    logger.info("✅ Tous les imports réussis")
    return True

def test_configuration():
    """Teste la configuration du bot"""
    logger.info("=== Test de la configuration ===")
    
    try:
        from config_manager import ConfigManager
        
        # Test avec un fichier de config existant
        if not os.path.exists('config.yaml'):
            logger.warning("⚠️ Fichier config.yaml non trouvé, création d'un exemple")
            create_example_config()
        
        config = ConfigManager()
        logger.info("✅ Configuration chargée avec succès")
        
        # Test des méthodes de configuration
        profile = config.get_profile()
        logger.info(f"✅ Profil récupéré: {profile.get('nom', 'N/A')}")
        
        preferences = config.get_preferences()
        logger.info(f"✅ Préférences récupérées: {len(preferences)} sections")
        
        sources = config.get_sources()
        logger.info(f"✅ Sources configurées: {len(sources)} sources")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Erreur lors du test de configuration: {e}")
        return False

def create_example_config():
    """Crée un fichier de configuration d'exemple"""
    example_config = """# Configuration d'exemple pour le bot de candidature
profile:
  nom: "Utilisateur Test"
  email: "test@example.com"
  telephone: "+33 6 12 34 56 78"
  linkedin: "https://linkedin.com/in/test"
  cv_path: "./example_cv.pdf"

preferences:
  stack_technique: ["Python", "JavaScript", "React"]
  localisation: ["Paris", "Remote"]
  type_contrat: ["CDI", "Freelance"]
  salaire_min: 40000
  mots_cles: ["développeur", "ingénieur"]

api_keys:
  france_travail: "VOTRE_TOKEN_API_FRANCE_TRAVAIL"
  openai: "VOTRE_CLE_API_OPENAI"

sources:
  france_travail:
    enabled: false
    url: "https://api.pole-emploi.io/partenaire/offresdemploi/v2/offres/search"
  linkedin:
    enabled: false
    base_url: "https://www.linkedin.com/jobs/search/"
  indeed:
    enabled: false
    base_url: "https://fr.indeed.com/emplois"

generation:
  mode: "semi_auto"
  llm_provider: "openai"
  ollama_model: "llama3"

notifications:
  email: false
  slack: false
  webhook: ""
"""
    
    with open('config.yaml', 'w', encoding='utf-8') as f:
        f.write(example_config)
    
    logger.info("✅ Fichier config.yaml d'exemple créé")

def test_sources():
    """Teste les sources d'offres d'emploi"""
    logger.info("=== Test des sources ===")
    
    try:
        from config_manager import ConfigManager
        from sources.france_travail import FranceTravailSource
        from sources.linkedin import LinkedInSource
        from sources.indeed import IndeedSource
        
        config = ConfigManager()
        
        # Test France Travail (sans API key)
        if config.is_source_enabled('france_travail'):
            source = FranceTravailSource(config)
            logger.info("✅ Source France Travail initialisée")
        else:
            logger.info("ℹ️ Source France Travail désactivée")
        
        # Test LinkedIn
        if config.is_source_enabled('linkedin'):
            source = LinkedInSource(config)
            logger.info("✅ Source LinkedIn initialisée")
        else:
            logger.info("ℹ️ Source LinkedIn désactivée")
        
        # Test Indeed
        if config.is_source_enabled('indeed'):
            source = IndeedSource(config)
            logger.info("✅ Source Indeed initialisée")
        else:
            logger.info("ℹ️ Source Indeed désactivée")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Erreur lors du test des sources: {e}")
        return False

def test_nlp_modules():
    """Teste les modules NLP"""
    logger.info("=== Test des modules NLP ===")
    
    try:
        from config_manager import ConfigManager
        from nlp.matcher import JobMatcher
        from nlp.generator import LetterGenerator
        
        config = ConfigManager()
        
        # Test du matcher
        matcher = JobMatcher(config)
        logger.info("✅ JobMatcher initialisé")
        
        # Test du générateur
        generator = LetterGenerator(config)
        logger.info("✅ LetterGenerator initialisé")
        
        # Test des statistiques
        stats = generator.get_generation_stats()
        logger.info(f"✅ Statistiques de génération: {stats}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Erreur lors du test des modules NLP: {e}")
        return False

def test_managers():
    """Teste les gestionnaires"""
    logger.info("=== Test des gestionnaires ===")
    
    try:
        from config_manager import ConfigManager
        from candidature_manager import CandidatureManager
        from notification_manager import NotificationManager
        
        config = ConfigManager()
        
        # Test du gestionnaire de candidatures
        candidature_manager = CandidatureManager(config)
        logger.info("✅ CandidatureManager initialisé")
        
        # Test du gestionnaire de notifications
        notification_manager = NotificationManager(config)
        logger.info("✅ NotificationManager initialisé")
        
        # Test du statut des notifications
        notif_status = notification_manager.get_notification_status()
        logger.info(f"✅ Statut des notifications: {notif_status}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Erreur lors du test des gestionnaires: {e}")
        return False

def test_directories():
    """Teste la création des dossiers"""
    logger.info("=== Test de la création des dossiers ===")
    
    try:
        directories = ['logs', 'outbox', 'temp', 'cv_letters']
        
        for directory in directories:
            Path(directory).mkdir(exist_ok=True)
            logger.info(f"✅ Dossier {directory} créé/vérifié")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Erreur lors de la création des dossiers: {e}")
        return False

def run_all_tests():
    """Exécute tous les tests"""
    logger.info("🚀 Démarrage des tests du bot de candidature")
    
    tests = [
        ("Imports", test_imports),
        ("Configuration", test_configuration),
        ("Sources", test_sources),
        ("Modules NLP", test_nlp_modules),
        ("Gestionnaires", test_managers),
        ("Dossiers", test_directories)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            logger.error(f"❌ Test {test_name} a échoué avec une exception: {e}")
            results.append((test_name, False))
    
    # Résumé des tests
    logger.info("\n" + "="*50)
    logger.info("📊 RÉSUMÉ DES TESTS")
    logger.info("="*50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSÉ" if result else "❌ ÉCHOUÉ"
        logger.info(f"{test_name}: {status}")
        if result:
            passed += 1
    
    logger.info(f"\nRésultat: {passed}/{total} tests réussis")
    
    if passed == total:
        logger.info("🎉 Tous les tests sont passés ! Le bot est prêt à fonctionner.")
        return True
    else:
        logger.error(f"⚠️ {total - passed} test(s) ont échoué. Vérifiez la configuration.")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
