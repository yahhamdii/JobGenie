"""
Module de génération de lettres de motivation
Utilise OpenAI ou Ollama pour générer des lettres personnalisées
"""

import logging
import os
import subprocess
from typing import Dict, Any, Optional
import openai
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

logger = logging.getLogger(__name__)

class LetterGenerator:
    """Générateur de lettres de motivation personnalisées"""
    
    def __init__(self, config):
        """Initialise le générateur avec la configuration"""
        self.config = config
        self.profile = config.get_profile()
        self.llm_provider = config.get('generation.llm_provider', 'openai')
        
        # Configuration OpenAI
        if self.llm_provider == 'openai':
            api_key = config.get('api_keys.openai')
            if api_key:
                openai.api_key = api_key
            else:
                logger.warning("Clé API OpenAI non configurée")
        
        # Configuration Ollama
        self.ollama_model = config.get('generation.ollama_model', 'llama3')
        
        # Styles pour la génération PDF
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Configure les styles personnalisés pour les lettres"""
        # Style pour l'en-tête
        header_style = ParagraphStyle(
            'CustomHeader',
            parent=self.styles['Heading1'],
            fontSize=14,
            spaceAfter=20,
            alignment=1  # Centré
        )
        self.styles.add(header_style)
        
        # Style pour le corps de la lettre
        body_style = ParagraphStyle(
            'CustomBody',
            parent=self.styles['Normal'],
            fontSize=11,
            spaceAfter=12,
            leading=16
        )
        self.styles.add(body_style)
    
    def generate_letter(self, job: Dict[str, Any]) -> str:
        """
        Génère une lettre de motivation personnalisée pour une offre
        
        Args:
            job: Offre d'emploi avec toutes les informations
            
        Returns:
            str: Lettre de motivation générée
        """
        try:
            # Construction du prompt
            prompt = self._build_prompt(job)
            
            # Génération du contenu
            if self.llm_provider == 'openai':
                content = self._generate_with_openai(prompt)
            elif self.llm_provider == 'ollama':
                content = self._generate_with_ollama(prompt)
            else:
                raise ValueError(f"Fournisseur LLM non supporté: {self.llm_provider}")
            
            # Formatage de la lettre
            formatted_letter = self._format_letter(content, job)
            
            logger.info(f"Lettre générée pour {job.get('titre', 'Offre inconnue')}")
            return formatted_letter
            
        except Exception as e:
            logger.error(f"Erreur lors de la génération de la lettre: {e}")
            return self._generate_fallback_letter(job)
    
    def _build_prompt(self, job: Dict[str, Any]) -> str:
        """Construit le prompt optimisé pour la génération de la lettre"""
        profile = self.profile
        preferences = self.config.get_preferences()
        from datetime import datetime
        today = datetime.now().strftime('%d/%m/%Y')
        
        # Calculer le score de correspondance pour personnaliser le prompt
        match_score = job.get('match_score', 0)
        score_percentage = int(match_score * 100)
        
        prompt = f"""
Tu es un expert en rédaction de lettres de motivation en français. Génère une lettre COURTE (≤350 mots), PROFESSIONNELLE, PERSONNALISÉE, suivant STRICTEMENT cette structure:

1) En-tête (haut à gauche):
   - Date du jour: {today}
   - Nom, Email, Téléphone, LinkedIn du candidat

2) Objet: Candidature au poste de {job.get('titre', '')}

3) Accroche d’ouverture: une phrase d’impact montrant la motivation et l’adéquation.

4) Corps:
   - Paragraphe 1: Relier l’expérience/savoir‑faire du candidat aux exigences de la fiche de poste (exemples concrets, mots‑clés techniques exacts demandés).
   - Paragraphe 2: Mettre en avant les savoir‑être (communication, collaboration, autonomie, rigueur, ownership) pertinents vis‑à‑vis des attentes du poste.
   - Paragraphe 3: Pourquoi ce métier et pourquoi cette entreprise (valeurs, produits, impact, stack, secteur), avec 1 à 2 éléments spécifiques à {job.get('entreprise', '')}.

5) Conclusion: disponibilité, ouverture à l’échange, remerciements.

6) Signature: Nom.

Contrainte d’analyse:
- Valide la fiche de poste (déduis besoins essentiels) et aligne le contenu dessus.
- Utilise un ton positif et assuré (score de correspondance estimé: {score_percentage}%).

DONNÉES CANDIDAT:
- Nom: {profile.get('nom', '')}
- Email: {profile.get('email', '')}
- Téléphone: {profile.get('telephone', '')}
- LinkedIn: {profile.get('linkedin', '')}
- Compétences techniques: {', '.join(preferences.get('stack_technique', []))}
- Préférences: {', '.join(preferences.get('localisation', []))}

DONNÉES OFFRE:
- Titre: {job.get('titre', '')}
- Entreprise: {job.get('entreprise', '')}
- Localisation: {job.get('localisation', '')}
- Contrat: {job.get('type_contrat', '')}
- Salaire: {job.get('salaire', 'N/A')}
- Remote: {'Oui' if job.get('remote') else 'Non'}
- Expérience: {job.get('experience', 'N/A')}
- Description (extrait): {job.get('description', '')[:800]}...

Produit UNIQUEMENT la lettre, sans balises ni titres.
"""
        return prompt.strip()
    
    def _generate_with_openai(self, prompt: str) -> str:
        """Génère le contenu avec OpenAI"""
        try:
            from openai import OpenAI
            
            client = OpenAI(api_key=openai.api_key)
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Tu es un expert en rédaction de lettres de motivation professionnelles."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.7
            )
            
            content = response.choices[0].message.content.strip()
            return content
            
        except Exception as e:
            logger.error(f"Erreur OpenAI: {e}")
            raise
    
    def _generate_with_ollama(self, prompt: str) -> str:
        """Génère le contenu avec Ollama"""
        try:
            # Appel d'Ollama via subprocess
            cmd = ['ollama', 'run', self.ollama_model, prompt]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=120  # 2 minutes max
            )
            
            if result.returncode == 0:
                content = result.stdout.strip()
                # Nettoyage du contenu Ollama
                content = self._clean_ollama_output(content)
                return content
            else:
                logger.error(f"Erreur Ollama: {result.stderr}")
                raise RuntimeError(f"Ollama a échoué: {result.stderr}")
                
        except subprocess.TimeoutExpired:
            logger.error("Timeout lors de l'appel Ollama")
            raise RuntimeError("Timeout Ollama")
        except Exception as e:
            logger.error(f"Erreur Ollama: {e}")
            raise
    
    def _clean_ollama_output(self, content: str) -> str:
        """Nettoie la sortie d'Ollama"""
        # Suppression des marqueurs de début/fin
        lines = content.split('\n')
        cleaned_lines = []
        
        for line in lines:
            line = line.strip()
            if line and not line.startswith('```') and not line.startswith('---'):
                cleaned_lines.append(line)
        
        return '\n'.join(cleaned_lines)
    
    def _format_letter(self, content: str, job: Dict[str, Any]) -> str:
        """Formate la lettre avec les informations de contact"""
        profile = self.profile
        
        # En-tête de la lettre
        header = f"""
{profile.get('nom', '')}
{profile.get('email', '')}
{profile.get('telephone', '')}
{profile.get('linkedin', '')}

{job.get('entreprise', '')}
{job.get('localisation', '')}

Objet: Candidature au poste de {job.get('titre', '')}

"""
        
        # Corps de la lettre
        body = content.strip()
        
        # Signature
        signature = f"""

Cordialement,

{profile.get('nom', '')}
"""
        
        return header + body + signature
    
    def _generate_fallback_letter(self, job: Dict[str, Any]) -> str:
        """Génère une lettre de secours en cas d'échec"""
        profile = self.profile
        
        fallback_content = f"""
Madame, Monsieur,

Je me permets de vous présenter ma candidature au poste de {job.get('titre', '')} au sein de votre entreprise {job.get('entreprise', '')}.

Ayant pris connaissance de votre offre d'emploi, je suis convaincu que mon profil correspond parfaitement à vos attentes. Mon expérience et mes compétences me permettent de m'intégrer rapidement dans votre équipe et de contribuer efficacement à vos projets.

Je suis particulièrement attiré par cette opportunité car elle correspond à mes aspirations professionnelles et à mon désir de rejoindre une entreprise dynamique et innovante.

Je reste à votre disposition pour un entretien afin de vous présenter plus en détail ma motivation et mes compétences.

Cordialement,

{profile.get('nom', '')}
"""
        
        return self._format_letter(fallback_content, job)
    
    def generate_pdf_letter(self, job: Dict[str, Any], output_path: str) -> bool:
        """
        Génère une version PDF de la lettre de motivation
        
        Args:
            job: Offre d'emploi
            output_path: Chemin de sortie du PDF
            
        Returns:
            bool: True si succès, False sinon
        """
        try:
            # Génération du contenu
            letter_content = self.generate_letter(job)
            
            # Création du PDF
            doc = SimpleDocTemplate(output_path, pagesize=letter)
            story = []
            
            # En-tête
            header_text = f"{self.profile.get('nom', '')} - {job.get('titre', '')}"
            story.append(Paragraph(header_text, self.styles['CustomHeader']))
            story.append(Spacer(1, 20))
            
            # Contenu de la lettre
            paragraphs = letter_content.split('\n\n')
            for para in paragraphs:
                if para.strip():
                    story.append(Paragraph(para.strip(), self.styles['CustomBody']))
                    story.append(Spacer(1, 12))
            
            # Génération du PDF
            doc.build(story)
            
            logger.info(f"PDF généré: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Erreur lors de la génération du PDF: {e}")
            return False
    
    def get_generation_stats(self) -> Dict[str, Any]:
        """Retourne les statistiques de génération"""
        return {
            'provider': self.llm_provider,
            'ollama_model': self.ollama_model if self.llm_provider == 'ollama' else None,
            'openai_configured': bool(self.config.get('api_keys.openai')),
            'ollama_available': self._check_ollama_availability()
        }
    
    def _check_ollama_availability(self) -> bool:
        """Vérifie si Ollama est disponible"""
        try:
            result = subprocess.run(['ollama', '--version'], capture_output=True, timeout=10)
            return result.returncode == 0
        except:
            return False
