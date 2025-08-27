"""
Gestionnaire de notifications pour le bot de candidature
Envoie des résumés par email, Slack ou webhook
"""

import logging
import smtplib
import json
import requests
from datetime import datetime
from typing import Dict, Any, List, Optional
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path
import os

logger = logging.getLogger(__name__)

class NotificationManager:
    """Gestionnaire des notifications pour le bot de candidature"""
    
    def __init__(self, config):
        """Initialise le gestionnaire de notifications"""
        self.config = config
        self.notifications_config = config.get('notifications', {})
        
        # Configuration email
        self.email_enabled = self.notifications_config.get('email', False)
        self.smtp_config = self._get_smtp_config()
        
        # Configuration Slack
        self.slack_enabled = self.notifications_config.get('slack', False)
        self.slack_webhook = self.notifications_config.get('webhook', '')
        
        # Configuration webhook personnalisé
        self.webhook_enabled = bool(self.notifications_config.get('webhook', ''))
        self.webhook_url = self.notifications_config.get('webhook', '')
    
    def _get_smtp_config(self) -> Dict[str, str]:
        """Récupère la configuration SMTP depuis les variables d'environnement"""
        # Charger les variables d'environnement depuis le fichier .env
        from dotenv import load_dotenv
        load_dotenv()
        
        return {
            'server': os.getenv('SMTP_SERVER', 'smtp.gmail.com'),
            'port': int(os.getenv('SMTP_PORT', '587')),
            'username': os.getenv('SMTP_USERNAME', ''),
            'password': os.getenv('SMTP_PASSWORD', ''),
            'use_tls': os.getenv('SMTP_USE_TLS', 'true').lower() == 'true'
        }
    
    def send_summary(self, jobs: List[Dict[str, Any]]) -> bool:
        """
        Envoie un résumé des candidatures traitées
        
        Args:
            jobs: Liste des offres avec lettres générées
            
        Returns:
            bool: True si au moins une notification a été envoyée
        """
        if not jobs:
            logger.info("Aucune candidature à notifier")
            return False
        
        success = False
        
        try:
            # Préparation du contenu
            summary_content = self._prepare_summary_content(jobs)
            
            # Envoi des notifications
            if self.email_enabled:
                if self._send_email_notification(summary_content, jobs):
                    success = True
            
            if self.slack_enabled:
                if self._send_slack_notification(summary_content, jobs):
                    success = True
            
            if self.webhook_enabled:
                if self._send_webhook_notification(summary_content, jobs):
                    success = True
            
            if success:
                logger.info("Résumé des candidatures envoyé avec succès")
            else:
                logger.warning("Aucune notification n'a pu être envoyée")
            
            return success
            
        except Exception as e:
            logger.error(f"Erreur lors de l'envoi des notifications: {e}")
            return False
    
    def _prepare_summary_content(self, jobs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Prépare le contenu du résumé des candidatures"""
        # Statistiques
        total_jobs = len(jobs)
        sources = {}
        scores = []
        
        for job in jobs:
            source = job.get('source', 'inconnue')
            sources[source] = sources.get(source, 0) + 1
            
            score = job.get('match_score', 0)
            if score > 0:
                scores.append(score)
        
        # Calcul des moyennes
        avg_score = sum(scores) / len(scores) if scores else 0
        
        # Détail des offres
        job_details = []
        for job in jobs:
            job_details.append({
                'titre': job.get('titre', 'N/A'),
                'entreprise': job.get('entreprise', 'N/A'),
                'localisation': job.get('localisation', 'N/A'),
                'source': job.get('source', 'N/A'),
                'score': round(job.get('match_score', 0), 3),
                'url': job.get('url', 'N/A')
            })
        
        return {
            'timestamp': datetime.now().isoformat(),
            'total_candidatures': total_jobs,
            'sources_distribution': sources,
            'score_moyen': round(avg_score, 3),
            'details': job_details
        }
    
    def _send_email_notification(self, summary: Dict[str, Any], jobs: List[Dict[str, Any]]) -> bool:
        """Envoie une notification par email"""
        try:
            if not self.smtp_config['username'] or not self.smtp_config['password']:
                logger.warning("Configuration SMTP incomplète")
                return False
            
            # Création du message
            msg = MIMEMultipart()
            msg['From'] = self.smtp_config['username']
            msg['To'] = self.config.get_profile().get('email', '')
            msg['Subject'] = f"Résumé des candidatures - {datetime.now().strftime('%Y-%m-%d')}"
            
            # Contenu du message
            email_content = self._format_email_content(summary, jobs)
            msg.attach(MIMEText(email_content, 'plain', 'utf-8'))
            
            # Connexion et envoi
            with smtplib.SMTP(self.smtp_config['server'], self.smtp_config['port']) as server:
                if self.smtp_config['use_tls']:
                    server.starttls()
                
                server.login(self.smtp_config['username'], self.smtp_config['password'])
                server.send_message(msg)
            
            logger.info("Notification email envoyée avec succès")
            return True
            
        except Exception as e:
            logger.error(f"Erreur lors de l'envoi de l'email: {e}")
            return False
    
    def _format_email_content(self, summary: Dict[str, Any], jobs: List[Dict[str, Any]]) -> str:
        """Formate le contenu de l'email"""
        content = f"""
RÉSUMÉ DES CANDIDATURES AUTOMATIQUES
====================================

Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Total des candidatures: {summary['total_candidatures']}
Score moyen: {summary['score_moyen']}

RÉPARTITION PAR SOURCE:
"""
        
        for source, count in summary['sources_distribution'].items():
            content += f"- {source}: {count} offre(s)\n"
        
        content += f"""

DÉTAIL DES OFFRES:
"""
        
        for i, job in enumerate(summary['details'], 1):
            content += f"""
{i}. {job['titre']}
   Entreprise: {job['entreprise']}
   Localisation: {job['localisation']}
   Source: {job['source']}
   Score: {job['score']}
   URL: {job['url']}
"""
        
        content += f"""

STATUT: Les candidatures ont été préparées dans le dossier 'outbox'.
Consultez chaque dossier pour valider et envoyer manuellement.

---
Bot de candidature automatique
"""
        
        return content
    
    def _send_slack_notification(self, summary: Dict[str, Any], jobs: List[Dict[str, Any]]) -> bool:
        """Envoie une notification Slack"""
        try:
            if not self.slack_webhook:
                logger.warning("Webhook Slack non configuré")
                return False
            
            # Préparation du message Slack
            slack_message = self._format_slack_message(summary, jobs)
            
            # Envoi via webhook
            response = requests.post(
                self.slack_webhook,
                json=slack_message,
                timeout=10
            )
            
            if response.status_code == 200:
                logger.info("Notification Slack envoyée avec succès")
                return True
            else:
                logger.error(f"Erreur Slack: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Erreur lors de l'envoi Slack: {e}")
            return False
    
    def _format_slack_message(self, summary: Dict[str, Any], jobs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Formate le message Slack"""
        # Création des blocs Slack
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"🎯 Résumé des candidatures - {datetime.now().strftime('%Y-%m-%d')}"
                }
            },
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*Total:* {summary['total_candidatures']} candidature(s)"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Score moyen:* {summary['score_moyen']}"
                    }
                ]
            }
        ]
        
        # Ajout des sources
        sources_text = "\n".join([f"• {source}: {count}" for source, count in summary['sources_distribution'].items()])
        blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*Répartition par source:*\n{sources_text}"
            }
        })
        
        # Ajout des détails des offres
        for job in summary['details'][:5]:  # Limite à 5 offres pour Slack
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*{job['titre']}*\n{job['entreprise']} - {job['localisation']}\nScore: {job['score']}"
                }
            })
        
        if len(summary['details']) > 5:
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"... et {len(summary['details']) - 5} autre(s) offre(s)"
                }
            })
        
        # Ajout du statut
        blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "✅ *Statut:* Candidatures préparées dans le dossier 'outbox'"
            }
        })
        
        return {
            "text": f"Résumé des candidatures: {summary['total_candidatures']} offre(s) traitée(s)",
            "blocks": blocks
        }
    
    def _send_webhook_notification(self, summary: Dict[str, Any], jobs: List[Dict[str, Any]]) -> bool:
        """Envoie une notification via webhook personnalisé"""
        try:
            if not self.webhook_url:
                logger.warning("URL webhook non configurée")
                return False
            
            # Préparation des données
            webhook_data = {
                'event': 'candidatures_summary',
                'timestamp': summary['timestamp'],
                'summary': summary,
                'bot_version': '1.0.0'
            }
            
            # Envoi
            response = requests.post(
                self.webhook_url,
                json=webhook_data,
                timeout=10
            )
            
            if response.status_code in [200, 201, 202]:
                logger.info("Notification webhook envoyée avec succès")
                return True
            else:
                logger.error(f"Erreur webhook: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Erreur lors de l'envoi webhook: {e}")
            return False
    
    def send_error_notification(self, error_message: str, context: str = "") -> bool:
        """
        Envoie une notification d'erreur
        
        Args:
            error_message: Message d'erreur
            context: Contexte de l'erreur
            
        Returns:
            bool: True si succès
        """
        try:
            error_content = f"""
🚨 ERREUR DU BOT DE CANDIDATURE
===============================

Contexte: {context}
Erreur: {error_message}
Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Le bot a rencontré une erreur et nécessite une intervention.
"""
            
            # Envoi des notifications d'erreur
            success = False
            
            if self.email_enabled:
                if self._send_error_email(error_content, context):
                    success = True
            
            if self.slack_enabled:
                if self._send_error_slack(error_content, context):
                    success = True
            
            return success
            
        except Exception as e:
            logger.error(f"Erreur lors de l'envoi de la notification d'erreur: {e}")
            return False
    
    def _send_error_email(self, error_content: str, context: str) -> bool:
        """Envoie un email d'erreur"""
        try:
            if not self.smtp_config['username'] or not self.smtp_config['password']:
                return False
            
            msg = MIMEMultipart()
            msg['From'] = self.smtp_config['username']
            msg['To'] = self.config.get_profile().get('email', '')
            msg['Subject'] = f"🚨 ERREUR Bot Candidature - {context}"
            
            msg.attach(MIMEText(error_content, 'plain', 'utf-8'))
            
            with smtplib.SMTP(self.smtp_config['server'], self.smtp_config['port']) as server:
                if self.smtp_config['use_tls']:
                    server.starttls()
                
                server.login(self.smtp_config['username'], self.smtp_config['password'])
                server.send_message(msg)
            
            return True
            
        except Exception as e:
            logger.error(f"Erreur lors de l'envoi de l'email d'erreur: {e}")
            return False
    
    def _send_error_slack(self, error_content: str, context: str) -> bool:
        """Envoie une notification Slack d'erreur"""
        try:
            if not self.slack_webhook:
                return False
            
            error_message = {
                "text": f"🚨 Erreur du bot de candidature: {context}",
                "blocks": [
                    {
                        "type": "header",
                        "text": {
                            "type": "plain_text",
                            "text": "🚨 ERREUR DU BOT DE CANDIDATURE"
                        }
                    },
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": f"*Contexte:* {context}\n*Erreur:* {error_content}"
                        }
                    }
                ]
            }
            
            response = requests.post(self.slack_webhook, json=error_message, timeout=10)
            return response.status_code == 200
            
        except Exception as e:
            logger.error(f"Erreur lors de l'envoi Slack d'erreur: {e}")
            return False
    
    def get_notification_status(self) -> Dict[str, Any]:
        """Retourne le statut des notifications"""
        return {
            'email_enabled': self.email_enabled,
            'email_configured': bool(self.smtp_config['username'] and self.smtp_config['password']),
            'slack_enabled': self.slack_enabled,
            'slack_configured': bool(self.slack_webhook),
            'webhook_enabled': self.webhook_enabled,
            'webhook_configured': bool(self.webhook_url)
        }
    
    def send_candidature_recap_email(self, candidatures: List[Dict[str, Any]]) -> bool:
        """Envoie un email récapitulatif avec toutes les candidatures"""
        try:
            if not self.email_enabled or not self.smtp_config['username'] or not self.smtp_config['password']:
                logger.warning("Email non configuré pour l'envoi du récapitulatif")
                return False
            
            # Créer le contenu de l'email
            subject = f"📋 Récapitulatif des candidatures - {len(candidatures)} offres traitées"
            
            # Construire le contenu HTML
            html_content = self._build_recap_html_content(candidatures)
            
            # Envoyer l'email
            return self._send_html_email_notification(html_content, subject)
            
        except Exception as e:
            logger.error(f"Erreur lors de l'envoi du récapitulatif: {e}")
            return False
    
    def _build_recap_html_content(self, candidatures: List[Dict[str, Any]]) -> str:
        """Construit le contenu HTML du récapitulatif"""
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ background-color: #f8f9fa; padding: 20px; border-radius: 8px; }}
                .candidature {{ border: 1px solid #ddd; margin: 10px 0; padding: 15px; border-radius: 5px; }}
                .score {{ font-weight: bold; color: #28a745; }}
                .entreprise {{ color: #007bff; font-weight: bold; }}
                .footer {{ margin-top: 30px; padding: 20px; background-color: #f8f9fa; border-radius: 8px; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🚀 Récapitulatif des Candidatures</h1>
                <p><strong>Date:</strong> {datetime.now().strftime('%d/%m/%Y à %H:%M')}</p>
                <p><strong>Total des candidatures:</strong> {len(candidatures)}</p>
            </div>
        """
        
        # Ajouter chaque candidature
        for i, candidature in enumerate(candidatures, 1):
            score = candidature.get('match_score', 0)
            score_color = '#28a745' if score > 0.7 else '#ffc107' if score > 0.5 else '#dc3545'
            
            html += f"""
            <div class="candidature">
                <h3>{i}. {candidature.get('titre', 'N/A')}</h3>
                <p><span class="entreprise">🏢 {candidature.get('entreprise', 'N/A')}</span></p>
                <p><strong>📍 Localisation:</strong> {candidature.get('localisation', 'N/A')}</p>
                <p><strong>📝 Type:</strong> {candidature.get('type_contrat', 'N/A')}</p>
                <p><strong>💰 Salaire:</strong> {candidature.get('salaire', 'N/A')}</p>
                <p><strong>🎯 Score:</strong> <span class="score" style="color: {score_color}">{score:.3f}</span></p>
                <p><strong>🔗 URL:</strong> <a href="{candidature.get('url', '#')}">{candidature.get('url', 'N/A')}</a></p>
                <p><strong>📅 Date publication:</strong> {candidature.get('date_publication', 'N/A')}</p>
            </div>
            """
        
        html += f"""
            <div class="footer">
                <h3>💡 Prochaines étapes</h3>
                <ol>
                    <li>Consultez les candidatures dans le dossier <code>./outbox/</code></li>
                    <li>Relisez et personnalisez les lettres de motivation</li>
                    <li>Envoyez via les sites web officiels</li>
                    <li>Mettez à jour les fichiers de suivi</li>
                </ol>
                <p><strong>📧 Contact:</strong> hamdi_yahyaoui@yahoo.fr</p>
                <p><em>Cet email a été généré automatiquement par votre bot de candidature</em></p>
            </div>
        </body>
        </html>
        """
        
        return html
    
    def _send_html_email_notification(self, html_content: str, subject: str) -> bool:
        """Envoie un email HTML"""
        try:
            if not self.smtp_config['username'] or not self.smtp_config['password']:
                return False
            
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.smtp_config['username']
            msg['To'] = self.smtp_config['username']  # Envoi à soi-même
            
            # Partie HTML
            html_part = MIMEText(html_content, 'html')
            msg.attach(html_part)
            
            # Connexion et envoi
            with smtplib.SMTP(self.smtp_config['server'], self.smtp_config['port']) as server:
                if self.smtp_config['use_tls']:
                    server.starttls()
                
                server.login(self.smtp_config['username'], self.smtp_config['password'])
                server.send_message(msg)
            
            logger.info(f"Email récapitulatif envoyé avec succès à {self.smtp_config['username']}")
            return True
            
        except Exception as e:
            logger.error(f"Erreur lors de l'envoi de l'email HTML: {e}")
            return False
