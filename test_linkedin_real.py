#!/usr/bin/env python3
"""
Test d'une candidature réelle sur LinkedIn
Collecte une vraie offre et tente l'envoi automatique
"""

import logging
import time
from config_manager import ConfigManager
from sources.linkedin import LinkedInSource
from nlp.matcher import JobMatcher
from nlp.generator import LetterGenerator
from candidature_manager import CandidatureManager

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_linkedin_real_candidature():
    """Test d'une candidature réelle sur LinkedIn"""
    logger.info("🚀 Test d'une candidature réelle sur LinkedIn")
    
    try:
        # 1. Chargement de la configuration
        config = ConfigManager()
        logger.info("✅ Configuration chargée")
        
        # 2. Initialisation de la source LinkedIn
        linkedin_source = LinkedInSource(config)
        logger.info("✅ Source LinkedIn initialisée")
        
        # 3. Collecte d'offres réelles
        logger.info("🔍 Collecte d'offres réelles sur LinkedIn...")
        
        # Paramètres de recherche adaptés à votre profil
        search_params = {
            'keywords': 'développeur React PHP',
            'location': 'France',
            'remote': True,
            'experience': 'mid-senior'
        }
        
        logger.info(f"🔍 Recherche avec paramètres: {search_params}")
        
        # Collecte des offres
        jobs = linkedin_source.get_jobs(**search_params)
        logger.info(f"📊 {len(jobs)} offres collectées")
        
        if not jobs:
            logger.warning("⚠️ Aucune offre trouvée. Vérifiez les paramètres de recherche.")
            return False
        
        # 4. Affichage des offres trouvées
        logger.info("\n📋 Offres trouvées:")
        for i, job in enumerate(jobs[:3], 1):  # Afficher les 3 premières
            logger.info(f"\n{i}. {job.get('titre', 'N/A')}")
            logger.info(f"   Entreprise: {job.get('entreprise', 'N/A')}")
            logger.info(f"   Localisation: {job.get('localisation', 'N/A')}")
            logger.info(f"   Type: {job.get('type_contrat', 'N/A')}")
            logger.info(f"   URL: {job.get('url', 'N/A')}")
        
        # 5. Filtrage des offres
        matcher = JobMatcher(config)
        filtered_jobs = matcher.filter_jobs(jobs)
        logger.info(f"\n✅ {len(filtered_jobs)} offres correspondent à vos critères")
        
        if not filtered_jobs:
            logger.warning("⚠️ Aucune offre ne correspond à vos critères")
            return False
        
        # 6. Sélection de la meilleure offre
        best_job = max(filtered_jobs, key=lambda x: x.get('match_score', 0))
        logger.info(f"\n🎯 Meilleure offre sélectionnée:")
        logger.info(f"   Titre: {best_job.get('titre')}")
        logger.info(f"   Score: {best_job.get('match_score', 'N/A')}")
        logger.info(f"   URL: {best_job.get('url')}")
        
        # 7. Génération de la lettre de motivation
        logger.info("\n📝 Génération de la lettre de motivation...")
        generator = LetterGenerator(config)
        
        try:
            letter = generator.generate_letter(best_job)
            best_job['lettre_motivation'] = letter
            logger.info("✅ Lettre de motivation générée")
            
            # Affichage d'un extrait de la lettre
            letter_preview = letter[:200] + "..." if len(letter) > 200 else letter
            logger.info(f"📄 Extrait de la lettre: {letter_preview}")
            
        except Exception as e:
            logger.error(f"❌ Erreur génération lettre: {e}")
            return False
        
        # 8. Préparation de la candidature
        logger.info("\n📁 Préparation de la candidature...")
        candidature_manager = CandidatureManager(config)
        
        try:
            success = candidature_manager.prepare_application(best_job)
            if success:
                logger.info("✅ Candidature préparée")
            else:
                logger.error("❌ Échec préparation candidature")
                return False
        except Exception as e:
            logger.error(f"❌ Erreur préparation: {e}")
            return False
        
        # 9. Tentative d'envoi automatique
        logger.info("\n🚀 Tentative d'envoi automatique...")
        logger.info("⚠️ ATTENTION: L'envoi automatique est expérimental et peut être détecté")
        logger.info("💡 Il est recommandé de vérifier manuellement avant l'envoi")
        
        # Demande de confirmation
        response = input("\n❓ Voulez-vous tenter l'envoi automatique ? (oui/non): ").lower().strip()
        
        if response in ['oui', 'o', 'yes', 'y']:
            logger.info("🔄 Lancement de l'envoi automatique...")
            
            try:
                # Tentative d'envoi automatique
                success = candidature_manager.submit_application_automated(best_job)
                
                if success:
                    logger.info("🎉 Candidature envoyée automatiquement avec succès !")
                    logger.info("📧 Vérifiez votre email pour la confirmation")
                else:
                    logger.warning("⚠️ L'envoi automatique a échoué")
                    logger.info("💡 Utilisez le mode semi-automatique à la place")
                    
            except Exception as e:
                logger.error(f"❌ Erreur lors de l'envoi automatique: {e}")
                logger.info("💡 L'envoi automatique n'est pas encore stable")
        
        else:
            logger.info("✅ Mode semi-automatique activé")
            logger.info("📁 Consultez la candidature dans ./outbox/")
            logger.info("🔗 Envoyez manuellement via: " + best_job.get('url', 'N/A'))
        
        # 10. Résumé final
        logger.info("\n" + "="*60)
        logger.info("🎯 TEST TERMINÉ - RÉSUMÉ")
        logger.info("="*60)
        logger.info(f"📊 Offres collectées: {len(jobs)}")
        logger.info(f"✅ Offres filtrées: {len(filtered_jobs)}")
        logger.info(f"🎯 Meilleure offre: {best_job.get('titre')}")
        logger.info(f"📝 Lettre générée: {'Oui' if 'lettre_motivation' in best_job else 'Non'}")
        logger.info(f"📁 Candidature préparée: Oui")
        
        logger.info("\n💡 Prochaines étapes:")
        logger.info("   1. Vérifiez la candidature dans ./outbox/")
        logger.info("   2. Relisez et modifiez la lettre si nécessaire")
        logger.info("   3. Envoyez via le site web ou utilisez l'envoi automatique")
        logger.info("   4. Suivez l'état de votre candidature")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Erreur lors du test: {e}")
        return False

def main():
    """Fonction principale"""
    logger.info("🚀 Test d'une candidature réelle sur LinkedIn")
    logger.info("⚠️ Ce test va collecter de vraies offres d'emploi")
    
    success = test_linkedin_real_candidature()
    
    if success:
        logger.info("\n🎉 Test réussi ! Votre bot est prêt pour de vraies candidatures.")
    else:
        logger.error("\n⚠️ Le test a échoué. Vérifiez la configuration et les erreurs.")
    
    return success

if __name__ == "__main__":
    main()
