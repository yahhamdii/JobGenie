# 🐳 Bot de Candidature Automatique - Version Docker

## 🚀 **Démarrage ultra-rapide**

### **Option 1: Démarrage automatique (recommandé)**
```bash
# Rendre le script exécutable (une seule fois)
chmod +x start_docker.sh

# Démarrer l'application
./start_docker.sh
```

### **Option 2: Démarrage manuel**
```bash
# Construire et démarrer
docker-compose build
docker-compose up -d

# Vérifier le statut
docker-compose ps
```

## 🌐 **Accès à l'application**

Une fois démarré, votre bot est accessible sur :
- **Interface web** : http://localhost:7001
- **Dashboard** : Surveillance et contrôle en temps réel

## 📱 **Fonctionnalités de l'interface web**

### **Dashboard principal**
- 📊 **Statut du bot** : Actif/Arrêté
- 📁 **Candidatures** : Nombre total envoyées
- 🎯 **Score minimum** : Seuil de correspondance (60%)
- 📧 **Notifications** : Configuration email/Slack

### **Actions disponibles**
- 🚀 **Démarrer** : Lance le bot automatique
- ⏹️ **Arrêter** : Arrête le bot
- 🔄 **Exécuter** : Cycle unique de candidature
- 📊 **Actualiser** : Mise à jour des données

### **Informations en temps réel**
- 📋 **Candidatures récentes** : Dernières envoyées
- ⚙️ **Configuration** : Profil et préférences
- 📈 **Statistiques** : Résultats des cycles

## 🎯 **Système automatique intelligent**

### **Filtrage automatique**
- ✅ **Score minimum 60%** : Seules les meilleures offres
- 🔍 **Analyse intelligente** : Compétences, localisation, contrat
- 📅 **Offres récentes** : Moins de 7 jours

### **Génération optimisée**
- 🤖 **GPT intelligent** : Prompts personnalisés par score
- 📝 **Lettres ciblées** : Adaptées à chaque poste
- 🎨 **Format professionnel** : TXT + PDF automatiques

### **Candidature automatique**
- 🚀 **Envoi automatique** : Via Playwright/Selenium
- 📧 **Email de confirmation** : Après chaque candidature
- 📁 **Organisation** : Dossiers structurés dans `./outbox`

## 🛠️ **Commandes utiles**

### **Surveillance**
```bash
# Logs en temps réel
docker-compose logs -f bot-candidature

# Statut des services
docker-compose ps

# Ressources utilisées
docker stats
```

### **Gestion**
```bash
# Redémarrer le bot
docker-compose restart bot-candidature

# Arrêter tous les services
docker-compose down

# Reconstruire l'image
docker-compose build --no-cache
```

### **Tests**
```bash
# Test complet Docker
./test_docker.sh

# Test du système automatique
python3 test_auto_candidature.py

# Test avec de vraies offres
python3 test_linkedin_real.py
```

## 🔧 **Configuration**

### **Fichiers requis**
- `config.yaml` : Configuration du bot
- `.env` : Variables d'environnement
- `cv.pdf` : Votre CV

### **Variables d'environnement (.env)**
```bash
# API OpenAI
OPENAI_API_KEY=votre_clé_api

# Email SMTP
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=votre_email@gmail.com
SMTP_PASSWORD=votre_mot_de_passe_app

# Webhooks (optionnel)
SLACK_WEBHOOK_URL=https://hooks.slack.com/...
WEBHOOK_URL=https://votre-webhook.com/...
```

## 📊 **Architecture Docker**

### **Services inclus**
- **bot-candidature** : Bot principal + interface web
- **ollama** : Génération locale de lettres (optionnel)
- **redis** : Cache et sessions (optionnel)
- **prometheus** : Monitoring (optionnel)
- **grafana** : Dashboards (optionnel)

### **Ports exposés**
- **7001** : Interface web principale
- **11434** : Service Ollama
- **6379** : Redis
- **9090** : Prometheus
- **3000** : Grafana

## 🚨 **Dépannage**

### **Problèmes courants**

#### **Port 7001 déjà utilisé**
```bash
# Vérifier le processus
lsof -i :7001

# Arrêter ou changer le port
```

#### **Service ne démarre pas**
```bash
# Voir les logs
docker-compose logs bot-candidature

# Vérifier la config
docker-compose config
```

#### **Erreur de permission**
```bash
# Vérifier les permissions
ls -la config.yaml .env

# Corriger si nécessaire
chmod 644 config.yaml .env
```

### **Logs et debugging**
```bash
# Logs détaillés
docker-compose logs -f --tail=100 bot-candidature

# Logs avec timestamps
docker-compose logs -f -t bot-candidature

# Logs d'un service spécifique
docker-compose logs ollama
```

## 🔒 **Sécurité**

### **Bonnes pratiques**
- ✅ Ne jamais commiter `.env`
- ✅ Mots de passe forts
- ✅ Accès limité au port 7001
- ✅ Surveillance des logs

### **Firewall (optionnel)**
```bash
# macOS
sudo pfctl -e
echo "block drop in proto tcp from any to any port 7001" | sudo pfctl -f -

# Linux
sudo ufw deny 7001
```

## 📈 **Monitoring avancé**

### **Grafana (port 3000)**
- 📊 Dashboards de performance
- 📈 Métriques des candidatures
- 🚨 Alertes automatiques

### **Prometheus (port 9090)**
- 📊 Collecte de métriques
- 📈 Historique des performances
- 🔍 Requêtes personnalisées

## 🎯 **Utilisation en production**

### **Recommandations**
- 🌐 Reverse proxy (nginx)
- 🔒 HTTPS avec Let's Encrypt
- 💾 Sauvegardes automatiques
- 📊 Surveillance des ressources

### **Exemple nginx**
```nginx
server {
    listen 80;
    server_name votre-domaine.com;
    
    location / {
        proxy_pass http://localhost:7001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 🆘 **Support**

### **Ressources**
- 📚 Guide Docker : `GUIDE_DOCKER.md`
- 🧪 Tests : `test_docker.sh`
- 📋 Logs : `docker-compose logs`

### **En cas de problème**
1. 🔍 Vérifier les logs
2. ⚙️ Vérifier la configuration
3. 🔄 Redémarrer le service
4. 🔨 Reconstruire l'image

---

## 🎉 **Félicitations !**

Votre bot de candidature automatique est maintenant :
- 🐳 **Containerisé** avec Docker
- 🌐 **Accessible** via interface web sur le port 7001
- 🤖 **Intelligent** avec filtrage automatique ≥60%
- 📧 **Automatique** avec emails de confirmation
- 📊 **Surveillé** avec métriques en temps réel

**🚀 Ouvrez http://localhost:7001 et commencez à automatiser vos candidatures !**
