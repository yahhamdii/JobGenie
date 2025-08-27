"""
Gestionnaire de configuration pour le bot de candidature
Charge et gère le fichier config.yaml
"""

import os
import yaml
from typing import Any, Dict, Optional
from pathlib import Path

class ConfigManager:
    def __init__(self, config_path: str = "config.yaml"):
        """Initialise le gestionnaire de configuration"""
        self.config_path = config_path
        self.config = self._load_config()
        
    def _load_config(self) -> Dict[str, Any]:
        """Charge la configuration depuis le fichier YAML"""
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(f"Fichier de configuration {self.config_path} non trouvé")
        
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            
            # Validation de base
            self._validate_config(config)
            return config
            
        except yaml.YAMLError as e:
            raise ValueError(f"Erreur de syntaxe YAML: {e}")
        except Exception as e:
            raise RuntimeError(f"Erreur lors du chargement de la configuration: {e}")
    
    def _validate_config(self, config: Dict[str, Any]):
        """Valide la configuration de base"""
        required_sections = ['profile', 'preferences', 'sources']
        
        for section in required_sections:
            if section not in config:
                raise ValueError(f"Section '{section}' manquante dans la configuration")
        
        # Validation du profil
        profile = config['profile']
        required_profile_fields = ['nom', 'email', 'cv_path']
        for field in required_profile_fields:
            if not profile.get(field):
                raise ValueError(f"Champ '{field}' manquant dans le profil")
        
        # Validation des sources
        sources = config['sources']
        if not any(sources.get(source, {}).get('enabled', False) for source in sources):
            raise ValueError("Aucune source d'emploi n'est activée")
    
    def get(self, key_path: str, default: Any = None) -> Any:
        """
        Récupère une valeur de configuration par chemin (ex: 'sources.france_travail.enabled')
        """
        keys = key_path.split('.')
        value = self.config
        
        try:
            for key in keys:
                value = value[key]
            return value
        except (KeyError, TypeError):
            return default
    
    def get_profile(self) -> Dict[str, Any]:
        """Récupère le profil utilisateur"""
        return self.config.get('profile', {})
    
    def get_preferences(self) -> Dict[str, Any]:
        """Récupère les préférences utilisateur"""
        return self.config.get('preferences', {})
    
    def get_api_keys(self) -> Dict[str, str]:
        """Récupère les clés API"""
        return self.config.get('api_keys', {})
    
    def get_sources(self) -> Dict[str, Any]:
        """Récupère la configuration des sources"""
        return self.config.get('sources', {})
    
    def is_source_enabled(self, source_name: str) -> bool:
        """Vérifie si une source est activée"""
        return self.config.get(f'sources.{source_name}.enabled', False)
    
    def reload(self):
        """Recharge la configuration depuis le fichier"""
        self.config = self._load_config()
    
    def get_cv_path(self) -> str:
        """Récupère le chemin vers le CV"""
        cv_path = self.config.get('profile', {}).get('cv_path')
        if not cv_path or not os.path.exists(cv_path):
            raise FileNotFoundError(f"CV non trouvé: {cv_path}")
        return cv_path
    
    def get_generation_mode(self) -> str:
        """Récupère le mode de génération (auto/semi_auto)"""
        return self.config.get('generation', {}).get('mode', 'semi_auto')
    
    def get_llm_provider(self) -> str:
        """Récupère le fournisseur LLM configuré"""
        return self.config.get('generation', {}).get('llm_provider', 'openai')
