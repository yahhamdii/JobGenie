#!/usr/bin/env python3
"""
Script de démonstration du bot de candidature
Simule des offres d'emploi pour tester le système complet
"""

import logging
from config_manager import ConfigManager
from nlp.matcher import JobMatcher
from nlp.generator import LetterGenerator
from candidature_manager import CandidatureManager
from notification_manager import NotificationManager

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_demo_jobs():
    """Crée des offres d'emploi de démonstration"""
    demo_jobs = [
        {
            'id': 'demo_001',
            'titre': 'Développeur Full Stack React/Node.js',
            'entreprise': 'TechCorp Paris',
            'localisation': 'Paris, Île-de-France',
            'description': 'Nous recherchons un développeur Full Stack expérimenté en React, Node.js et PHP. Vous travaillerez sur des projets innovants avec une équipe dynamique.',
            'type_contrat': 'CDI',
            'salaire': '45000€ - 55000€',
            'url': 'https://example.com/job1',
            'date_publication': '2024-01-15',
            'source': 'linkedin'
        },
        {
            'id': 'demo_002',
            'titre': 'Ingénieur Backend PHP/Symfony',
            'entreprise': 'Digital Solutions',
            'localisation': 'Remote',
            'description': 'Poste d\'ingénieur backend spécialisé en PHP/Symfony. Architecture microservices, bases de données relationnelles, API REST.',
            'type_contrat': 'CDI',
            'salaire': '50000€ - 60000€',
            'url': 'https://example.com/job2',
            'date_publication': '2024-01-14',
            'source': 'indeed'
        },
        {
            'id': 'demo_003',
            'titre': 'Développeur Frontend React Senior',
            'entreprise': 'Startup Innovation',
            'localisation': 'Paris, Île-de-France',
            'description': 'Développeur frontend senior React pour une startup en pleine croissance. Interface utilisateur moderne, performance, accessibilité.',
            'type_contrat': 'CDI',
            'salaire': '55000€ - 65000€',
            'url': 'https://example.com/job3',
            'date_publication': '2024-01-13',
            'source': 'linkedin'
        }
    ]
    
    return demo_jobs

def test_complete_workflow():
    """Test du workflow complet du bot"""
    logger.info("🚀 Démonstration du workflow complet du bot")
    
    try:
        # 1. Chargement de la configuration
        config = ConfigManager()
        logger.info("✅ Configuration chargée")
        
        # 2. Création des offres de démonstration
        demo_jobs = create_demo_jobs()
        logger.info(f"✅ {len(demo_jobs)} offres de démonstration créées")
        
        # 3. Filtrage des offres
        matcher = JobMatcher(config)
        filtered_jobs = matcher.filter_jobs(demo_jobs)
        logger.info(f"✅ {len(filtered_jobs)} offres filtrées selon vos préférences")
        
        # Affichage des offres filtrées
        for i, job in enumerate(filtered_jobs, 1):
            logger.info(f"\n📋 Offre {i}:")
            logger.info(f"   Titre: {job.get('titre')}")
            logger.info(f"   Entreprise: {job.get('entreprise')}")
            logger.info(f"   Localisation: {job.get('localisation')}")
            logger.info(f"   Score: {job.get('match_score', 'N/A')}")
        
        if not filtered_jobs:
            logger.warning("⚠️ Aucune offre ne correspond à vos critères")
            return False
        
        # 4. Génération des lettres de motivation
        generator = LetterGenerator(config)
        logger.info("\n📝 Génération des lettres de motivation...")
        
        jobs_with_letters = []
        for job in filtered_jobs:
            try:
                letter = generator.generate_letter(job)
                job['lettre_motivation'] = letter
                logger.info(f"✅ Lettre générée pour {job.get('titre')}")
                jobs_with_letters.append(job)
            except Exception as e:
                logger.error(f"❌ Erreur génération lettre: {e}")
        
        if not jobs_with_letters:
            logger.error("❌ Aucune lettre n'a pu être générée")
            return False
        
        # 5. Préparation des candidatures
        candidature_manager = CandidatureManager(config)
        logger.info("\n📁 Préparation des candidatures...")
        
        for job in jobs_with_letters:
            try:
                success = candidature_manager.prepare_application(job)
                if success:
                    logger.info(f"✅ Candidature préparée pour {job.get('titre')}")
                else:
                    logger.error(f"❌ Échec préparation pour {job.get('titre')}")
            except Exception as e:
                logger.error(f"❌ Erreur préparation: {e}")
        
        # 6. Test des notifications
        notification_manager = NotificationManager(config)
        logger.info("\n📧 Test des notifications...")
        
        notif_status = notification_manager.get_notification_status()
        logger.info(f"✅ Statut notifications: {notif_status}")
        
        # 7. Résumé final
        logger.info("\n" + "="*60)
        logger.info("🎉 DÉMONSTRATION TERMINÉE AVEC SUCCÈS !")
        logger.info("="*60)
        logger.info(f"📊 Offres traitées: {len(jobs_with_letters)}")
        logger.info(f"📝 Lettres générées: {len(jobs_with_letters)}")
        logger.info(f"📁 Candidatures préparées dans: ./outbox/")
        
        # Affichage des dossiers créés
        import os
        if os.path.exists('outbox'):
            candidatures = [d for d in os.listdir('outbox') if os.path.isdir(os.path.join('outbox', d))]
            logger.info(f"📂 Dossiers de candidature créés: {len(candidatures)}")
            for candidature in candidatures[:3]:  # Afficher les 3 premiers
                logger.info(f"   - {candidature}")
        
        logger.info("\n💡 Prochaines étapes:")
        logger.info("   1. Consultez les candidatures dans ./outbox/")
        logger.info("   2. Vérifiez les lettres générées")
        logger.info("   3. Envoyez manuellement via les sites web")
        logger.info("   4. Mettez à jour les fichiers de suivi")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Erreur lors de la démonstration: {e}")
        return False

def main():
    """Fonction principale"""
    success = test_complete_workflow()
    
    if success:
        logger.info("\n🎯 Le bot est prêt à fonctionner !")
        logger.info("🚀 Lancez-le avec: ./start.sh daemon")
    else:
        logger.error("\n⚠️ La démonstration a échoué. Vérifiez la configuration.")
    
    return success

if __name__ == "__main__":
    main()
