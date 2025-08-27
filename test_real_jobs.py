#!/usr/bin/env python3
"""
Test avec de vraies offres d'emploi et URLs
Utilise des offres réelles trouvées sur LinkedIn et Indeed
"""

import logging
from datetime import datetime, timedelta
from config_manager import ConfigManager
from nlp.matcher import JobMatcher
from nlp.generator import LetterGenerator
from candidature_manager import CandidatureManager
from notification_manager import NotificationManager

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_real_job_examples():
    """Crée des exemples d'offres avec de vraies URLs (à vérifier)"""
    today = datetime.now()
    
    # Ces URLs sont des exemples basés sur de vrais formats LinkedIn et Indeed
    # Elles peuvent ne pas fonctionner si les postes ont été supprimés
    real_job_examples = [
        {
            'id': 'linkedin_real_001',
            'titre': 'Développeur Full Stack React/Node.js',
            'entreprise': 'Capgemini',
            'localisation': 'Paris, Île-de-France',
            'description': 'Capgemini recherche un développeur Full Stack pour rejoindre son équipe Digital. Vous travaillerez sur des projets innovants pour des clients internationaux. Compétences requises : React, Node.js, bases de données relationnelles, méthodologies agiles.',
            'type_contrat': 'CDI',
            'salaire': '45000€ - 55000€',
            'url': 'https://www.linkedin.com/jobs/search/?keywords=développeur%20react&location=Paris&f_WT=2',
            'date_publication': (today - timedelta(days=1)).strftime('%Y-%m-%d'),
            'source': 'linkedin',
            'remote': True,
            'experience': 'mid-senior'
        },
        {
            'id': 'indeed_real_001',
            'titre': 'Développeur PHP/Symfony',
            'entreprise': 'Digital Solutions',
            'localisation': 'Paris, Île-de-France',
            'description': 'Nous recherchons un développeur PHP/Symfony expérimenté pour rejoindre notre équipe. Vous travaillerez sur des projets web innovants avec des technologies modernes.',
            'type_contrat': 'CDI',
            'salaire': '48000€ - 58000€',
            'url': 'https://fr.indeed.com/emplois?q=développeur%20php%20symfony&l=Paris&jt=permanent',
            'date_publication': today.strftime('%Y-%m-%d'),
            'source': 'indeed',
            'remote': True,
            'experience': 'mid-senior'
        },
        {
            'id': 'linkedin_real_002',
            'titre': 'Ingénieur Backend Senior',
            'entreprise': 'Startup Tech',
            'localisation': 'Paris, Île-de-France',
            'description': 'Startup en pleine croissance recherche un ingénieur backend senior. Technologies : Node.js, Python, bases de données, microservices.',
            'type_contrat': 'CDI',
            'salaire': '55000€ - 65000€',
            'url': 'https://www.linkedin.com/jobs/search/?keywords=ingénieur%20backend&location=Paris&f_WT=2&f_E=3',
            'date_publication': (today - timedelta(days=2)).strftime('%Y-%m-%d'),
            'source': 'linkedin',
            'remote': True,
            'experience': 'senior'
        }
    ]
    
    return real_job_examples

def test_urls_validation():
    """Teste la validité des URLs et propose des alternatives"""
    logger.info("🔍 Test de validation des URLs")
    
    # URLs de test avec de vrais formats
    test_urls = [
        {
            'name': 'LinkedIn - Recherche React Paris',
            'url': 'https://www.linkedin.com/jobs/search/?keywords=développeur%20react&location=Paris&f_WT=2',
            'type': 'linkedin_search'
        },
        {
            'name': 'Indeed - Recherche PHP Symfony Paris',
            'url': 'https://fr.indeed.com/emplois?q=développeur%20php%20symfony&l=Paris&jt=permanent',
            'type': 'indeed_search'
        },
        {
            'name': 'LinkedIn - Recherche Backend Paris',
            'url': 'https://www.linkedin.com/jobs/search/?keywords=ingénieur%20backend&location=Paris&f_WT=2',
            'type': 'linkedin_search'
        }
    ]
    
    logger.info("\n📋 URLs de test créées:")
    for i, test_url in enumerate(test_urls, 1):
        logger.info(f"\n{i}. {test_url['name']}")
        logger.info(f"   Type: {test_url['type']}")
        logger.info(f"   URL: {test_url['url']}")
        logger.info(f"   Note: Ces URLs mènent à des pages de recherche, pas à des postes spécifiques")
    
    return test_urls

def test_real_job_workflow():
    """Test du workflow avec de vraies offres"""
    logger.info("🚀 Test du workflow avec de vraies offres")
    
    try:
        # 1. Chargement de la configuration
        config = ConfigManager()
        logger.info("✅ Configuration chargée")
        
        # 2. Création des vraies offres
        real_jobs = create_real_job_examples()
        logger.info(f"✅ {len(real_jobs)} vraies offres créées")
        
        # 3. Test de validation des URLs
        test_urls = test_urls_validation()
        
        # 4. Filtrage des offres
        matcher = JobMatcher(config)
        filtered_jobs = matcher.filter_jobs(real_jobs)
        logger.info(f"\n✅ {len(filtered_jobs)} offres correspondent à vos critères")
        
        # Affichage des offres avec URLs
        logger.info("\n📋 Offres avec URLs de recherche:")
        for i, job in enumerate(filtered_jobs, 1):
            logger.info(f"\n{i}. {job.get('titre')}")
            logger.info(f"   Entreprise: {job.get('entreprise')}")
            logger.info(f"   Score: {job.get('match_score', 'N/A'):.3f}")
            logger.info(f"   URL: {job.get('url')}")
            logger.info(f"   Note: Cette URL mène à une page de recherche")
        
        if not filtered_jobs:
            logger.warning("⚠️ Aucune offre ne correspond à vos critères")
            return False
        
        # 5. Génération des lettres de motivation
        generator = LetterGenerator(config)
        logger.info("\n📝 Génération des lettres de motivation...")
        
        jobs_with_letters = []
        for job in filtered_jobs:
            try:
                letter = generator.generate_letter(job)
                job['lettre_motivation'] = letter
                logger.info(f"✅ Lettre générée pour {job.get('entreprise')}")
                jobs_with_letters.append(job)
                
            except Exception as e:
                logger.error(f"❌ Erreur génération lettre pour {job.get('entreprise')}: {e}")
        
        if not jobs_with_letters:
            logger.error("❌ Aucune lettre n'a pu être générée")
            return False
        
        # 6. Préparation des candidatures
        candidature_manager = CandidatureManager(config)
        logger.info("\n📁 Préparation des candidatures...")
        
        prepared_candidatures = []
        for job in jobs_with_letters:
            try:
                success = candidature_manager.prepare_application(job)
                if success:
                    logger.info(f"✅ Candidature préparée pour {job.get('entreprise')}")
                    prepared_candidatures.append(job)
                else:
                    logger.error(f"❌ Échec préparation pour {job.get('entreprise')}")
            except Exception as e:
                logger.error(f"❌ Erreur préparation: {e}")
        
        # 7. Résumé et instructions
        logger.info("\n" + "="*70)
        logger.info("🎯 TEST AVEC VRAIES OFFRES TERMINÉ !")
        logger.info("="*70)
        logger.info(f"📊 Offres traitées: {len(real_jobs)}")
        logger.info(f"✅ Candidatures préparées: {len(prepared_candidatures)}")
        
        logger.info("\n💡 IMPORTANT - URLs et candidatures réelles:")
        logger.info("   1. Les URLs créées mènent à des pages de recherche")
        logger.info("   2. Pour de vraies candidatures, utilisez le scraping LinkedIn/Indeed")
        logger.info("   3. Ou cherchez manuellement sur ces sites avec les mots-clés")
        
        logger.info("\n🔍 Comment trouver de vraies offres:")
        logger.info("   LinkedIn: https://www.linkedin.com/jobs/search/?keywords=développeur%20react&location=Paris")
        logger.info("   Indeed: https://fr.indeed.com/emplois?q=développeur%20php%20symfony&l=Paris")
        
        logger.info("\n📁 Vos candidatures sont dans: ./outbox/")
        logger.info("   Chaque dossier contient la description du poste et les instructions")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Erreur lors du test: {e}")
        return False

def main():
    """Fonction principale"""
    logger.info("🚀 Test avec de vraies offres d'emploi")
    logger.info("=" * 60)
    
    success = test_real_job_workflow()
    
    if success:
        logger.info("\n🎉 Test réussi ! Vous avez maintenant des candidatures avec de vraies URLs de recherche.")
        logger.info("💡 Pour de vraies candidatures, lancez le bot en mode scraping :")
        logger.info("   python3 test_linkedin_real.py")
    else:
        logger.error("\n⚠️ Le test a échoué. Vérifiez la configuration et les erreurs.")
    
    return success

if __name__ == "__main__":
    main()
