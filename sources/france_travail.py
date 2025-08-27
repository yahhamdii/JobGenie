"""
Source France Travail (Pôle Emploi) pour la collecte d'offres d'emploi
Utilise l'API officielle de Pôle Emploi
"""

import requests
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from .base_source import BaseSource

logger = logging.getLogger(__name__)

class FranceTravailSource(BaseSource):
    """Source pour récupérer les offres d'emploi depuis France Travail"""
    
    def __init__(self, config):
        super().__init__(config)
        self.api_url = config.get('sources.france_travail.url')
        self.api_key = config.get('api_keys.france_travail')
        
        if not self.api_key:
            logger.warning("Clé API France Travail non configurée")
        
        # Paramètres de recherche par défaut
        self.default_params = {
            'motsCles': 'développeur',
            'range': '0-49',  # Limite à 50 résultats
            'tri': '0',  # Tri par date
            'commune': '',  # Toutes les communes
            'departement': '',
            'region': '',
            'pays': 'FR'
        }
    
    def get_jobs(self, **kwargs) -> List[Dict[str, Any]]:
        """
        Récupère les offres d'emploi depuis l'API France Travail
        
        Args:
            **kwargs: Paramètres de recherche supplémentaires
            
        Returns:
            List[Dict]: Liste des offres standardisées
        """
        try:
            # Fusion des paramètres par défaut avec ceux fournis
            search_params = {**self.default_params, **kwargs}
            
            # Récupération des offres
            raw_jobs = self._fetch_jobs(search_params)
            
            # Standardisation des offres
            standardized_jobs = []
            for raw_job in raw_jobs:
                try:
                    standardized_job = self.standardize_job(raw_job)
                    standardized_jobs.append(standardized_job)
                except Exception as e:
                    logger.warning(f"Erreur lors de la standardisation d'une offre: {e}")
                    continue
            
            logger.info(f"Récupéré {len(standardized_jobs)} offres depuis France Travail")
            return standardized_jobs
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des offres France Travail: {e}")
            return []
    
    def _fetch_jobs(self, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Effectue l'appel API vers France Travail
        
        Args:
            params: Paramètres de recherche
            
        Returns:
            List[Dict]: Offres brutes depuis l'API
        """
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        try:
            response = requests.get(
                self.api_url,
                headers=headers,
                params=params,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get('resultats', [])
            else:
                logger.error(f"Erreur API France Travail: {response.status_code} - {response.text}")
                return []
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Erreur de connexion à l'API France Travail: {e}")
            return []
    
    def _extract_id(self, raw_job: Dict[str, Any]) -> str:
        """Extrait l'ID de l'offre France Travail"""
        return str(raw_job.get('id', raw_job.get('idOffre', '')))
    
    def _extract_title(self, raw_job: Dict[str, Any]) -> str:
        """Extrait le titre du poste France Travail"""
        return raw_job.get('intitule', raw_job.get('title', ''))
    
    def _extract_company(self, raw_job: Dict[str, Any]) -> str:
        """Extrait le nom de l'entreprise France Travail"""
        return raw_job.get('entreprise', {}).get('nom', raw_job.get('entreprise', ''))
    
    def _extract_location(self, raw_job: Dict[str, Any]) -> str:
        """Extrait la localisation France Travail"""
        lieu = raw_job.get('lieuTravail', {})
        if isinstance(lieu, dict):
            return f"{lieu.get('libelle', '')} {lieu.get('commune', '')}".strip()
        return str(lieu)
    
    def _extract_description(self, raw_job: Dict[str, Any]) -> str:
        """Extrait la description du poste France Travail"""
        description = raw_job.get('description', '')
        if not description:
            description = raw_job.get('profilPoste', '')
        return description
    
    def _extract_contract_type(self, raw_job: Dict[str, Any]) -> str:
        """Extrait le type de contrat France Travail"""
        return raw_job.get('typeContrat', raw_job.get('natureContrat', ''))
    
    def _extract_salary(self, raw_job: Dict[str, Any]) -> Optional[str]:
        """Extrait le salaire France Travail"""
        salaire = raw_job.get('salaire', {})
        if isinstance(salaire, dict):
            libelle = salaire.get('libelle', '')
            commentaire = salaire.get('commentaire', '')
            if libelle or commentaire:
                return f"{libelle} {commentaire}".strip()
        return None
    
    def _extract_url(self, raw_job: Dict[str, Any]) -> str:
        """Extrait l'URL de l'offre France Travail"""
        return f"https://candidat.pole-emploi.fr/offres/recherche/detail/{raw_job.get('id', '')}"
    
    def _extract_publication_date(self, raw_job: Dict[str, Any]) -> str:
        """Extrait la date de publication France Travail"""
        date_str = raw_job.get('dateCreation', raw_job.get('datePublication', ''))
        if date_str:
            try:
                # Format attendu: "2024-01-15T10:30:00Z"
                date_obj = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                return date_obj.strftime('%Y-%m-%d')
            except:
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
            jobs = self.get_jobs(motsCles=keyword)
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
        return self.get_jobs(commune=location)
    
    def get_recent_jobs(self, days: int = 7) -> List[Dict[str, Any]]:
        """
        Récupère les offres récentes
        
        Args:
            days: Nombre de jours en arrière
            
        Returns:
            List[Dict]: Offres récentes
        """
        # Note: L'API France Travail ne permet pas de filtrer par date
        # On récupère toutes les offres et on filtre côté client
        all_jobs = self.get_jobs()
        
        if days <= 0:
            return all_jobs
        
        cutoff_date = datetime.now() - timedelta(days=days)
        recent_jobs = []
        
        for job in all_jobs:
            try:
                pub_date = datetime.strptime(job.get('date_publication', ''), '%Y-%m-%d')
                if pub_date >= cutoff_date:
                    recent_jobs.append(job)
            except:
                # Si la date n'est pas parsable, on inclut l'offre
                recent_jobs.append(job)
        
        return recent_jobs
