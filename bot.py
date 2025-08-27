#!/usr/bin/env python3
"""
Bot de candidature automatique pour sites d'emploi
Script principal qui orchestre la collecte, l'analyse et la candidature
"""

import os
import json
import logging
import schedule
import time
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any

from config_manager import ConfigManager
from sources.france_travail import FranceTravailSource
from sources.linkedin import LinkedInSource
from sources.indeed import IndeedSource
from nlp.matcher import JobMatcher
from nlp.generator import LetterGenerator
from candidature_manager import CandidatureManager
from notification_manager import NotificationManager

# Configuration du logging
handlers: List[logging.Handler] = [logging.StreamHandler()]
try:
    os.makedirs('logs', exist_ok=True)
    handlers.insert(0, logging.FileHandler('logs/bot.log'))
except Exception:
    # Si on ne peut pas écrire dans logs/, on continue avec la sortie console uniquement
    pass

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=handlers
)
logger = logging.getLogger(__name__)

class JobBot:
    def __init__(self):
        """Initialise le bot avec tous les composants nécessaires"""
        self.config = ConfigManager()
        self.sources = self._init_sources()
        self.matcher = JobMatcher(self.config)
        self.generator = LetterGenerator(self.config)
        self.candidature_manager = CandidatureManager(self.config)
        self.notification_manager = NotificationManager(self.config)
        
        # Créer les dossiers nécessaires
        self._create_directories()
        
    def _init_sources(self) -> Dict[str, Any]:
        """Initialise les sources d'offres d'emploi"""
        sources = {}
        
        if self.config.get('sources.france_travail.enabled'):
            sources['france_travail'] = FranceTravailSource(self.config)
            
        if self.config.get('sources.linkedin.enabled'):
            sources['linkedin'] = LinkedInSource(self.config)
            
        if self.config.get('sources.indeed.enabled'):
            sources['indeed'] = IndeedSource(self.config)
            
        return sources
    
    def _create_directories(self):
        """Crée les dossiers nécessaires pour l'application"""
        directories = ['logs', 'outbox', 'temp', 'cv_letters']
        for directory in directories:
            Path(directory).mkdir(exist_ok=True)
    
    def collect_jobs(self) -> List[Dict[str, Any]]:
        """Collecte les offres d'emploi depuis toutes les sources activées"""
        all_jobs = []
        
        for source_name, source in self.sources.items():
            try:
                logger.info(f"Collecte depuis {source_name}...")
                jobs = source.get_jobs()
                all_jobs.extend(jobs)
                logger.info(f"Récupéré {len(jobs)} offres depuis {source_name}")
            except Exception as e:
                logger.error(f"Erreur lors de la collecte depuis {source_name}: {e}")
        
        return all_jobs
    
    def filter_jobs(self, jobs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Filtre les offres selon les préférences utilisateur"""
        logger.info(f"Filtrage de {len(jobs)} offres...")
        filtered_jobs = self.matcher.filter_jobs(jobs)
        logger.info(f"{len(filtered_jobs)} offres correspondent aux critères")
        return filtered_jobs
    
    def generate_letters(self, jobs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Génère les lettres de motivation pour chaque offre filtrée"""
        logger.info("Génération des lettres de motivation...")
        jobs_with_letters = []
        
        for job in jobs:
            try:
                letter = self.generator.generate_letter(job)
                job['lettre_motivation'] = letter
                job['lettre_path'] = self._save_letter(job, letter)
                jobs_with_letters.append(job)
                logger.info(f"Lettre générée pour {job.get('titre', 'Offre inconnue')}")
            except Exception as e:
                logger.error(f"Erreur lors de la génération de la lettre: {e}")
        
        return jobs_with_letters
    
    def _save_letter(self, job: Dict[str, Any], letter: str) -> str:
        """Sauvegarde la lettre de motivation dans un fichier"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        job_id = job.get('id', 'unknown')
        filename = f"cv_letters/lettre_{job_id}_{timestamp}.txt"
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(letter)
        
        return filename
    
    def process_candidatures(self, jobs: List[Dict[str, Any]]):
        """Traite les candidatures selon le mode configuré"""
        mode = self.config.get('generation.mode')
        
        if mode == 'auto':
            self._auto_candidature(jobs)
        else:
            self._semi_auto_candidature(jobs)
    
    def _auto_candidature(self, jobs: List[Dict[str, Any]]):
        """Candidature automatique (risqué)"""
        logger.info("Mode automatique activé - candidatures directes")
        for job in jobs:
            try:
                success = self.candidature_manager.send_application(job)
                if success:
                    logger.info(f"Candidature envoyée automatiquement pour {job.get('titre')}")
                else:
                    logger.warning(f"Échec de l'envoi automatique pour {job.get('titre')}")
            except Exception as e:
                logger.error(f"Erreur lors de l'envoi automatique: {e}")
    
    def _semi_auto_candidature(self, jobs: List[Dict[str, Any]]):
        """Candidature semi-automatique (plus sûr)"""
        logger.info("Mode semi-automatique - préparation des candidatures")
        for job in jobs:
            try:
                self.candidature_manager.prepare_application(job)
                logger.info(f"Candidature préparée pour {job.get('titre')}")
            except Exception as e:
                logger.error(f"Erreur lors de la préparation: {e}")
    
    def run_cycle(self):
        """Exécute un cycle complet de collecte et traitement"""
        logger.info("=== Début du cycle de collecte ===")
        
        try:
            # 1. Collecte des offres
            jobs = self.collect_jobs()
            if not jobs:
                logger.info("Aucune offre trouvée")
                return []
            
            # 2. Filtrage selon les préférences
            filtered_jobs = self.filter_jobs(jobs)
            if not filtered_jobs:
                logger.info("Aucune offre ne correspond aux critères")
                return []
            
            # 3. Génération des lettres
            jobs_with_letters = self.generate_letters(filtered_jobs)
            
            # 4. Traitement des candidatures
            self.process_candidatures(jobs_with_letters)
            
            # 5. Sauvegarde du log
            self._save_cycle_log(jobs_with_letters)
            
            # 6. Notification
            self.notification_manager.send_summary(jobs_with_letters)
            
            logger.info(f"=== Cycle terminé: {len(jobs_with_letters)} candidatures traitées ===")
            return jobs_with_letters
        except Exception as e:
            logger.error(f"Erreur lors du cycle: {e}")
            return []
    
    def _save_cycle_log(self, jobs: List[Dict[str, Any]]):
        """Sauvegarde le log des candidatures du cycle"""
        log_entry = {
            'date': datetime.now().isoformat(),
            'candidatures': [
                {
                    'id': job.get('id'),
                    'titre': job.get('titre'),
                    'entreprise': job.get('entreprise'),
                    'source': job.get('source'),
                    'status': 'préparée' if self.config.get('generation.mode') == 'semi_auto' else 'envoyée',
                    'lettre_path': job.get('lettre_path')
                }
                for job in jobs
            ]
        }
        
        log_file = 'logs/applications.json'
        try:
            if os.path.exists(log_file):
                with open(log_file, 'r', encoding='utf-8') as f:
                    logs = json.load(f)
            else:
                logs = []
            
            logs.append(log_entry)
            
            with open(log_file, 'w', encoding='utf-8') as f:
                json.dump(logs, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde du log: {e}")
    
    def start_scheduler(self):
        """Démarre le planificateur pour exécuter le bot régulièrement"""
        logger.info("Démarrage du planificateur...")
        
        # Exécution immédiate
        self.run_cycle()
        
        # Planification toutes les 6 heures
        schedule.every(6).hours.do(self.run_cycle)
        
        # Planification quotidienne à 9h et 18h
        schedule.every().day.at("09:00").do(self.run_cycle)
        schedule.every().day.at("18:00").do(self.run_cycle)
        
        logger.info("Planificateur démarré - cycles toutes les 6h + 9h et 18h")
        
        while True:
            schedule.run_pending()
            time.sleep(60)  # Vérification toutes les minutes

def main():
    """Point d'entrée principal"""
    try:
        bot = JobBot()
        
        # Mode interactif ou planifié
        import sys
        if len(sys.argv) > 1 and sys.argv[1] == '--once':
            bot.run_cycle()
        else:
            bot.start_scheduler()
            
    except KeyboardInterrupt:
        logger.info("Arrêt du bot...")
    except Exception as e:
        logger.error(f"Erreur fatale: {e}")

if __name__ == "__main__":
    main()
