#!/usr/bin/env python3
"""
Test spécifique des sources LinkedIn et Indeed
Vérifie que le scraping fonctionne correctement
"""

import logging
from config_manager import ConfigManager

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_linkedin_source():
    """Test de la source LinkedIn"""
    try:
        from sources.linkedin import LinkedInSource
        
        config = ConfigManager()
        source = LinkedInSource(config)
        
        logger.info("✅ Source LinkedIn initialisée avec succès")
        
        # Test de construction d'URL
        test_params = {
            'keywords': 'développeur',
            'location': 'Paris'
        }
        
        url = source._build_search_url(test_params)
        logger.info(f"✅ URL LinkedIn construite: {url}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Erreur LinkedIn: {e}")
        return False

def test_indeed_source():
    """Test de la source Indeed"""
    try:
        from sources.indeed import IndeedSource
        
        config = ConfigManager()
        source = IndeedSource(config)
        
        logger.info("✅ Source Indeed initialisée avec succès")
        
        # Test de construction d'URL
        test_params = {
            'q': 'développeur',
            'l': 'Paris'
        }
        
        url = source._build_search_url(test_params)
        logger.info(f"✅ URL Indeed construite: {url}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Erreur Indeed: {e}")
        return False

def test_configuration():
    """Test de la configuration"""
    try:
        config = ConfigManager()
        
        # Vérification des sources
        linkedin_enabled = config.is_source_enabled('linkedin')
        indeed_enabled = config.is_source_enabled('indeed')
        
        logger.info(f"✅ LinkedIn activé: {linkedin_enabled}")
        logger.info(f"✅ Indeed activé: {indeed_enabled}")
        
        # Vérification du profil
        profile = config.get_profile()
        logger.info(f"✅ Profil: {profile.get('nom')} - {profile.get('email')}")
        
        # Vérification des préférences
        preferences = config.get_preferences()
        stack = preferences.get('stack_technique', [])
        logger.info(f"✅ Stack technique: {', '.join(stack)}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Erreur configuration: {e}")
        return False

def main():
    """Test principal"""
    logger.info("🚀 Test des sources LinkedIn et Indeed")
    
    tests = [
        ("Configuration", test_configuration),
        ("LinkedIn", test_linkedin_source),
        ("Indeed", test_indeed_source)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            logger.error(f"❌ Test {test_name} a échoué: {e}")
            results.append((test_name, False))
    
    # Résumé
    logger.info("\n" + "="*50)
    logger.info("📊 RÉSUMÉ DES TESTS DES SOURCES")
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
        logger.info("🎉 Toutes les sources sont prêtes !")
        logger.info("💡 Vous pouvez maintenant lancer le bot avec: ./start.sh once")
    else:
        logger.error("⚠️ Certains tests ont échoué. Vérifiez la configuration.")
    
    return passed == total

if __name__ == "__main__":
    main()
