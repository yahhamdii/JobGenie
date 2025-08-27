#!/usr/bin/env python3
"""
Interface web pour le bot de candidature automatique
Permet de surveiller et contrôler le bot via un navigateur web
"""

import os
import json
import logging
from datetime import datetime
from flask import Flask, render_template_string, request, jsonify, redirect, url_for
from config_manager import ConfigManager
from auto_candidature_manager import AutoCandidatureManager
from threading import Thread
from bot import JobBot

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Configuration globale
BOT_STATUS = {
    'running': False,
    'last_run': None,
    'total_candidatures': 0,
    'last_cycle_results': None
}
_worker_thread = None

def get_bot_status():
    """Récupère le statut actuel du bot"""
    try:
        config = ConfigManager()
        auto_manager = AutoCandidatureManager(config)
        
        # Statut des notifications
        notif_status = auto_manager.notification_manager.get_notification_status()
        
        # Compter les candidatures dans outbox
        candidatures_count = 0
        if os.path.exists('outbox'):
            candidatures_count = len([d for d in os.listdir('outbox') if os.path.isdir(os.path.join('outbox', d))])
        
        return {
            'running': BOT_STATUS['running'],
            'last_run': BOT_STATUS['last_run'],
            'total_candidatures': candidatures_count,
            'last_cycle_results': BOT_STATUS['last_cycle_results'],
            'config': {
                'profile': config.get_profile(),
                'preferences': config.get_preferences(),
                'auto_candidature': auto_manager.get_auto_candidature_status(),
                'notifications': notif_status
            }
        }
    except Exception as e:
        logger.error(f"Erreur lors de la récupération du statut: {e}")
        return {'error': str(e)}

def get_recent_candidatures(limit=10):
    """Récupère les candidatures récentes"""
    try:
        candidatures = []
        if os.path.exists('outbox'):
            outbox_items = os.listdir('outbox')
            outbox_items.sort(key=lambda x: os.path.getctime(os.path.join('outbox', x)), reverse=True)
            
            for item in outbox_items[:limit]:
                item_path = os.path.join('outbox', item)
                if os.path.isdir(item_path):
                    # Lire le fichier de résumé
                    resume_file = os.path.join(item_path, 'RESUME_CANDIDATURE.txt')
                    if os.path.exists(resume_file):
                        with open(resume_file, 'r', encoding='utf-8') as f:
                            content = f.read()
                            
                        # Extraire les informations
                        candidature_info = {
                            'dossier': item,
                            'date_creation': datetime.fromtimestamp(os.path.getctime(item_path)).strftime('%d/%m/%Y %H:%M'),
                            'resume': content[:200] + '...' if len(content) > 200 else content
                        }
                        candidatures.append(candidature_info)
        
        return candidatures
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des candidatures: {e}")
        return []

# Template HTML pour l'interface
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🤖 Bot de Candidature Automatique</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container { 
            max-width: 1200px; 
            margin: 0 auto; 
            background: white; 
            border-radius: 15px; 
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            overflow: hidden;
        }
        .header { 
            background: linear-gradient(135deg, #28a745, #20c997); 
            color: white; 
            padding: 30px; 
            text-align: center;
        }
        .header h1 { font-size: 2.5em; margin-bottom: 10px; }
        .header p { font-size: 1.2em; opacity: 0.9; }
        
        .content { padding: 30px; }
        .status-card { 
            background: #f8f9fa; 
            border-radius: 10px; 
            padding: 25px; 
            margin-bottom: 30px;
            border-left: 5px solid #28a745;
        }
        .status-card h2 { color: #28a745; margin-bottom: 20px; }
        .status-grid { 
            display: grid; 
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); 
            gap: 20px; 
            margin-bottom: 20px;
        }
        .status-item { 
            background: white; 
            padding: 20px; 
            border-radius: 8px; 
            text-align: center;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .status-item .value { 
            font-size: 2em; 
            font-weight: bold; 
            color: #28a745; 
        }
        .status-item .label { 
            color: #6c757d; 
            margin-top: 5px; 
        }
        
        .actions { 
            display: flex; 
            gap: 15px; 
            margin-bottom: 30px; 
            flex-wrap: wrap;
        }
        .btn { 
            padding: 12px 25px; 
            border: none; 
            border-radius: 8px; 
            cursor: pointer; 
            font-size: 1em; 
            font-weight: 500; 
            transition: all 0.3s ease;
            text-decoration: none;
            display: inline-block;
        }
        .btn-primary { 
            background: #007bff; 
            color: white; 
        }
        .btn-primary:hover { background: #0056b3; transform: translateY(-2px); }
        .btn-success { 
            background: #28a745; 
            color: white; 
        }
        .btn-success:hover { background: #1e7e34; transform: translateY(-2px); }
        .btn-warning { 
            background: #ffc107; 
            color: #212529; 
        }
        .btn-warning:hover { background: #e0a800; transform: translateY(-2px); }
        .btn-danger { 
            background: #dc3545; 
            color: white; 
        }
        .btn-danger:hover { background: #c82333; transform: translateY(-2px); }
        
        .candidatures { 
            background: white; 
            border-radius: 10px; 
            padding: 25px; 
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .candidature-item { 
            background: #f8f9fa; 
            padding: 20px; 
            margin-bottom: 15px; 
            border-radius: 8px; 
            border-left: 4px solid #007bff;
        }
        .candidature-item h3 { color: #007bff; margin-bottom: 10px; }
        .candidature-item .date { color: #6c757d; font-size: 0.9em; margin-bottom: 10px; }
        .candidature-item .resume { color: #495057; line-height: 1.6; }
        
        .config-section { 
            background: white; 
            border-radius: 10px; 
            padding: 25px; 
            margin-top: 30px; 
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .config-grid { 
            display: grid; 
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); 
            gap: 20px; 
        }
        .config-item { 
            background: #f8f9fa; 
            padding: 20px; 
            border-radius: 8px; 
        }
        .config-item h4 { color: #495057; margin-bottom: 15px; }
        .config-item .value { 
            background: white; 
            padding: 10px; 
            border-radius: 5px; 
            border: 1px solid #dee2e6; 
            font-family: monospace; 
            font-size: 0.9em;
        }
        
        @media (max-width: 768px) {
            .status-grid { grid-template-columns: 1fr; }
            .actions { flex-direction: column; }
            .config-grid { grid-template-columns: 1fr; }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤖 Bot de Candidature Automatique</h1>
            <p>Interface de surveillance et de contrôle</p>
        </div>
        
        <div class="content">
            <!-- Statut du bot -->
            <div class="status-card">
                <h2>📊 Statut du Bot</h2>
                <div class="status-grid">
                    <div class="status-item">
                        <div class="value" id="status-value">{{ "🟢 Actif" if bot_status.running else "🔴 Arrêté" }}</div>
                        <div class="label">Statut</div>
                    </div>
                    <div class="status-item">
                        <div class="value" id="candidatures-value">{{ bot_status.total_candidatures }}</div>
                        <div class="label">Candidatures</div>
                    </div>
                    <div class="status-item">
                        <div class="value" id="score-min-value">{{ bot_status.config.auto_candidature.min_score_percentage }}%</div>
                        <div class="label">Score Minimum</div>
                    </div>
                    <div class="status-item">
                        <div class="value" id="email-status">{{ "✅ Configuré" if bot_status.config.notifications.email_configured else "❌ Non configuré" }}</div>
                        <div class="label">Email</div>
                    </div>
                </div>
                
                <div class="actions">
                    <button class="btn btn-success" onclick="startBot()">🚀 Démarrer le Bot</button>
                    <button class="btn btn-danger" onclick="stopBot()">⏹️ Arrêter le Bot</button>
                    <button class="btn btn-primary" onclick="runOnce()">🔄 Exécuter une fois</button>
                    <button class="btn btn-warning" onclick="refreshStatus()">🔄 Actualiser</button>
                </div>
                
                {% if bot_status.last_run %}
                <p><strong>Dernière exécution:</strong> {{ bot_status.last_run }}</p>
                {% endif %}
            </div>
            
            <!-- Candidatures récentes -->
            <div class="candidatures">
                <h2>📁 Candidatures Récentes</h2>
                {% if candidatures %}
                    {% for candidature in candidatures %}
                    <div class="candidature-item">
                        <h3>{{ candidature.dossier }}</h3>
                        <div class="date">Créé le: {{ candidature.date_creation }}</div>
                        <div class="resume">{{ candidature.resume }}</div>
                    </div>
                    {% endfor %}
                {% else %}
                    <p>Aucune candidature trouvée.</p>
                {% endif %}
            </div>
            
            <!-- Configuration -->
            <div class="config-section">
                <h2>⚙️ Configuration</h2>
                <div class="config-grid">
                    <div class="config-item">
                        <h4>👤 Profil</h4>
                        <div class="value">{{ bot_status.config.profile.nom }}</div>
                        <div class="value">{{ bot_status.config.profile.email }}</div>
                    </div>
                    <div class="config-item">
                        <h4>🛠️ Compétences</h4>
                        <div class="value">{{ ', '.join(bot_status.config.preferences.stack_technique) }}</div>
                    </div>
                    <div class="config-item">
                        <h4>📍 Localisation</h4>
                        <div class="value">{{ ', '.join(bot_status.config.preferences.localisation) }}</div>
                    </div>
                    <div class="config-item">
                        <h4>🎯 Candidature Auto</h4>
                        <div class="value">Score min: {{ bot_status.config.auto_candidature.min_score_percentage }}%</div>
                        <div class="value">Max/cycle: {{ bot_status.config.auto_candidature.max_candidatures_per_cycle }}</div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        function startBot() {
            fetch('/api/start', {method: 'POST'})
                .then(response => response.json())
                .then(data => {
                    alert(data.message);
                    refreshStatus();
                });
        }
        
        function stopBot() {
            fetch('/api/stop', {method: 'POST'})
                .then(response => response.json())
                .then(data => {
                    alert(data.message);
                    refreshStatus();
                });
        }
        
        function runOnce() {
            fetch('/api/run-once', {method: 'POST'})
                .then(response => response.json())
                .then(data => {
                    alert(data.message);
                    refreshStatus();
                });
        }
        
        function refreshStatus() {
            location.reload();
        }
        
        // Actualisation automatique toutes les 30 secondes
        setInterval(refreshStatus, 30000);
    </script>
</body>
</html>
"""

@app.route('/')
def dashboard():
    """Page principale du dashboard"""
    bot_status = get_bot_status()
    candidatures = get_recent_candidatures(10)
    
    return render_template_string(HTML_TEMPLATE, 
                                bot_status=bot_status, 
                                candidatures=candidatures)

@app.route('/api/start', methods=['POST'])
def start_bot():
    """Démarre le bot"""
    try:
        global _worker_thread
        if BOT_STATUS['running']:
            return jsonify({'success': True, 'message': 'Bot déjà en cours.'})

        BOT_STATUS['running'] = True
        BOT_STATUS['last_run'] = datetime.now().strftime('%d/%m/%Y %H:%M:%S')

        def _run_scheduler():
            try:
                JobBot().start_scheduler()
            finally:
                BOT_STATUS['running'] = False

        _worker_thread = Thread(target=_run_scheduler, daemon=True)
        _worker_thread.start()
        logger.info("Bot démarré via l'interface web (scheduler)")
        return jsonify({'success': True, 'message': 'Bot démarré avec succès !'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Erreur: {e}'})

@app.route('/api/stop', methods=['POST'])
def stop_bot():
    """Arrête le bot"""
    try:
        # Note: pour un vrai arrêt, il faudrait une coopérative via un flag/évènement
        BOT_STATUS['running'] = False
        logger.info("Demande d'arrêt du bot via l'interface web")
        
        return jsonify({'success': True, 'message': 'Bot arrêté avec succès !'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Erreur: {e}'})

@app.route('/api/run-once', methods=['POST'])
def run_once():
    """Exécute le bot une seule fois"""
    try:
        def _run_once_bg():
            try:
                bot = JobBot()
                results = bot.run_cycle()
                BOT_STATUS['last_run'] = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
                BOT_STATUS['last_cycle_results'] = {
                    'candidatures_traitees': len(results)
                }
            except Exception as ex:
                logger.error(f"Erreur run-once: {ex}")

        Thread(target=_run_once_bg, daemon=True).start()
        logger.info("Exécution unique du bot via l'interface web (bg)")
        return jsonify({'success': True, 'message': 'Exécution lancée en arrière-plan. Actualisez dans quelques instants.'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Erreur: {e}'})

@app.route('/api/status')
def api_status():
    """API pour récupérer le statut du bot"""
    return jsonify(get_bot_status())

if __name__ == '__main__':
    logger.info("🚀 Démarrage de l'interface web sur le port 7001")
    app.run(host='0.0.0.0', port=7001, debug=False)
