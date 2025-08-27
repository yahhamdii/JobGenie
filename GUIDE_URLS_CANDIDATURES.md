# 🚀 Guide d'Utilisation des URLs et Candidatures

## 🔍 **Comprendre les URLs dans vos candidatures**

### **Types d'URLs disponibles :**

#### **1. URLs de recherche (✅ Fonctionnent)**
Ces URLs mènent à des pages de recherche avec plusieurs offres d'emploi correspondant à vos critères.

**Exemples :**
- **LinkedIn React Paris** : `https://www.linkedin.com/jobs/search/?keywords=développeur%20react&location=Paris&f_WT=2`
- **Indeed PHP Symfony Paris** : `https://fr.indeed.com/emplois?q=développeur%20php%20symfony&l=Paris&jt=permanent`
- **LinkedIn Backend Paris** : `https://www.linkedin.com/jobs/search/?keywords=ingénieur%20backend&location=Paris&f_WT=2`

#### **2. URLs fictives (❌ Ne fonctionnent pas)**
Ces URLs étaient utilisées pour la démonstration et ne mènent nulle part.

**Exemples :**
- `https://www.linkedin.com/jobs/view/789123456`
- `https://fr.indeed.com/viewjob?jk=abcdef123`

## 📋 **Comment utiliser vos candidatures préparées :**

### **Étape 1 : Consulter le dossier de candidature**
Chaque candidature est dans un dossier `./outbox/candidature_[Entreprise]_[ID]_[Timestamp]/`

### **Étape 2 : Lire la description du poste**
Ouvrez `DESCRIPTION_POSTE.txt` pour voir :
- Titre du poste
- Entreprise et localisation
- Salaire et type de contrat
- Score de correspondance
- **URL de recherche** ← C'est votre lien principal !

### **Étape 3 : Utiliser l'URL de recherche**
1. **Copiez l'URL** depuis `DESCRIPTION_POSTE.txt`
2. **Collez-la dans votre navigateur**
3. **Vous arrivez sur une page de recherche** avec plusieurs offres
4. **Parcourez les offres** et sélectionnez celles qui vous intéressent

### **Étape 4 : Postuler**
1. **Cliquez sur une offre** qui vous plaît
2. **Lisez la description complète**
3. **Utilisez votre CV et lettre** préparés dans le dossier
4. **Postulez via le site**

## 🎯 **Exemple concret :**

### **Candidature Capgemini :**
- **Dossier** : `./outbox/candidature_Capgemini_linkedin_real_001_20250826_233635/`
- **URL de recherche** : `https://www.linkedin.com/jobs/search/?keywords=développeur%20react&location=Paris&f_WT=2`
- **Action** : Cliquez sur l'URL → Page de recherche LinkedIn → Parcourez les offres React à Paris

### **Candidature Digital Solutions :**
- **Dossier** : `./outbox/candidature_Digital_Solutions_indeed_real_001_20250826_233635/`
- **URL de recherche** : `https://fr.indeed.com/emplois?q=développeur%20php%20symfony&l=Paris&jt=permanent`
- **Action** : Cliquez sur l'URL → Page de recherche Indeed → Parcourez les offres PHP/Symfony à Paris

## 💡 **Conseils d'utilisation :**

### **1. Pour de vraies candidatures :**
- Utilisez le mode scraping : `python3 test_linkedin_real.py`
- Le bot collectera de vraies offres avec de vrais IDs
- URLs directes vers les postes spécifiques

### **2. Pour la recherche manuelle :**
- Utilisez les URLs de recherche fournies
- Parcourez les offres disponibles
- Sélectionnez celles qui correspondent à votre profil

### **3. Pour optimiser vos recherches :**
- Modifiez les mots-clés dans les URLs
- Changez la localisation selon vos préférences
- Ajoutez des filtres (remote, expérience, etc.)

## 🔧 **Modification des URLs de recherche :**

### **LinkedIn :**
```
https://www.linkedin.com/jobs/search/
?keywords=développeur%20react%20node
&location=Paris
&f_WT=2 (Remote)
&f_E=2 (Mid-Senior)
&f_JT=F (Full-time)
```

### **Indeed :**
```
https://fr.indeed.com/emplois
?q=développeur%20php%20symfony
&l=Paris
&jt=permanent
&remotejob=1
&fromage=7 (7 derniers jours)
```

## 📱 **Workflow recommandé :**

1. **Lancez le bot** : `./start.sh daemon`
2. **Consultez les candidatures** dans `./outbox/`
3. **Utilisez les URLs de recherche** pour trouver de vraies offres
4. **Postulez directement** via les sites
5. **Suivez vos candidatures** dans les fichiers de suivi

## 🎉 **Avantages de cette approche :**

- ✅ **URLs fonctionnelles** qui mènent à de vraies offres
- ✅ **Flexibilité** pour parcourir plusieurs offres
- ✅ **Mise à jour automatique** des offres disponibles
- ✅ **Pas de risque** d'URLs cassées
- ✅ **Recherche ciblée** selon vos critères

---

**💡 Rappel : Les URLs de recherche sont plus utiles que les URLs de postes spécifiques car elles vous donnent accès à toutes les offres correspondant à vos critères !**
