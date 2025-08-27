"""
Source Indeed pour la collecte d'offres d'emploi
Utilise du scraping avec Playwright pour récupérer les offres
"""

import logging
import time
from typing import List, Dict, Any, Optional
from datetime import datetime
from playwright.sync_api import sync_playwright, Page
from .base_source import BaseSource

logger = logging.getLogger(__name__)

class IndeedSource(BaseSource):
    """Source pour récupérer les offres d'emploi depuis Indeed"""
    
    def __init__(self, config):
        super().__init__(config)
        self.base_url = config.get('sources.indeed.base_url')
        self.headless = True  # Mode headless par défaut
        
        # Paramètres de recherche par défaut
        self.default_params = {
            'q': 'développeur',
            'l': 'France',
            'jt': 'permanent',  # Type de contrat
            'remotejob': '1',    # Remote
            'start': 0
        }
    
    def get_jobs(self, **kwargs) -> List[Dict[str, Any]]:
        """
        Récupère les offres d'emploi depuis Indeed
        
        Args:
            **kwargs: Paramètres de recherche supplémentaires
            
        Returns:
            List[Dict]: Liste des offres standardisées
        """
        try:
            # Fusion des paramètres par défaut avec ceux fournis
            search_params = {**self.default_params, **kwargs}
            
            # Récupération des offres via scraping
            raw_jobs = self._scrape_jobs(search_params)
            
            # Standardisation des offres
            standardized_jobs = []
            for raw_job in raw_jobs:
                try:
                    standardized_job = self.standardize_job(raw_job)
                    standardized_jobs.append(standardized_job)
                except Exception as e:
                    logger.warning(f"Erreur lors de la standardisation d'une offre Indeed: {e}")
                    continue
            
            logger.info(f"Récupéré {len(standardized_jobs)} offres depuis Indeed")
            return standardized_jobs
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des offres Indeed: {e}")
            return []
    
    def _scrape_jobs(self, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Effectue le scraping des offres Indeed
        
        Args:
            params: Paramètres de recherche
            
        Returns:
            List[Dict]: Offres brutes scrapées
        """
        jobs = []
        
        try:
            with sync_playwright() as p:
                # Lancement du navigateur
                browser = p.chromium.launch(headless=self.headless)
                page = browser.new_page()
                
                # Configuration de la page
                page.set_viewport_size({"width": 1920, "height": 1080})
                page.set_extra_http_headers({
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                })
                
                # Construction de l'URL de recherche
                search_url = self._build_search_url(params)
                logger.info(f"Navigation vers: {search_url}")
                
                # Navigation vers la page de recherche
                page.goto(search_url, wait_until='networkidle')
                time.sleep(3)  # Attente du chargement
                
                # Scroll pour charger plus d'offres
                self._scroll_page(page)
                
                # Extraction des offres
                jobs = self._extract_jobs_from_page(page)
                
                browser.close()
                
        except Exception as e:
            logger.error(f"Erreur lors du scraping Indeed: {e}")
        
        return jobs
    
    def _build_search_url(self, params: Dict[str, Any]) -> str:
        """Construit l'URL de recherche Indeed"""
        url_parts = [self.base_url]
        
        # Ajout des paramètres
        if params.get('q'):
            url_parts.append(f"?q={params['q']}")
        
        if params.get('l'):
            url_parts.append(f"&l={params['l']}")
        
        if params.get('jt'):
            url_parts.append(f"&jt={params['jt']}")
        
        if params.get('remotejob'):
            url_parts.append(f"&remotejob={params['remotejob']}")
        
        if params.get('start'):
            url_parts.append(f"&start={params['start']}")
        
        return ''.join(url_parts)
    
    def _scroll_page(self, page: Page):
        """Scroll la page pour charger plus d'offres"""
        try:
            # Scroll progressif
            for i in range(3):
                page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                time.sleep(2)
                
                # Vérification s'il y a plus de contenu
                page_height = page.evaluate("document.body.scrollHeight")
                current_position = page.evaluate("window.pageYOffset")
                
                if current_position >= page_height - 1000:
                    break
                    
        except Exception as e:
            logger.warning(f"Erreur lors du scroll: {e}")
    
    def _extract_jobs_from_page(self, page: Page) -> List[Dict[str, Any]]:
        """Extrait les offres d'emploi de la page Indeed"""
        jobs = []
        
        try:
            # Sélecteur pour les cartes d'offres d'emploi Indeed
            job_cards = page.query_selector_all('div[data-jk]')
            
            for card in job_cards:
                try:
                    job_data = self._extract_job_from_card(card)
                    if job_data:
                        jobs.append(job_data)
                except Exception as e:
                    logger.debug(f"Erreur lors de l'extraction d'une offre: {e}")
                    continue
            
            logger.info(f"Extrait {len(jobs)} offres de la page Indeed")
            
        except Exception as e:
            logger.error(f"Erreur lors de l'extraction des offres Indeed: {e}")
        
        return jobs
    
    def _extract_job_from_card(self, card) -> Optional[Dict[str, Any]]:
        """Extrait les données d'une offre depuis une carte Indeed"""
        try:
            # Extraction des données de base
            job_id = card.get_attribute('data-jk')
            if not job_id:
                return None
            
            # Titre du poste
            title_elem = card.query_selector('h2.jobTitle span[title]')
            title = title_elem.get_attribute('title') if title_elem else ''
            
            # Nom de l'entreprise
            company_elem = card.query_selector('span[data-testid="company-name"]')
            company = company_elem.text_content().strip() if company_elem else ''
            
            # Localisation
            location_elem = card.query_selector('div[data-testid="text-location"]')
            location = location_elem.text_content().strip() if location_elem else ''
            
            # Date de publication
            date_elem = card.query_selector('span[data-testid="date"]')
            date = date_elem.text_content().strip() if date_elem else ''
            
            # URL de l'offre
            url_elem = card.query_selector('h2.jobTitle a')
            url = url_elem.get_attribute('href') if url_elem else ''
            if url and not url.startswith('http'):
                url = f"https://fr.indeed.com{url}"
            
            # Description (courte, depuis la carte)
            description_elem = card.query_selector('div[data-testid="job-snippet"]')
            description = description_elem.text_content().strip() if description_elem else ''
            
            # Salaire (si disponible)
            salary_elem = card.query_selector('div[data-testid="attribute_snippet_testid"]')
            salary = salary_elem.text_content().strip() if salary_elem else None
            
            return {
                'id': job_id,
                'title': title,
                'company': company,
                'location': location,
                'description': description,
                'url': url,
                'datePublication': date,
                'salary': salary,
                'source': 'indeed'
            }
            
        except Exception as e:
            logger.debug(f"Erreur lors de l'extraction d'une carte Indeed: {e}")
            return None
    
    def _extract_id(self, raw_job: Dict[str, Any]) -> str:
        """Extrait l'ID de l'offre Indeed"""
        return str(raw_job.get('id', ''))
    
    def _extract_title(self, raw_job: Dict[str, Any]) -> str:
        """Extrait le titre du poste Indeed"""
        return raw_job.get('title', '')
    
    def _extract_company(self, raw_job: Dict[str, Any]) -> str:
        """Extrait le nom de l'entreprise Indeed"""
        return raw_job.get('company', '')
    
    def _extract_location(self, raw_job: Dict[str, Any]) -> str:
        """Extrait la localisation Indeed"""
        return raw_job.get('location', '')
    
    def _extract_description(self, raw_job: Dict[str, Any]) -> str:
        """Extrait la description du poste Indeed"""
        return raw_job.get('description', '')
    
    def _extract_contract_type(self, raw_job: Dict[str, Any]) -> str:
        """Extrait le type de contrat Indeed"""
        # Indeed ne fournit pas toujours cette information
        return raw_job.get('contractType', 'Non spécifié')
    
    def _extract_salary(self, raw_job: Dict[str, Any]) -> Optional[str]:
        """Extrait le salaire Indeed"""
        return raw_job.get('salary')
    
    def _extract_url(self, raw_job: Dict[str, Any]) -> str:
        """Extrait l'URL de l'offre Indeed"""
        return raw_job.get('url', '')
    
    def _extract_publication_date(self, raw_job: Dict[str, Any]) -> str:
        """Extrait la date de publication Indeed"""
        date_str = raw_job.get('datePublication', '')
        if date_str:
            # Indeed utilise des formats comme "Il y a 2 jours", "Aujourd'hui", etc.
            # Pour l'instant, on garde le texte brut
            return date_str
        return ''
    
    def search_by_keywords(self, keywords: List[str]) -> List[Dict[str, Any]]:
        """
        Recherche des offres par mots-clés
        
        Args:
            keywords: Liste des mots-clés
            
        Returns:
            List[Dict]: Offres correspondant aux mots-clés
        """
        if not keywords:
            return self.get_jobs()
        
        all_jobs = []
        for keyword in keywords:
            jobs = self.get_jobs(q=keyword)
            all_jobs.extend(jobs)
        
        # Suppression des doublons
        unique_jobs = {}
        for job in all_jobs:
            unique_jobs[job['id']] = job
        
        return list(unique_jobs.values())
    
    def search_by_location(self, location: str) -> List[Dict[str, Any]]:
        """
        Recherche des offres par localisation
        
        Args:
            location: Localisation recherchée
            
        Returns:
            List[Dict]: Offres dans la localisation
        """
        return self.get_jobs(l=location)
