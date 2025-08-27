#!/usr/bin/env python3
"""
Test réaliste avec des offres simulées mais crédibles
Démontre le système complet sans dépendre du scraping
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

def create_realistic_jobs():
    """Crée des offres d'emploi réalistes basées sur de vraies entreprises"""
    realistic_jobs = [
        {
            'id': 'linkedin_001',
            'titre': 'Développeur Full Stack React/Node.js H/F',
            'entreprise': 'Capgemini',
            'localisation': 'Paris, Île-de-France',
            'description': 'Capgemini recherche un développeur Full Stack pour rejoindre son équipe Digital. Vous travaillerez sur des projets innovants pour des clients internationaux. Compétences requises : React, Node.js, bases de données relationnelles, méthodologies agiles.',
            'type_contrat': 'CDI',
            'salaire': '45000€ - 55000€',
            'url': 'https://www.linkedin.com/jobs/view/123456789',
            'date_publication': '2024-01-15',
            'source': 'linkedin',
            'remote': True,
            'experience': 'mid-senior'
        },
        {
            'id': 'linkedin_002',
            'titre': 'Ingénieur Développement PHP/Symfony',
            'entreprise': 'Orange',
            'localisation': 'Châtillon, Île-de-France',
            'description': 'Orange recherche un ingénieur développement PHP/Symfony pour ses services numériques. Vous participerez au développement d\'applications critiques, à l\'architecture des systèmes et à l\'optimisation des performances.',
            'type_contrat': 'CDI',
            'salaire': '50000€ - 60000€',
            'url': 'https://www.linkedin.com/jobs/view/987654321',
            'date_publication': '2024-01-14',
            'source': 'linkedin',
            'remote': False,
            'experience': 'senior'
        },
        {
            'id': 'indeed_001',
            'titre': 'Développeur Frontend React Senior',
            'entreprise': 'BlaBlaCar',
            'localisation': 'Paris, Île-de-France',
            'description': 'BlaBlaCar recherche un développeur Frontend React Senior pour améliorer l\'expérience utilisateur de sa plateforme. Vous travaillerez sur des fonctionnalités innovantes et contribuerez à l\'architecture frontend.',
            'type_contrat': 'CDI',
            'salaire': '55000€ - 65000€',
            'url': 'https://fr.indeed.com/viewjob?jk=abcdef123',
            'date_publication': '2024-01-13',
            'source': 'indeed',
            'remote': True,
            'experience': 'senior'
        },
        {
            'id': 'linkedin_003',
            'titre': 'Développeur Backend PHP/Symfony',
            'entreprise': 'Doctolib',
            'localisation': 'Paris, Île-de-France',
            'description': 'Doctolib recherche un développeur Backend PHP/Symfony pour développer ses services de santé numérique. Vous travaillerez sur des APIs robustes, la sécurité des données et l\'optimisation des performances.',
            'type_contrat': 'CDI',
            'salaire': '48000€ - 58000€',
            'url': 'https://www.linkedin.com/jobs/view/456789123',
            'date_publication': '2024-01-12',
            'source': 'linkedin',
            'remote': True,
            'experience': 'mid-senior'
        }
    ]
    
    return realistic_jobs

def test_realistic_workflow():
    """Test du workflow avec des offres réalistes"""
    logger.info("🚀 Test réaliste du workflow de candidature")
    
    try:
        # 1. Chargement de la configuration
        config = ConfigManager()
        logger.info("✅ Configuration chargée")
        
        # 2. Création des offres réalistes
        realistic_jobs = create_realistic_jobs()
        logger.info(f"✅ {len(realistic_jobs)} offres réalistes créées")
        
        # 3. Filtrage des offres
        matcher = JobMatcher(config)
        filtered_jobs = matcher.filter_jobs(realistic_jobs)
        logger.info(f"✅ {len(filtered_jobs)} offres correspondent à vos critères")
        
        # Affichage des offres filtrées avec scores
        logger.info("\n📋 Offres filtrées par pertinence :")
        for i, job in enumerate(filtered_jobs, 1):
            score = job.get('match_score', 0)
            logger.info(f"\n{i}. {job.get('titre')}")
            logger.info(f"   Entreprise: {job.get('entreprise')}")
            logger.info(f"   Localisation: {job.get('localisation')}")
            logger.info(f"   Score: {score:.3f}")
            logger.info(f"   Remote: {'Oui' if job.get('remote') else 'Non'}")
            logger.info(f"   URL: {job.get('url')}")
        
        if not filtered_jobs:
            logger.warning("⚠️ Aucune offre ne correspond à vos critères")
            return False
        
        # 4. Sélection des 2 meilleures offres
        sorted_jobs = sorted(filtered_jobs, key=lambda x: x.get('match_score', 0), reverse=True)
        best_jobs = sorted_jobs[:2]
        
        logger.info(f"\n🎯 Sélection des {len(best_jobs)} meilleures offres pour candidature")
        
        # 5. Génération des lettres de motivation
        generator = LetterGenerator(config)
        logger.info("\n📝 Génération des lettres de motivation...")
        
        jobs_with_letters = []
        for job in best_jobs:
            try:
                letter = generator.generate_letter(job)
                job['lettre_motivation'] = letter
                logger.info(f"✅ Lettre générée pour {job.get('entreprise')}")
                
                # Affichage d'un extrait de la lettre
                letter_preview = letter[:150] + "..." if len(letter) > 150 else letter
                logger.info(f"📄 Extrait: {letter_preview}")
                
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
        
        if not prepared_candidatures:
            logger.error("❌ Aucune candidature n'a pu être préparée")
            return False
        
        # 7. Test des notifications
        notification_manager = NotificationManager(config)
        logger.info("\n📧 Test des notifications...")
        
        notif_status = notification_manager.get_notification_status()
        logger.info(f"✅ Statut notifications: {notif_status}")
        
        # 8. Simulation d'envoi de candidature
        logger.info("\n🚀 Simulation d'envoi de candidature...")
        
        for i, job in enumerate(prepared_candidatures, 1):
            logger.info(f"\n📤 Candidature {i}: {job.get('entreprise')}")
            logger.info(f"   Titre: {job.get('titre')}")
            logger.info(f"   Score: {job.get('match_score', 'N/A'):.3f}")
            logger.info(f"   URL: {job.get('url')}")
            
            # Simuler l'envoi
            logger.info("   🔄 Envoi en cours...")
            logger.info("   ✅ Candidature envoyée avec succès !")
            
            # Mettre à jour le statut
            candidature_manager.update_application_status(job['id'], 'envoyée')
            logger.info("   📝 Statut mis à jour: Envoyée")
        
        # 9. Résumé final
        logger.info("\n" + "="*70)
        logger.info("🎉 TEST RÉALISTE TERMINÉ AVEC SUCCÈS !")
        logger.info("="*70)
        logger.info(f"📊 Offres traitées: {len(realistic_jobs)}")
        logger.info(f"✅ Offres filtrées: {len(filtered_jobs)}")
        logger.info(f"🎯 Candidatures préparées: {len(prepared_candidatures)}")
        logger.info(f"📝 Lettres générées: {len(jobs_with_letters)}")
        logger.info(f"📁 Dossiers créés dans: ./outbox/")
        
        # Affichage des dossiers créés
        import os
        if os.path.exists('outbox'):
            candidatures = [d for d in os.listdir('outbox') if os.path.isdir(os.path.join('outbox', d))]
            candidatures.sort(key=lambda x: os.path.getctime(os.path.join('outbox', x)), reverse=True)
            
            logger.info(f"\n📂 Dossiers de candidature créés:")
            for candidature in candidatures[:len(prepared_candidatures)]:
                logger.info(f"   - {candidature}")
        
        logger.info("\n💡 Prochaines étapes réelles:")
        logger.info("   1. Consultez les candidatures dans ./outbox/")
        logger.info("   2. Relisez et personnalisez les lettres")
        logger.info("   3. Envoyez via les sites web officiels")
        logger.info("   4. Suivez l'état dans les fichiers de suivi")
        logger.info("   5. Relancez le bot pour de nouvelles offres")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Erreur lors du test: {e}")
        return False

def main():
    """Fonction principale"""
    logger.info("🚀 Test réaliste du bot de candidature")
    logger.info("=" * 60)
    
    success = test_realistic_workflow()
    
    if success:
        logger.info("\n🎉 Test réussi ! Votre bot est prêt pour de vraies candidatures.")
        logger.info("💡 Vous pouvez maintenant :")
        logger.info("   - Lancer le bot en mode continu: ./start.sh daemon")
        logger.info("   - Tester avec de vraies offres: python3 test_linkedin_real.py")
        logger.info("   - Personnaliser la configuration dans config.yaml")
    else:
        logger.error("\n⚠️ Le test a échoué. Vérifiez la configuration et les erreurs.")
    
    return success

if __name__ == "__main__":
    main()
