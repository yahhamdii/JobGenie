"""
Classe de base pour toutes les sources d'offres d'emploi
Définit l'interface commune pour la collecte d'offres
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class BaseSource(ABC):
    """Classe abstraite de base pour les sources d'offres d'emploi"""
    
    def __init__(self, config):
        """Initialise la source avec la configuration"""
        self.config = config
        self.name = self.__class__.__name__.lower().replace('source', '')
        
    @abstractmethod
    def get_jobs(self, **kwargs) -> List[Dict[str, Any]]:
        """
        Récupère les offres d'emploi depuis la source
        
        Returns:
            List[Dict]: Liste des offres avec structure standardisée
        """
        pass
    
    def standardize_job(self, raw_job: Dict[str, Any]) -> Dict[str, Any]:
        """
        Standardise une offre brute selon le format commun
        
        Args:
            raw_job: Offre brute depuis la source
            
        Returns:
            Dict: Offre standardisée
        """
        return {
            'id': self._extract_id(raw_job),
            'titre': self._extract_title(raw_job),
            'entreprise': self._extract_company(raw_job),
            'localisation': self._extract_location(raw_job),
            'description': self._extract_description(raw_job),
            'type_contrat': self._extract_contract_type(raw_job),
            'salaire': self._extract_salary(raw_job),
            'url': self._extract_url(raw_job),
            'date_publication': self._extract_publication_date(raw_job),
            'source': self.name,
            'raw_data': raw_job  # Données brutes pour traitement ultérieur
        }
    
    def _extract_id(self, raw_job: Dict[str, Any]) -> str:
        """Extrait l'ID de l'offre"""
        return str(raw_job.get('id', raw_job.get('jobId', raw_job.get('reference', ''))))
    
    def _extract_title(self, raw_job: Dict[str, Any]) -> str:
        """Extrait le titre du poste"""
        return raw_job.get('title', raw_job.get('titre', raw_job.get('poste', '')))
    
    def _extract_company(self, raw_job: Dict[str, Any]) -> str:
        """Extrait le nom de l'entreprise"""
        return raw_job.get('company', raw_job.get('entreprise', raw_job.get('societe', '')))
    
    def _extract_location(self, raw_job: Dict[str, Any]) -> str:
        """Extrait la localisation"""
        return raw_job.get('location', raw_job.get('localisation', raw_job.get('lieu', '')))
    
    def _extract_description(self, raw_job: Dict[str, Any]) -> str:
        """Extrait la description du poste"""
        return raw_job.get('description', raw_job.get('contenu', ''))
    
    def _extract_contract_type(self, raw_job: Dict[str, Any]) -> str:
        """Extrait le type de contrat"""
        return raw_job.get('contractType', raw_job.get('type_contrat', raw_job.get('contrat', '')))
    
    def _extract_salary(self, raw_job: Dict[str, Any]) -> Optional[str]:
        """Extrait le salaire"""
        return raw_job.get('salary', raw_job.get('salaire'))
    
    def _extract_url(self, raw_job: Dict[str, Any]) -> str:
        """Extrait l'URL de l'offre"""
        return raw_job.get('url', raw_job.get('lien', ''))
    
    def _extract_publication_date(self, raw_job: Dict[str, Any]) -> str:
        """Extrait la date de publication"""
        return raw_job.get('publicationDate', raw_job.get('date_publication', ''))
    
    def filter_jobs(self, jobs: List[Dict[str, Any]], preferences: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Filtre les offres selon les préférences utilisateur
        
        Args:
            jobs: Liste des offres à filtrer
            preferences: Préférences utilisateur
            
        Returns:
            List[Dict]: Offres filtrées
        """
        filtered_jobs = []
        
        for job in jobs:
            if self._matches_preferences(job, preferences):
                filtered_jobs.append(job)
        
        return filtered_jobs
    
    def _matches_preferences(self, job: Dict[str, Any], preferences: Dict[str, Any]) -> bool:
        """
        Vérifie si une offre correspond aux préférences
        
        Args:
            job: Offre à vérifier
            preferences: Préférences utilisateur
            
        Returns:
            bool: True si l'offre correspond
        """
        # Vérification des mots-clés dans le titre et la description
        keywords = preferences.get('mots_cles', [])
        if keywords:
            job_text = f"{job.get('titre', '')} {job.get('description', '')}".lower()
            if not any(keyword.lower() in job_text for keyword in keywords):
                return False
        
        # Vérification de la localisation
        locations = preferences.get('localisation', [])
        if locations:
            job_location = job.get('localisation', '').lower()
            if not any(loc.lower() in job_location for loc in locations):
                return False
        
        # Vérification du type de contrat
        contract_types = preferences.get('type_contrat', [])
        if contract_types:
            job_contract = job.get('type_contrat', '').lower()
            if not any(ct.lower() in job_contract for ct in contract_types):
                return False
        
        return True
    
    def get_source_info(self) -> Dict[str, Any]:
        """Retourne les informations sur la source"""
        return {
            'name': self.name,
            'enabled': self.config.is_source_enabled(self.name),
            'type': 'api' if hasattr(self, 'api_url') else 'scraping'
        }
