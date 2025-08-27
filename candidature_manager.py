"""
Gestionnaire de candidatures pour l'envoi automatique ou la préparation
Gère les deux modes: automatique (risqué) et semi-automatique (sûr)
"""

import os
import logging
import shutil
from datetime import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path
from playwright.sync_api import sync_playwright, Page

logger = logging.getLogger(__name__)

class CandidatureManager:
    """Gestionnaire des candidatures automatiques et semi-automatiques"""
    
    def __init__(self, config):
        """Initialise le gestionnaire de candidatures"""
        self.config = config
        self.profile = config.get_profile()
        self.mode = config.get_generation_mode()
        
        # Dossiers de travail
        self.outbox_dir = Path("outbox")
        self.temp_dir = Path("temp")
        self.cv_dir = Path("cv_letters")
        
        # Création des dossiers
        self._create_directories()
    
    def _create_directories(self):
        """Crée les dossiers nécessaires"""
        for directory in [self.outbox_dir, self.temp_dir, self.cv_dir]:
            directory.mkdir(exist_ok=True)
    
    def send_application(self, job: Dict[str, Any]) -> bool:
        """
        Envoie automatiquement une candidature (mode automatique)
        
        Args:
            job: Offre d'emploi avec lettre générée
            
        Returns:
            bool: True si succès, False sinon
        """
        if self.mode != 'auto':
            logger.warning("Mode automatique non activé")
            return False
        
        try:
            logger.info(f"Envoi automatique pour {job.get('titre', 'Offre inconnue')}")
            
            # Détermination de la méthode d'envoi
            source = job.get('source', '')
            
            if source == 'france_travail':
                return self._send_france_travail(job)
            elif source == 'linkedin':
                return self._send_linkedin(job)
            elif source == 'indeed':
                return self._send_indeed(job)
            else:
                logger.warning(f"Source non supportée pour l'envoi automatique: {source}")
                return False
                
        except Exception as e:
            logger.error(f"Erreur lors de l'envoi automatique: {e}")
            return False
    
    def prepare_application(self, job: Dict[str, Any]) -> bool:
        """
        Prépare une candidature pour envoi manuel (mode semi-automatique)
        
        Args:
            job: Offre d'emploi avec lettre générée
            
        Returns:
            bool: True si succès, False sinon
        """
        try:
            logger.info(f"Préparation de la candidature pour {job.get('titre', 'Offre inconnue')}")
            
            # Création du dossier de candidature
            candidature_dir = self._create_candidature_folder(job)
            
            # Copie des fichiers
            self._copy_application_files(job, candidature_dir)
            
            # Création du fichier de description du poste
            self._create_job_description_file(job, candidature_dir)
            
            # Création du fichier de résumé
            self._create_summary_file(job, candidature_dir)
            
            # Création du fichier de suivi
            self._create_tracking_file(job, candidature_dir)
            
            logger.info(f"Candidature préparée dans: {candidature_dir}")
            return True
            
        except Exception as e:
            logger.error(f"Erreur lors de la préparation: {e}")
            return False
    
    def _create_candidature_folder(self, job: Dict[str, Any]) -> Path:
        """Crée le dossier de candidature"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        job_id = job.get('id', 'unknown')
        company = job.get('entreprise', 'unknown').replace(' ', '_')
        
        folder_name = f"candidature_{company}_{job_id}_{timestamp}"
        candidature_dir = self.outbox_dir / folder_name
        candidature_dir.mkdir(exist_ok=True)
        
        return candidature_dir
    
    def _copy_application_files(self, job: Dict[str, Any], candidature_dir: Path):
        """Copie les fichiers de candidature"""
        # Copie du CV
        cv_path = self.config.get_cv_path()
        if cv_path and os.path.exists(cv_path):
            cv_dest = candidature_dir / f"CV_{self.profile.get('nom', 'candidat')}.pdf"
            shutil.copy2(cv_path, cv_dest)
        
        # Copie de la lettre
        lettre_path = job.get('lettre_path')
        if lettre_path and os.path.exists(lettre_path):
            lettre_dest = candidature_dir / "lettre_motivation.txt"
            shutil.copy2(lettre_path, lettre_dest)
            
            # Génération de la version PDF
            pdf_path = candidature_dir / "lettre_motivation.pdf"
            from nlp.generator import LetterGenerator
            generator = LetterGenerator(self.config)
            generator.generate_pdf_letter(job, str(pdf_path))
    
    def _create_summary_file(self, job: Dict[str, Any], candidature_dir: Path):
        """Crée le fichier de résumé de la candidature"""
        summary_content = f"""
RÉSUMÉ DE LA CANDIDATURE
========================

Offre: {job.get('titre', 'N/A')}
Entreprise: {job.get('entreprise', 'N/A')}
Localisation: {job.get('localisation', 'N/A')}
Type de contrat: {job.get('type_contrat', 'N/A')}
Source: {job.get('source', 'N/A')}
URL: {job.get('url', 'N/A')}
Score de correspondance: {job.get('match_score', 'N/A')}

Date de préparation: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

FICHIERS INCLUS:
- CV_{self.profile.get('nom', 'candidat')}.pdf
- lettre_motivation.txt
- lettre_motivation.pdf

INSTRUCTIONS:
1. Vérifiez le contenu de la lettre de motivation
2. Modifiez si nécessaire
3. Envoyez la candidature via le site web
4. Marquez comme envoyée dans le fichier de suivi

NOTES:
- Cette candidature a été générée automatiquement
- Score de correspondance: {job.get('match_score', 'N/A')}
- Adaptez la lettre selon vos préférences
"""
        
        summary_file = candidature_dir / "RESUME_CANDIDATURE.txt"
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write(summary_content)
    
    def _create_job_description_file(self, job: Dict[str, Any], candidature_dir: Path):
        """Crée le fichier de description du poste"""
        description_content = f"""
DESCRIPTION DU POSTE
====================

Titre: {job.get('titre', 'N/A')}
Entreprise: {job.get('entreprise', 'N/A')}
Localisation: {job.get('localisation', 'N/A')}
Type de contrat: {job.get('type_contrat', 'N/A')}
Salaire: {job.get('salaire', 'N/A')}
Source: {job.get('source', 'N/A')}
URL: {job.get('url', 'N/A')}
Date de publication: {job.get('date_publication', 'N/A')}
Score de correspondance: {job.get('match_score', 'N/A')}

REMOTE: {'Oui' if job.get('remote') else 'Non'}
NIVEAU D'EXPÉRIENCE: {job.get('experience', 'N/A')}

DESCRIPTION DÉTAILLÉE:
{job.get('description', 'Aucune description disponible')}

MOTS-CLÉS DÉTECTÉS:
{', '.join(job.get('keywords', [])) if job.get('keywords') else 'Aucun mot-clé détecté'}

NOTES PERSONNELLES:
- Poste correspondant à votre profil (score: {job.get('match_score', 'N/A')})
- Technologies: {', '.join(self.config.get_preferences().get('stack_technique', []))}
- Localisation souhaitée: {', '.join(self.config.get_preferences().get('localisation', []))}
"""
        
        description_file = candidature_dir / "DESCRIPTION_POSTE.txt"
        with open(description_file, 'w', encoding='utf-8') as f:
            f.write(description_content)

    def _create_tracking_file(self, job: Dict[str, Any], candidature_dir: Path):
        """Crée le fichier de suivi de la candidature"""
        tracking_content = f"""
FICHIER DE SUIVI - CANDIDATURE
===============================

ID Offre: {job.get('id', 'N/A')}
Titre: {job.get('titre', 'N/A')}
Entreprise: {job.get('entreprise', 'N/A')}
Source: {job.get('source', 'N/A')}

STATUT: À ENVOYER
Date de préparation: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Date d'envoi: ___________
Date de réponse: ___________
Type de réponse: ___________

NOTES:
- Modifications apportées: ___________
- Contact établi: ___________
- Suivi effectué: ___________

ACTIONS À EFFECTUER:
□ Vérifier la lettre de motivation
□ Adapter le contenu si nécessaire
□ Envoyer la candidature
□ Suivre la réponse
□ Mettre à jour ce fichier
"""
        
        tracking_file = candidature_dir / "SUIVI_CANDIDATURE.txt"
        with open(tracking_file, 'w', encoding='utf-8') as f:
            f.write(tracking_content)
    
    def _send_france_travail(self, job: Dict[str, Any]) -> bool:
        """Envoie une candidature via l'API France Travail"""
        try:
            # Note: L'API France Travail ne permet pas l'envoi de candidatures
            # Cette méthode est un placeholder pour une future implémentation
            logger.info("Envoi via France Travail non implémenté (API limitée)")
            return False
            
        except Exception as e:
            logger.error(f"Erreur lors de l'envoi France Travail: {e}")
            return False
    
    def _send_linkedin(self, job: Dict[str, Any]) -> bool:
        """Envoie une candidature via LinkedIn (scraping)"""
        try:
            logger.info("Tentative d'envoi automatique via LinkedIn...")
            
            # Note: LinkedIn a des protections anti-bot très strictes
            # Cette méthode est expérimentale et risquée
            return self._attempt_linkedin_application(job)
            
        except Exception as e:
            logger.error(f"Erreur lors de l'envoi LinkedIn: {e}")
            return False
    
    def _send_indeed(self, job: Dict[str, Any]) -> bool:
        """Envoie une candidature via Indeed (scraping)"""
        try:
            logger.info("Tentative d'envoi automatique via Indeed...")
            
            # Note: Indeed a également des protections anti-bot
            # Cette méthode est expérimentale et risquée
            return self._attempt_indeed_application(job)
            
        except Exception as e:
            logger.error(f"Erreur lors de l'envoi Indeed: {e}")
            return False
    
    def _attempt_linkedin_application(self, job: Dict[str, Any]) -> bool:
        """Tente d'envoyer une candidature LinkedIn (expérimental)"""
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=False)  # Visible pour debug
                page = browser.new_page()
                
                # Navigation vers l'offre
                url = job.get('url')
                if not url:
                    logger.error("URL de l'offre manquante")
                    return False
                
                page.goto(url, wait_until='networkidle')
                
                # Recherche du bouton de candidature
                apply_button = page.query_selector('button[aria-label*="Postuler"]')
                if not apply_button:
                    logger.warning("Bouton de candidature non trouvé")
                    return False
                
                # Clic sur le bouton
                apply_button.click()
                page.wait_for_timeout(2000)
                
                # Note: LinkedIn demande généralement une connexion
                # Cette méthode ne peut pas aller plus loin sans authentification
                logger.warning("Candidature LinkedIn interrompue (connexion requise)")
                
                browser.close()
                return False
                
        except Exception as e:
            logger.error(f"Erreur lors de la tentative LinkedIn: {e}")
            return False
    
    def _attempt_indeed_application(self, job: Dict[str, Any]) -> bool:
        """Tente d'envoyer une candidature Indeed (expérimental)"""
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=False)  # Visible pour debug
                page = browser.new_page()
                
                # Navigation vers l'offre
                url = job.get('url')
                if not url:
                    logger.error("URL de l'offre manquante")
                    return False
                
                page.goto(url, wait_until='networkidle')
                
                # Recherche du bouton de candidature
                apply_button = page.query_selector('button[id*="apply"]')
                if not apply_button:
                    apply_button = page.query_selector('a[href*="apply"]')
                
                if not apply_button:
                    logger.warning("Bouton de candidature non trouvé")
                    return False
                
                # Clic sur le bouton
                apply_button.click()
                page.wait_for_timeout(2000)
                
                # Note: Indeed redirige généralement vers le site de l'entreprise
                # Cette méthode ne peut pas aller plus loin
                logger.warning("Candidature Indeed interrompue (redirection externe)")
                
                browser.close()
                return False
                
        except Exception as e:
            logger.error(f"Erreur lors de la tentative Indeed: {e}")
            return False
    
    def get_pending_applications(self) -> List[Dict[str, Any]]:
        """Récupère la liste des candidatures en attente"""
        pending = []
        
        if not self.outbox_dir.exists():
            return pending
        
        for candidature_dir in self.outbox_dir.iterdir():
            if candidature_dir.is_dir():
                tracking_file = candidature_dir / "SUIVI_CANDIDATURE.txt"
                if tracking_file.exists():
                    # Lecture du statut
                    try:
                        with open(tracking_file, 'r', encoding='utf-8') as f:
                            content = f.read()
                            if "STATUT: À ENVOYER" in content:
                                # Extraction des informations
                                info = self._extract_candidature_info(content, candidature_dir)
                                pending.append(info)
                    except Exception as e:
                        logger.warning(f"Erreur lecture fichier de suivi: {e}")
        
        return pending
    
    def _extract_candidature_info(self, content: str, candidature_dir: Path) -> Dict[str, Any]:
        """Extrait les informations d'une candidature depuis le fichier de suivi"""
        info = {
            'directory': str(candidature_dir),
            'status': 'À ENVOYER'
        }
        
        # Extraction des informations de base
        lines = content.split('\n')
        for line in lines:
            if ':' in line and not line.startswith('□'):
                key, value = line.split(':', 1)
                key = key.strip()
                value = value.strip()
                
                if key == 'Titre':
                    info['titre'] = value
                elif key == 'Entreprise':
                    info['entreprise'] = value
                elif key == 'Source':
                    info['source'] = value
                elif key == 'Date de préparation':
                    info['date_preparation'] = value
        
        return info
    
    def mark_as_sent(self, candidature_dir: str) -> bool:
        """Marque une candidature comme envoyée"""
        try:
            tracking_file = Path(candidature_dir) / "SUIVI_CANDIDATURE.txt"
            if not tracking_file.exists():
                return False
            
            # Lecture du contenu
            with open(tracking_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Mise à jour du statut
            content = content.replace("STATUT: À ENVOYER", "STATUT: ENVOYÉE")
            content = content.replace("Date d'envoi: ___________", f"Date d'envoi: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
            # Écriture du contenu mis à jour
            with open(tracking_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            logger.info(f"Candidature marquée comme envoyée: {candidature_dir}")
            return True
            
        except Exception as e:
            logger.error(f"Erreur lors de la mise à jour du statut: {e}")
            return False
