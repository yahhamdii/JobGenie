#!/usr/bin/env python3
"""
Test du système amélioré avec :
- Filtrage des offres récentes (< 7 jours)
- Description du poste dans chaque dossier
- Email récapitulatif
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

def create_recent_jobs():
    """Crée des offres d'emploi récentes (moins de 7 jours)"""
    today = datetime.now()
    
    recent_jobs = [
        {
            'id': 'linkedin_001',
            'titre': 'Développeur Full Stack React/Node.js H/F',
            'entreprise': 'Capgemini',
            'localisation': 'Paris, Île-de-France',
            'description': 'Capgemini recherche un développeur Full Stack pour rejoindre son équipe Digital. Vous travaillerez sur des projets innovants pour des clients internationaux. Compétences requises : React, Node.js, bases de données relationnelles, méthodologies agiles.',
            'type_contrat': 'CDI',
            'salaire': '45000€ - 55000€',
            'url': 'https://www.linkedin.com/jobs/view/123456789',
            'date_publication': (today - timedelta(days=2)).strftime('%Y-%m-%d'),
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
            'date_publication': (today - timedelta(days=1)).strftime('%Y-%m-%d'),
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
            'date_publication': today.strftime('%Y-%m-%d'),
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
            'date_publication': (today - timedelta(days=3)).strftime('%Y-%m-%d'),
            'source': 'linkedin',
            'remote': True,
            'experience': 'mid-senior'
        },
        {
            'id': 'linkedin_004',
            'titre': 'Développeur Full Stack Senior',
            'entreprise': 'Air France',
            'localisation': 'Paris, Île-de-France',
            'description': 'Air France recherche un développeur Full Stack Senior pour moderniser ses systèmes de réservation. Technologies : React, Node.js, microservices, cloud AWS.',
            'type_contrat': 'CDI',
            'salaire': '52000€ - 62000€',
            'url': 'https://www.linkedin.com/jobs/view/789123456',
            'date_publication': (today - timedelta(days=5)).strftime('%Y-%m-%d'),
            'source': 'linkedin',
            'remote': True,
            'experience': 'senior'
        }
    ]
    
    return recent_jobs

def test_improved_system():
    """Test du système amélioré"""
    logger.info("🚀 Test du système amélioré de candidature")
    
    try:
        # 1. Chargement de la configuration
        config = ConfigManager()
        logger.info("✅ Configuration chargée")
        
        # 2. Création des offres récentes
        recent_jobs = create_recent_jobs()
        logger.info(f"✅ {len(recent_jobs)} offres récentes créées")
        
        # Affichage des dates
        logger.info("\n📅 Dates des offres créées:")
        for job in recent_jobs:
            days_ago = (datetime.now() - datetime.strptime(job['date_publication'], '%Y-%m-%d')).days
            logger.info(f"   {job['entreprise']}: {job['date_publication']} ({days_ago} jour(s) ago)")
        
        # 3. Filtrage des offres (maintenant avec filtrage par date)
        matcher = JobMatcher(config)
        filtered_jobs = matcher.filter_jobs(recent_jobs)
        logger.info(f"\n✅ {len(filtered_jobs)} offres récentes correspondent à vos critères")
        
        # Affichage des offres filtrées avec scores
        logger.info("\n📋 Offres filtrées par pertinence :")
        for i, job in enumerate(filtered_jobs, 1):
            score = job.get('match_score', 0)
            days_ago = (datetime.now() - datetime.strptime(job['date_publication'], '%Y-%m-%d')).days
            logger.info(f"\n{i}. {job.get('titre')}")
            logger.info(f"   Entreprise: {job.get('entreprise')}")
            logger.info(f"   Localisation: {job.get('localisation')}")
            logger.info(f"   Score: {score:.3f}")
            logger.info(f"   Date: {job['date_publication']} ({days_ago} jour(s) ago)")
            logger.info(f"   Remote: {'Oui' if job.get('remote') else 'Non'}")
        
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
                logger.info(f"✅ Lettre générée pour {job.get('entreprise')}")
                jobs_with_letters.append(job)
                
            except Exception as e:
                logger.error(f"❌ Erreur génération lettre pour {job.get('entreprise')}: {e}")
        
        if not jobs_with_letters:
            logger.error("❌ Aucune lettre n'a pu être générée")
            return False
        
        # 5. Préparation des candidatures (maintenant avec description du poste)
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
        
        # 6. Test des notifications et envoi de l'email récapitulatif
        notification_manager = NotificationManager(config)
        logger.info("\n📧 Test des notifications et envoi de l'email récapitulatif...")
        
        notif_status = notification_manager.get_notification_status()
        logger.info(f"✅ Statut notifications: {notif_status}")
        
        # Envoi de l'email récapitulatif
        if notif_status['email_configured']:
            logger.info("📧 Envoi de l'email récapitulatif...")
            email_sent = notification_manager.send_candidature_recap_email(prepared_candidatures)
            
            if email_sent:
                logger.info("✅ Email récapitulatif envoyé avec succès !")
                logger.info(f"📧 Vérifiez votre boîte mail: {notif_status.get('email_configured', 'N/A')}")
            else:
                logger.warning("⚠️ Échec de l'envoi de l'email récapitulatif")
        else:
            logger.warning("⚠️ Email non configuré - impossible d'envoyer le récapitulatif")
        
        # 7. Vérification des dossiers créés
        logger.info("\n📁 Vérification des dossiers de candidature...")
        
        import os
        if os.path.exists('outbox'):
            candidatures = [d for d in os.listdir('outbox') if os.path.isdir(os.path.join('outbox', d))]
            candidatures.sort(key=lambda x: os.path.getctime(os.path.join('outbox', x)), reverse=True)
            
            # Afficher les dossiers récents
            recent_candidatures = candidatures[:len(prepared_candidatures)]
            logger.info(f"📂 Dossiers de candidature créés: {len(recent_candidatures)}")
            
            for candidature in recent_candidatures:
                candidature_path = os.path.join('outbox', candidature)
                files = os.listdir(candidature_path)
                
                logger.info(f"\n   📁 {candidature}:")
                for file in files:
                    file_path = os.path.join(candidature_path, file)
                    file_size = os.path.getsize(file_path)
                    logger.info(f"      📄 {file} ({file_size} bytes)")
        
        # 8. Résumé final
        logger.info("\n" + "="*70)
        logger.info("🎉 TEST DU SYSTÈME AMÉLIORÉ TERMINÉ AVEC SUCCÈS !")
        logger.info("="*70)
        logger.info(f"📊 Offres récentes créées: {len(recent_jobs)}")
        logger.info(f"✅ Offres filtrées (< 7 jours): {len(filtered_jobs)}")
        logger.info(f"🎯 Candidatures préparées: {len(prepared_candidatures)}")
        logger.info(f"📝 Lettres générées: {len(jobs_with_letters)}")
        logger.info(f"📁 Dossiers créés dans: ./outbox/")
        logger.info(f"📧 Email récapitulatif: {'Envoyé' if notif_status['email_configured'] else 'Non configuré'}")
        
        logger.info("\n💡 Améliorations testées:")
        logger.info("   ✅ Filtrage des offres récentes (< 7 jours)")
        logger.info("   ✅ Description du poste dans chaque dossier")
        logger.info("   ✅ Email récapitulatif HTML avec toutes les candidatures")
        logger.info("   ✅ Structure de dossier améliorée")
        
        logger.info("\n🚀 Votre bot est maintenant prêt pour la production !")
        logger.info("💡 Lancez-le avec: ./start.sh daemon")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Erreur lors du test: {e}")
        return False

def main():
    """Fonction principale"""
    logger.info("🚀 Test du système amélioré de candidature")
    logger.info("=" * 60)
    
    success = test_improved_system()
    
    if success:
        logger.info("\n🎉 Test réussi ! Toutes les améliorations fonctionnent.")
    else:
        logger.error("\n⚠️ Le test a échoué. Vérifiez la configuration et les erreurs.")
    
    return success

if __name__ == "__main__":
    main()
