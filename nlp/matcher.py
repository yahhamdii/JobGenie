"""
Module de matching pour filtrer les offres d'emploi selon les préférences utilisateur
Utilise des règles simples et des scores de correspondance
"""

import logging
import re
from typing import List, Dict, Any, Tuple
from difflib import SequenceMatcher

logger = logging.getLogger(__name__)

class JobMatcher:
    """Classe pour filtrer et scorer les offres d'emploi"""
    
    def __init__(self, config):
        """Initialise le matcher avec la configuration utilisateur"""
        self.config = config
        self.preferences = config.get_preferences()
        self.profile = config.get_profile()
        
        # Pondérations pour le scoring
        self.weights = {
            'keywords': 0.3,
            'location': 0.25,
            'contract_type': 0.2,
            'salary': 0.15,
            'company_size': 0.1
        }
    
    def filter_jobs(self, jobs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Filtre les offres selon les préférences utilisateur
        
        Args:
            jobs: Liste des offres à filtrer
            
        Returns:
            List[Dict]: Offres filtrées avec scores
        """
        if not jobs:
            return []
        
        logger.info(f"Filtrage de {len(jobs)} offres...")
        
        # Filtrage par date (offres récentes < 7 jours)
        recent_jobs = []
        for job in jobs:
            if self._is_job_recent(job):
                recent_jobs.append(job)
        
        logger.info(f"Offres récentes (< 7 jours): {len(recent_jobs)}")
        
        # Calcul des scores pour chaque offre récente
        scored_jobs = []
        for job in recent_jobs:
            try:
                score = self._calculate_match_score(job)
                # Seuil minimal de correspondance : 60% (0.6)
                if score >= 0.6:
                    job['match_score'] = score
                    scored_jobs.append(job)
                    logger.info(f"✅ Offre {job.get('entreprise', 'N/A')} retenue avec score {score:.3f}")
                else:
                    logger.info(f"❌ Offre {job.get('entreprise', 'N/A')} rejetée avec score {score:.3f} (< 0.6)")
            except Exception as e:
                logger.warning(f"Erreur lors du scoring d'une offre: {e}")
                continue
        
        # Tri par score décroissant
        scored_jobs.sort(key=lambda x: x.get('match_score', 0), reverse=True)
        
        # Application des filtres stricts
        filtered_jobs = self._apply_strict_filters(scored_jobs)
        
        logger.info(f"Filtrage terminé: {len(filtered_jobs)} offres retenues")
        return filtered_jobs
    
    def _calculate_match_score(self, job: Dict[str, Any]) -> float:
        """
        Calcule un score de correspondance pour une offre
        
        Args:
            job: Offre à évaluer
            
        Returns:
            float: Score entre 0 et 1
        """
        total_score = 0.0
        
        # Score pour les mots-clés
        keyword_score = self._calculate_keyword_score(job)
        total_score += keyword_score * self.weights['keywords']
        
        # Score pour la localisation
        location_score = self._calculate_location_score(job)
        total_score += location_score * self.weights['location']
        
        # Score pour le type de contrat
        contract_score = self._calculate_contract_score(job)
        total_score += contract_score * self.weights['contract_type']
        
        # Score pour le salaire
        salary_score = self._calculate_salary_score(job)
        total_score += salary_score * self.weights['salary']
        
        # Score pour la taille de l'entreprise (si disponible)
        company_score = self._calculate_company_score(job)
        total_score += company_score * self.weights['company_size']
        
        return min(total_score, 1.0)  # Score maximum de 1.0
    
    def _is_job_recent(self, job: Dict[str, Any]) -> bool:
        """Vérifie si l'offre est récente (moins de 7 jours)"""
        from datetime import datetime, timedelta
        
        # Récupérer la date de publication
        pub_date_str = job.get('date_publication')
        if not pub_date_str:
            # Si pas de date, considérer comme récente
            return True
        
        try:
            # Parser la date (format YYYY-MM-DD)
            pub_date = datetime.strptime(pub_date_str, '%Y-%m-%d')
            current_date = datetime.now()
            
            # Calculer la différence
            days_diff = (current_date - pub_date).days
            
            # Retourner True si moins de 7 jours
            return days_diff <= 7
            
        except ValueError:
            # Si erreur de parsing, considérer comme récente
            logger.warning(f"Impossible de parser la date: {pub_date_str}")
            return True
    
    def _calculate_keyword_score(self, job: Dict[str, Any]) -> float:
        """Calcule le score de correspondance des mots-clés"""
        keywords = self.preferences.get('stack_technique', [])
        if not keywords:
            return 0.5  # Score neutre si pas de préférences
        
        job_text = f"{job.get('titre', '')} {job.get('description', '')}".lower()
        
        matches = 0
        for keyword in keywords:
            if keyword.lower() in job_text:
                matches += 1
        
        return matches / len(keywords)
    
    def _calculate_location_score(self, job: Dict[str, Any]) -> float:
        """Calcule le score de correspondance de la localisation"""
        preferred_locations = self.preferences.get('localisation', [])
        if not preferred_locations:
            return 0.5  # Score neutre si pas de préférences
        
        job_location = job.get('localisation', '').lower()
        if not job_location:
            return 0.3  # Score faible si pas de localisation
        
        # Vérification des correspondances exactes
        for location in preferred_locations:
            if location.lower() in job_location:
                return 1.0
        
        # Vérification des correspondances partielles
        for location in preferred_locations:
            if self._fuzzy_match(location.lower(), job_location):
                return 0.8
        
        return 0.2  # Score faible si pas de correspondance
    
    def _calculate_contract_score(self, job: Dict[str, Any]) -> float:
        """Calcule le score de correspondance du type de contrat"""
        preferred_contracts = self.preferences.get('type_contrat', [])
        if not preferred_contracts:
            return 0.5  # Score neutre si pas de préférences
        
        job_contract = job.get('type_contrat', '').lower()
        if not job_contract:
            return 0.3  # Score faible si pas d'information
        
        for contract in preferred_contracts:
            if contract.lower() in job_contract:
                return 1.0
        
        return 0.2  # Score faible si pas de correspondance
    
    def _calculate_salary_score(self, job: Dict[str, Any]) -> float:
        """Calcule le score de correspondance du salaire"""
        min_salary = self.preferences.get('salaire_min', 0)
        if min_salary <= 0:
            return 0.5  # Score neutre si pas de préférence
        
        job_salary = job.get('salaire')
        if not job_salary:
            return 0.3  # Score faible si pas d'information
        
        # Extraction du salaire numérique
        salary_value = self._extract_salary_value(job_salary)
        if salary_value is None:
            return 0.3
        
        if salary_value >= min_salary:
            return 1.0
        elif salary_value >= min_salary * 0.8:
            return 0.7
        else:
            return 0.3
    
    def _calculate_company_score(self, job: Dict[str, Any]) -> float:
        """Calcule le score basé sur la taille de l'entreprise"""
        # Pour l'instant, score neutre
        # Peut être amélioré avec une base de données d'entreprises
        return 0.5
    
    def _extract_salary_value(self, salary_text: str) -> float:
        """Extrait la valeur numérique du salaire"""
        if not salary_text:
            return None
        
        # Recherche de patterns de salaire
        patterns = [
            r'(\d{1,3}(?:\s\d{3})*)\s*€',  # 45 000 €
            r'(\d{1,3}(?:\s\d{3})*)\s*EUR',  # 45 000 EUR
            r'(\d{1,3}(?:\s\d{3})*)\s*k€',  # 45 k€
            r'(\d{1,3}(?:\s\d{3})*)\s*K',  # 45K
        ]
        
        for pattern in patterns:
            match = re.search(pattern, salary_text, re.IGNORECASE)
            if match:
                value_str = match.group(1).replace(' ', '')
                try:
                    value = float(value_str)
                    # Conversion en annuel si nécessaire
                    if 'k' in salary_text.lower():
                        value *= 1000
                    return value
                except ValueError:
                    continue
        
        return None
    
    def _fuzzy_match(self, text1: str, text2: str, threshold: float = 0.8) -> bool:
        """Effectue une correspondance floue entre deux textes"""
        return SequenceMatcher(None, text1, text2).ratio() >= threshold
    
    def _apply_strict_filters(self, scored_jobs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Applique des filtres stricts sur les offres scorées"""
        filtered_jobs = []
        
        for job in scored_jobs:
            # Filtre par score minimum
            if job.get('match_score', 0) < 0.3:
                continue
            
            # Filtre par mots-clés obligatoires
            if not self._has_required_keywords(job):
                continue
            
            # Filtre par localisation si strictement requise
            if not self._meets_location_requirement(job):
                continue
            
            filtered_jobs.append(job)
        
        return filtered_jobs
    
    def _has_required_keywords(self, job: Dict[str, Any]) -> bool:
        """Vérifie si l'offre contient les mots-clés obligatoires"""
        required_keywords = self.preferences.get('mots_cles', [])
        if not required_keywords:
            return True
        
        job_text = f"{job.get('titre', '')} {job.get('description', '')}".lower()
        
        # Au moins un mot-clé obligatoire doit être présent
        for keyword in required_keywords:
            if keyword.lower() in job_text:
                return True
        
        return False
    
    def _meets_location_requirement(self, job: Dict[str, Any]) -> bool:
        """Vérifie si l'offre respecte les exigences de localisation"""
        preferred_locations = self.preferences.get('localisation', [])
        if not preferred_locations:
            return True
        
        # Si "Remote" est dans les préférences, accepter toutes les offres
        if any('remote' in loc.lower() for loc in preferred_locations):
            return True
        
        job_location = job.get('localisation', '').lower()
        if not job_location:
            return True  # Accepter si pas d'information
        
        # Vérifier si la localisation correspond
        for location in preferred_locations:
            if location.lower() in job_location:
                return True
        
        return False
    
    def get_matching_summary(self, jobs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Retourne un résumé des correspondances"""
        if not jobs:
            return {'total': 0, 'average_score': 0, 'distribution': {}}
        
        scores = [job.get('match_score', 0) for job in jobs]
        average_score = sum(scores) / len(scores)
        
        # Distribution des scores
        distribution = {
            'excellent': len([s for s in scores if s >= 0.8]),
            'bon': len([s for s in scores if 0.6 <= s < 0.8]),
            'moyen': len([s for s in scores if 0.4 <= s < 0.6]),
            'faible': len([s for s in scores if s < 0.4])
        }
        
        return {
            'total': len(jobs),
            'average_score': round(average_score, 3),
            'distribution': distribution
        }
