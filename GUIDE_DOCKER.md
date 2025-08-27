# 🐳 Guide Docker - Bot de Candidature Automatique

## 🚀 **Démarrage rapide avec Docker**

### **1. Prérequis**
- Docker installé sur votre machine
- Docker Compose installé
- Fichiers `config.yaml` et `.env` configurés

### **2. Démarrage automatique**
```bash
# Rendre le script exécutable (une seule fois)
chmod +x start_docker.sh

# Démarrer l'application
./start_docker.sh
```

### **3. Démarrage manuel**
```bash
# Construire l'image
docker-compose build

# Démarrer les services
docker-compose up -d

# Vérifier le statut
docker-compose ps
```

## 🌐 **Accès à l'interface web**

Une fois démarré, votre application est accessible sur :
- **URL locale** : http://localhost:7001
- **URL réseau** : http://[VOTRE_IP]:7001

## 📱 **Fonctionnalités de l'interface web**

### **Dashboard principal**
- 📊 **Statut du bot** : Actif/Arrêté
- 📁 **Nombre de candidatures** : Total des candidatures envoyées
- 🎯 **Score minimum** : Seuil de correspondance (60%)
- 📧 **Statut email** : Configuration des notifications

### **Actions disponibles**
- 🚀 **Démarrer le bot** : Lance le bot en mode automatique
- ⏹️ **Arrêter le bot** : Arrête le bot
- 🔄 **Exécuter une fois** : Lance un cycle unique
- 🔄 **Actualiser** : Met à jour les informations

### **Informations affichées**
- 📋 **Candidatures récentes** : Dernières candidatures envoyées
- ⚙️ **Configuration** : Profil, compétences, préférences
- 📊 **Statistiques** : Résultats des derniers cycles

## 🛠️ **Commandes Docker utiles**

### **Surveillance**
```bash
# Voir les logs en temps réel
docker-compose logs -f bot-candidature

# Voir le statut des services
docker-compose ps

# Voir les ressources utilisées
docker stats
```

### **Gestion des services**
```bash
# Redémarrer le bot
docker-compose restart bot-candidature

# Arrêter tous les services
docker-compose down

# Arrêter et supprimer les volumes
docker-compose down -v
```

### **Maintenance**
```bash
# Reconstruire l'image
docker-compose build --no-cache

# Mettre à jour les dépendances
docker-compose pull

# Nettoyer les images non utilisées
docker system prune -a
```

## 🔧 **Configuration avancée**

### **Variables d'environnement**
Le fichier `.env` doit contenir :
```bash
# API OpenAI
OPENAI_API_KEY=votre_clé_api

# Configuration SMTP
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=votre_email@gmail.com
SMTP_PASSWORD=votre_mot_de_passe_app

# Webhooks (optionnel)
SLACK_WEBHOOK_URL=https://hooks.slack.com/...
WEBHOOK_URL=https://votre-webhook.com/...
```

### **Ports exposés**
- **7001** : Interface web principale
- **11434** : Service Ollama (génération locale)
- **6379** : Redis (cache)
- **9090** : Prometheus (monitoring)
- **3000** : Grafana (dashboards)

## 📊 **Profils de déploiement**

### **Profil complet (recommandé)**
```bash
docker-compose --profile full up -d
```
Inclut : Bot + Ollama + Redis + Monitoring

### **Profil monitoring**
```bash
docker-compose --profile monitoring up -d
```
Inclut : Prometheus + Grafana

### **Profil minimal**
```bash
docker-compose up -d bot-candidature
```
Inclut : Seulement le bot principal

## 🚨 **Dépannage**

### **Problèmes courants**

#### **Port 7001 déjà utilisé**
```bash
# Vérifier quel processus utilise le port
lsof -i :7001

# Arrêter le processus ou changer le port dans docker-compose.yml
```

#### **Erreur de permission**
```bash
# Vérifier les permissions des fichiers
ls -la config.yaml .env

# Corriger les permissions si nécessaire
chmod 644 config.yaml .env
```

#### **Service ne démarre pas**
```bash
# Voir les logs d'erreur
docker-compose logs bot-candidature

# Vérifier la configuration
docker-compose config
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
- Ne jamais commiter le fichier `.env`
- Utiliser des mots de passe forts
- Limiter l'accès au port 7000 si nécessaire
- Surveiller les logs pour détecter les activités suspectes

### **Firewall (optionnel)**
```bash
# Sur macOS (avec pf)
sudo pfctl -e
echo "block drop in proto tcp from any to any port 7001" | sudo pfctl -f -

# Sur Linux (avec ufw)
sudo ufw deny 7001
```

## 📈 **Monitoring et métriques**

### **Grafana (port 3000)**
- Dashboards de performance
- Métriques des candidatures
- Surveillance des erreurs

### **Prometheus (port 9090)**
- Collecte de métriques
- Alertes automatiques
- Historique des performances

## 🎯 **Utilisation en production**

### **Recommandations**
- Utiliser un reverse proxy (nginx)
- Configurer HTTPS avec Let's Encrypt
- Mettre en place des sauvegardes automatiques
- Surveiller les ressources système

### **Exemple avec nginx**
```nginx
server {
    listen 80;
    server_name votre-domaine.com;
    
    location / {
        proxy_pass http://localhost:7000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 🆘 **Support et aide**

### **Ressources utiles**
- Logs Docker : `docker-compose logs`
- Documentation Flask : https://flask.palletsprojects.com/
- Documentation Docker : https://docs.docker.com/

### **En cas de problème**
1. Vérifier les logs : `docker-compose logs bot-candidature`
2. Vérifier la configuration : `docker-compose config`
3. Redémarrer le service : `docker-compose restart bot-candidature`
4. Reconstruire l'image : `docker-compose build --no-cache`

---

**🎉 Votre bot de candidature automatique est maintenant accessible via une interface web moderne sur le port 7001 !**
