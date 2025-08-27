#!/usr/bin/env python3
"""
Gestionnaire de candidature automatique
Postule automatiquement aux offres avec score >= 60% et envoie des emails de confirmation
"""

import logging
import time
from datetime import datetime
from typing import Dict, Any, List
from config_manager import ConfigManager
from nlp.matcher import JobMatcher
from nlp.generator import LetterGenerator
from candidature_manager import CandidatureManager
from notification_manager import NotificationManager

logger = logging.getLogger(__name__)

class AutoCandidatureManager:
    """Gestionnaire de candidature automatique intelligente"""
    
    def __init__(self, config: ConfigManager):
        """Initialise le gestionnaire de candidature automatique"""
        self.config = config
        self.profile = config.get_profile()
        self.preferences = config.get_preferences()
        
        # Composants
        self.matcher = JobMatcher(config)
        self.generator = LetterGenerator(config)
        self.candidature_manager = CandidatureManager(config)
        self.notification_manager = NotificationManager(config)
        
        # Configuration
        self.min_score = 0.6  # Score minimum de 60%
        self.max_candidatures_per_cycle = 10  # Limite de candidatures par cycle
        
        logger.info(f"🚀 AutoCandidatureManager initialisé - Score minimum: {self.min_score*100}%")
    
    def process_jobs_automatically(self, jobs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Traite automatiquement les offres et postule aux meilleures correspondances
        
        Args:
            jobs: Liste des offres d'emploi
            
        Returns:
            Dict: Résumé du traitement
        """
        logger.info(f"🚀 Début du traitement automatique de {len(jobs)} offres")
        
        results = {
            'total_jobs': len(jobs),
            'filtered_jobs': 0,
            'candidatures_sent': 0,
            'emails_sent': 0,
            'errors': [],
            'candidatures_details': []
        }
        
        try:
            # 1. Filtrage des offres avec score minimum
            logger.info(f"🔍 Filtrage des offres avec score minimum de {self.min_score*100}%")
            filtered_jobs = self._filter_high_score_jobs(jobs)
            results['filtered_jobs'] = len(filtered_jobs)
            
            if not filtered_jobs:
                logger.info("✅ Aucune offre ne correspond au score minimum requis")
                return results
            
            # 2. Tri par score décroissant
            filtered_jobs.sort(key=lambda x: x.get('match_score', 0), reverse=True)
            
            # 3. Limitation du nombre de candidatures
            if len(filtered_jobs) > self.max_candidatures_per_cycle:
                logger.info(f"⚠️ Limitation à {self.max_candidatures_per_cycle} candidatures par cycle")
                filtered_jobs = filtered_jobs[:self.max_candidatures_per_cycle]
            
            # 4. Traitement de chaque offre
            for i, job in enumerate(filtered_jobs, 1):
                try:
                    logger.info(f"\n📋 Traitement de l'offre {i}/{len(filtered_jobs)}: {job.get('titre')}")
                    
                    # Génération de la lettre optimisée
                    letter = self._generate_optimized_letter(job)
                    job['lettre_motivation'] = letter
                    
                    # Préparation de la candidature
                    candidature_success = self.candidature_manager.prepare_application(job)
                    
                    if candidature_success:
                        # Tentative de candidature automatique
                        application_success = self._submit_application_automated(job)
                        
                        if application_success:
                            results['candidatures_sent'] += 1
                            logger.info(f"✅ Candidature envoyée avec succès pour {job.get('entreprise')}")
                            
                            # Envoi de l'email de confirmation
                            email_success = self._send_confirmation_email(job)
                            if email_success:
                                results['emails_sent'] += 1
                                logger.info(f"📧 Email de confirmation envoyé")
                            
                            # Détails de la candidature
                            candidature_detail = {
                                'entreprise': job.get('entreprise'),
                                'titre': job.get('titre'),
                                'score': job.get('match_score'),
                                'url': job.get('url'),
                                'date_envoi': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                                'email_confirmation': email_success
                            }
                            results['candidatures_details'].append(candidature_detail)
                            
                        else:
                            logger.warning(f"⚠️ Échec de l'envoi automatique pour {job.get('entreprise')}")
                            results['errors'].append(f"Échec envoi: {job.get('entreprise')}")
                    
                    else:
                        logger.error(f"❌ Échec de la préparation pour {job.get('entreprise')}")
                        results['errors'].append(f"Échec préparation: {job.get('entreprise')}")
                    
                    # Pause entre les candidatures pour éviter la détection
                    if i < len(filtered_jobs):
                        logger.info("⏳ Pause de 5 secondes entre les candidatures...")
                        time.sleep(5)
                
                except Exception as e:
                    error_msg = f"Erreur lors du traitement de {job.get('entreprise', 'N/A')}: {e}"
                    logger.error(error_msg)
                    results['errors'].append(error_msg)
                    continue
            
            # 5. Résumé final
            logger.info(f"\n🎯 Traitement automatique terminé:")
            logger.info(f"   📊 Offres traitées: {results['total_jobs']}")
            logger.info(f"   ✅ Offres filtrées (≥{self.min_score*100}%): {results['filtered_jobs']}")
            logger.info(f"   🚀 Candidatures envoyées: {results['candidatures_sent']}")
            logger.info(f"   📧 Emails de confirmation: {results['emails_sent']}")
            
            if results['errors']:
                logger.warning(f"   ⚠️ Erreurs: {len(results['errors'])}")
            
            return results
            
        except Exception as e:
            error_msg = f"Erreur lors du traitement automatique: {e}"
            logger.error(error_msg)
            results['errors'].append(error_msg)
            return results
    
    def _filter_high_score_jobs(self, jobs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Filtre les offres avec un score minimum"""
        high_score_jobs = []
        
        for job in jobs:
            score = job.get('match_score', 0)
            if score >= self.min_score:
                high_score_jobs.append(job)
                logger.info(f"✅ {job.get('entreprise', 'N/A')}: score {score:.3f} ≥ {self.min_score}")
            else:
                logger.info(f"❌ {job.get('entreprise', 'N/A')}: score {score:.3f} < {self.min_score}")
        
        return high_score_jobs
    
    def _generate_optimized_letter(self, job: Dict[str, Any]) -> str:
        """Génère une lettre de motivation optimisée pour la candidature"""
        try:
            letter = self.generator.generate_letter(job)
            logger.info(f"📝 Lettre optimisée générée pour {job.get('entreprise')}")
            return letter
        except Exception as e:
            logger.error(f"❌ Erreur génération lettre: {e}")
            return self.generator._generate_fallback_letter(job)
    
    def _submit_application_automated(self, job: Dict[str, Any]) -> bool:
        """Tente l'envoi automatique de la candidature"""
        try:
            # Utiliser le gestionnaire de candidature existant
            success = self.candidature_manager.submit_application_automated(job)
            
            if success:
                logger.info(f"✅ Candidature automatique réussie pour {job.get('entreprise')}")
            else:
                logger.warning(f"⚠️ Candidature automatique échouée pour {job.get('entreprise')}")
            
            return success
            
        except Exception as e:
            logger.error(f"❌ Erreur lors de la candidature automatique: {e}")
            return False
    
    def _send_confirmation_email(self, job: Dict[str, Any]) -> bool:
        """Envoie un email de confirmation après candidature"""
        try:
            # Créer le contenu de l'email
            subject = f"✅ Candidature envoyée - {job.get('entreprise')}"
            
            # Construire le contenu HTML
            html_content = self._build_confirmation_email_content(job)
            
            # Envoyer l'email
            success = self.notification_manager._send_html_email_notification(html_content, subject)
            
            if success:
                logger.info(f"📧 Email de confirmation envoyé pour {job.get('entreprise')}")
            else:
                logger.warning(f"⚠️ Échec envoi email de confirmation pour {job.get('entreprise')}")
            
            return success
            
        except Exception as e:
            logger.error(f"❌ Erreur lors de l'envoi de l'email de confirmation: {e}")
            return False
    
    def _build_confirmation_email_content(self, job: Dict[str, Any]) -> str:
        """Construit le contenu HTML de l'email de confirmation"""
        score_percentage = int(job.get('match_score', 0) * 100)
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ background-color: #28a745; color: white; padding: 20px; border-radius: 8px; text-align: center; }}
                .content {{ margin: 20px 0; padding: 20px; border: 1px solid #ddd; border-radius: 5px; }}
                .score {{ font-weight: bold; color: #28a745; }}
                .footer {{ margin-top: 30px; padding: 20px; background-color: #f8f9fa; border-radius: 8px; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>✅ Candidature Envoyée avec Succès !</h1>
                <p>Votre candidature a été traitée automatiquement</p>
            </div>
            
            <div class="content">
                <h2>🎯 Détails de la candidature</h2>
                <p><strong>Entreprise:</strong> {job.get('entreprise', 'N/A')}</p>
                <p><strong>Poste:</strong> {job.get('titre', 'N/A')}</p>
                <p><strong>Localisation:</strong> {job.get('localisation', 'N/A')}</p>
                <p><strong>Type de contrat:</strong> {job.get('type_contrat', 'N/A')}</p>
                <p><strong>Salaire:</strong> {job.get('salaire', 'N/A')}</p>
                <p><strong>Score de correspondance:</strong> <span class="score">{score_percentage}%</span></p>
                <p><strong>URL de l'offre:</strong> <a href="{job.get('url', '#')}">{job.get('url', 'N/A')}</a></p>
                <p><strong>Date d'envoi:</strong> {datetime.now().strftime('%d/%m/%Y à %H:%M')}</p>
            </div>
            
            <div class="content">
                <h2>📝 Lettre de motivation générée</h2>
                <p>Une lettre de motivation personnalisée a été générée automatiquement avec GPT, optimisée pour ce poste spécifique.</p>
                <p>Vous pouvez la consulter dans le dossier de candidature créé dans <code>./outbox/</code></p>
            </div>
            
            <div class="footer">
                <h3>💡 Prochaines étapes</h3>
                <ol>
                    <li>Consultez le dossier de candidature dans <code>./outbox/</code></li>
                    <li>Relisez et personnalisez la lettre si nécessaire</li>
                    <li>Suivez l'état de votre candidature</li>
                    <li>Préparez-vous pour un éventuel entretien</li>
                </ol>
                <p><strong>📧 Contact:</strong> {self.profile.get('email', 'N/A')}</p>
                <p><em>Cet email a été généré automatiquement par votre bot de candidature</em></p>
            </div>
        </body>
        </html>
        """
        
        return html_content
    
    def get_auto_candidature_status(self) -> Dict[str, Any]:
        """Retourne le statut du système de candidature automatique"""
        return {
            'min_score': self.min_score,
            'min_score_percentage': int(self.min_score * 100),
            'max_candidatures_per_cycle': self.max_candidatures_per_cycle,
            'email_configured': self.notification_manager.get_notification_status()['email_configured'],
            'auto_submission_available': True  # Toujours disponible
        }
