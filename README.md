# 🤖 Bot de Candidature Automatique

Un bot intelligent qui automatise vos candidatures sur les sites d'emploi en générant des lettres de motivation personnalisées et en gérant le processus de candidature.

## ✨ Fonctionnalités

- **Collecte automatique** d'offres d'emploi depuis multiple sources
- **Génération intelligente** de lettres de motivation personnalisées
- **Filtrage intelligent** selon vos préférences et compétences
- **Mode semi-automatique** pour garder le contrôle humain
- **Suivi complet** de vos candidatures
- **Notifications** par email, Slack ou webhook

## 🎯 Sources d'emploi supportées

- **France Travail (Pôle Emploi)** - Via API officielle
- **LinkedIn** - Via scraping intelligent
- **Indeed** - Via scraping intelligent
- **Extensible** - Ajout facile de nouvelles sources

## 🏗️ Architecture

```
emploi_app/
├── bot.py                 # Script principal
├── config.yaml           # Configuration utilisateur
├── config_manager.py     # Gestionnaire de configuration
├── sources/              # Sources d'offres d'emploi
│   ├── base_source.py    # Classe de base
│   ├── france_travail.py # Source France Travail
│   ├── linkedin.py       # Source LinkedIn
│   └── indeed.py         # Source Indeed
├── nlp/                  # Traitement du langage naturel
│   ├── matcher.py        # Filtrage et scoring
│   └── generator.py      # Génération de lettres
├── candidature_manager.py # Gestion des candidatures
├── notification_manager.py # Notifications
├── requirements.txt      # Dépendances Python
└── README.md            # Documentation
```

## 🚀 Installation

### Prérequis

- Python 3.8+
- CV au format PDF
- Clés API (optionnel)

### 1. Clonage et installation

```bash
git clone <repository>
cd emploi_app
pip install -r requirements.txt
```

### 2. Configuration

1. **Copiez et modifiez `config.yaml`** :
```yaml
profile:
  nom: "Votre Nom"
  email: "votre.email@example.com"
  telephone: "+33 6 12 34 56 78"
  linkedin: "https://linkedin.com/in/votre-profil"
  cv_path: "./cv.pdf"  # Chemin vers votre CV

preferences:
  stack_technique: ["React", "Node.js", "Python", "Fullstack"]
  localisation: ["Île-de-France", "Remote", "Télétravail"]
  type_contrat: ["CDI", "Freelance", "CDD"]
  salaire_min: 45000
  mots_cles: ["développeur", "ingénieur", "architecte"]

api_keys:
  france_travail: "VOTRE_TOKEN_API_FRANCE_TRAVAIL"
  openai: "VOTRE_CLE_API_OPENAI"
```

2. **Placez votre CV** dans le dossier racine

3. **Variables d'environnement** (optionnel) :
```bash
export SMTP_SERVER=smtp.gmail.com
export SMTP_PORT=587
export SMTP_USERNAME=votre.email@gmail.com
export SMTP_PASSWORD=votre_mot_de_passe_app
```

### 3. Installation de Playwright

```bash
playwright install
```

## 📖 Utilisation

### Mode interactif (une seule fois)

```bash
python bot.py --once
```

### Mode planifié (recommandé)

```bash
python bot.py
```

Le bot s'exécute automatiquement :
- Toutes les 6 heures
- À 9h00 et 18h00 chaque jour
- Immédiatement au démarrage

## ⚙️ Configuration avancée

### Mode de génération

- **`semi_auto`** (recommandé) : Prépare les candidatures, vous validez et envoyez
- **`auto`** (expérimental) : Envoi automatique complet (risqué)

### Fournisseur LLM

- **`openai`** : Utilise GPT-3.5-turbo (nécessite une clé API)
- **`ollama`** : Utilise Ollama en local (gratuit, plus lent)

### Sources

Activez/désactivez les sources selon vos besoins dans `config.yaml`.

## 🔄 Flux de travail

1. **Collecte** : Le bot récupère les offres depuis toutes les sources activées
2. **Filtrage** : Application de vos critères et scoring intelligent
3. **Génération** : Création de lettres de motivation personnalisées
4. **Préparation** : Organisation des candidatures dans le dossier `outbox/`
5. **Validation** : Vous vérifiez et modifiez les lettres si nécessaire
6. **Envoi** : Candidature manuelle via les sites web
7. **Suivi** : Mise à jour du statut dans les fichiers de suivi

## 📁 Structure des dossiers

```
emploi_app/
├── outbox/               # Candidatures préparées
│   └── candidature_entreprise_id_timestamp/
│       ├── CV_nom.pdf
│       ├── lettre_motivation.txt
│       ├── lettre_motivation.pdf
│       ├── RESUME_CANDIDATURE.txt
│       └── SUIVI_CANDIDATURE.txt
├── cv_letters/          # Lettres générées
├── logs/                # Logs et historique
└── temp/                # Fichiers temporaires
```

## 📊 Suivi des candidatures

Chaque candidature génère un fichier de suivi que vous pouvez modifier :

```
STATUT: À ENVOYER
Date de préparation: 2024-01-15 14:30:00
Date d'envoi: ___________
Date de réponse: ___________
Type de réponse: ___________

ACTIONS À EFFECTUER:
□ Vérifier la lettre de motivation
□ Adapter le contenu si nécessaire
□ Envoyer la candidature
□ Suivre la réponse
□ Mettre à jour ce fichier
```

## 🔧 Personnalisation

### Ajouter une nouvelle source

1. Créez une classe héritant de `BaseSource`
2. Implémentez la méthode `get_jobs()`
3. Ajoutez la source dans `config.yaml`
4. Intégrez-la dans `bot.py`

### Modifier les critères de filtrage

Ajustez les pondérations dans `nlp/matcher.py` :

```python
self.weights = {
    'keywords': 0.3,      # Mots-clés techniques
    'location': 0.25,     # Localisation
    'contract_type': 0.2, # Type de contrat
    'salary': 0.15,       # Salaire
    'company_size': 0.1   # Taille entreprise
}
```

## 🚨 Sécurité et bonnes pratiques

### Mode automatique (dangereux)

- **Risque de blocage** par les sites d'emploi
- **Violation potentielle** des conditions d'utilisation
- **Détection anti-bot** possible

### Mode semi-automatique (recommandé)

- **Contrôle humain** sur chaque candidature
- **Personnalisation** des lettres avant envoi
- **Respect** des conditions d'utilisation
- **Suivi** manuel des réponses

## 📝 Exemples d'utilisation

### Recherche par mots-clés spécifiques

```python
from sources.france_travail import FranceTravailSource

source = FranceTravailSource(config)
jobs = source.search_by_keywords(["React", "Node.js", "Fullstack"])
```

### Génération manuelle de lettre

```python
from nlp.generator import LetterGenerator

generator = LetterGenerator(config)
letter = generator.generate_letter(job_data)
```

### Vérification du statut

```python
from candidature_manager import CandidatureManager

manager = CandidatureManager(config)
pending = manager.get_pending_applications()
```

## 🐛 Dépannage

### Erreurs courantes

1. **Module not found** : Vérifiez l'installation des dépendances
2. **Clé API manquante** : Configurez vos clés dans `config.yaml`
3. **CV non trouvé** : Vérifiez le chemin dans `config.yaml`
4. **Erreur Playwright** : Exécutez `playwright install`

### Logs

Les logs sont disponibles dans :
- `logs/bot.log` : Log principal du bot
- `logs/applications.json` : Historique des candidatures

### Mode debug

Activez les logs détaillés en modifiant le niveau dans `bot.py` :

```python
logging.basicConfig(level=logging.DEBUG)
```

## 🤝 Contribution

1. Fork le projet
2. Créez une branche feature (`git checkout -b feature/AmazingFeature`)
3. Committez vos changements (`git commit -m 'Add AmazingFeature'`)
4. Push vers la branche (`git push origin feature/AmazingFeature`)
5. Ouvrez une Pull Request

## 📄 Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

## ⚠️ Avertissements

- **Utilisez à vos risques** - L'automatisation peut violer les conditions d'utilisation
- **Respectez les sites** - Ne surchargez pas les serveurs
- **Vérifiez les lettres** - Toujours relire avant envoi
- **Respectez la loi** - Vérifiez la conformité avec la législation locale

## 🆘 Support

Pour toute question ou problème :
1. Consultez les logs dans `logs/`
2. Vérifiez la configuration dans `config.yaml`
3. Ouvrez une issue sur GitHub

---

**Bonnes candidatures ! 🚀**
