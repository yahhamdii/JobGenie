# 🔐 API France Travail - Guide d'Accès

## ⚠️ **Important : Accès Restreint**

L'API France Travail n'est **PAS accessible publiquement**. Elle nécessite une inscription et une validation en tant que partenaire.

## 📋 **Étapes pour Obtenir l'Accès**

### 1. **Inscription sur le Portail Partenaires**
- Rendez-vous sur : https://pole-emploi.io/data/
- Cliquez sur "Devenir partenaire"
- Remplissez le formulaire de demande

### 2. **Types de Partenaires Acceptés**
- **Établissements d'enseignement** (écoles, universités)
- **Organismes de formation**
- **Associations d'aide à l'emploi**
- **Entreprises de recrutement agréées**
- **Institutions publiques**

### 3. **Documents Requis**
- Justificatif de l'activité
- Statuts de l'organisation
- Plan d'utilisation des données
- Engagement de respect des conditions

### 4. **Processus de Validation**
- **Délai** : 4 à 8 semaines
- **Validation** par l'équipe France Travail
- **Formation** obligatoire sur l'utilisation

## 🔑 **Une Fois Approuvé**

### **Informations Fournies**
- Compte client et mot de passe
- Clé API (Client ID et Secret)
- Documentation technique complète
- Accès au portail de test

### **Limites d'Utilisation**
- **Quota** : Variable selon le type de partenaire
- **Fréquence** : Maximum 1000 appels/jour
- **Données** : Offres publiques uniquement

## 🚫 **Alternatives Sans Inscription**

### **1. Scraping LinkedIn (Recommandé)**
- ✅ Aucune inscription requise
- ✅ Données riches et à jour
- ✅ Interface stable
- ⚠️ Respecter les conditions d'utilisation

### **2. Scraping Indeed**
- ✅ Aucune inscription requise
- ✅ Large couverture géographique
- ✅ Interface simple
- ⚠️ Respecter les conditions d'utilisation

### **3. Sites d'Emploi Spécialisés**
- Apec.fr (cadres)
- RegionsJob.com
- Welcome to the Jungle
- WTTJ (Welcome to the Jungle)

## 🔧 **Configuration Recommandée**

Pour l'instant, utilisez cette configuration dans `config.yaml` :

```yaml
sources:
  france_travail:
    enabled: false  # Désactivé - nécessite inscription partenaire
    url: "https://api.pole-emploi.io/partenaire/offresdemploi/v2/offres/search"
    note: "Nécessite inscription sur https://pole-emploi.io/data/"
  
  linkedin:
    enabled: true   # Activé - fonctionne immédiatement
    base_url: "https://www.linkedin.com/jobs/search/"
  
  indeed:
    enabled: true   # Activé - fonctionne immédiatement
    base_url: "https://fr.indeed.com/emplois"
```

## 📞 **Contact France Travail**

- **Email** : api@pole-emploi.fr
- **Documentation** : https://pole-emploi.io/data/documentation
- **Support** : Via le portail partenaire

## 💡 **Recommandation**

Pour un usage personnel ou de petite entreprise, **LinkedIn et Indeed** sont plus adaptés car :
- Aucune inscription administrative
- Données suffisantes pour la plupart des besoins
- Mise à jour en temps réel
- Interface stable et fiable

L'API France Travail est principalement destinée aux **gros volumes** et aux **institutions**.
