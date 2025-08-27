#!/usr/bin/env python3
"""
Script de configuration de l'API GPT
Configure facilement votre clé API OpenAI
"""

import os
import getpass

def setup_openai_api():
    """Configuration de l'API OpenAI"""
    print("🔑 Configuration de l'API OpenAI (GPT)")
    print("=" * 50)
    
    # Vérifier si le fichier .env existe
    env_file = '.env'
    if not os.path.exists(env_file):
        print("❌ Fichier .env non trouvé. Création...")
        # Créer le fichier .env de base
        with open(env_file, 'w') as f:
            f.write("# Configuration des variables d'environnement\n\n")
            f.write("# API OpenAI\n")
            f.write("OPENAI_API_KEY=\n\n")
            f.write("# Configuration SMTP\n")
            f.write("SMTP_SERVER=smtp.gmail.com\n")
            f.write("SMTP_PORT=587\n")
            f.write("SMTP_USERNAME=ecommercetunisia1@gmail.com\n")
            f.write("SMTP_PASSWORD=hnbr ideo qrby zuzz\n\n")
            f.write("# Configuration des logs\n")
            f.write("LOG_LEVEL=INFO\n")
            f.write("LOG_FILE=logs/bot.log\n")
    
    # Lire le fichier .env actuel
    with open(env_file, 'r') as f:
        content = f.read()
    
    # Demander la clé API
    print("\n📋 Pour obtenir votre clé API OpenAI :")
    print("   1. Allez sur : https://platform.openai.com/api-keys")
    print("   2. Connectez-vous ou créez un compte")
    print("   3. Cliquez sur 'Create new secret key'")
    print("   4. Copiez la clé générée")
    print()
    
    api_key = getpass.getpass("🔑 Entrez votre clé API OpenAI (sera masquée): ").strip()
    
    if not api_key:
        print("❌ Aucune clé fournie. Configuration annulée.")
        return False
    
    # Mettre à jour le fichier .env
    if 'OPENAI_API_KEY=' in content:
        # Remplacer la ligne existante
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if line.startswith('OPENAI_API_KEY='):
                lines[i] = f'OPENAI_API_KEY={api_key}'
                break
        
        new_content = '\n'.join(lines)
    else:
        # Ajouter la ligne
        new_content = content + f'\nOPENAI_API_KEY={api_key}\n'
    
    # Écrire le fichier mis à jour
    with open(env_file, 'w') as f:
        f.write(new_content)
    
    print("✅ Clé API configurée avec succès !")
    print("🔒 Fichier .env mis à jour")
    
    # Vérifier la configuration
    print("\n🧪 Test de la configuration...")
    try:
        os.environ['OPENAI_API_KEY'] = api_key
        from nlp.generator import LetterGenerator
        from config_manager import ConfigManager
        
        config = ConfigManager()
        generator = LetterGenerator(config)
        
        print("✅ Configuration testée avec succès !")
        print("✅ Le générateur de lettres est prêt")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors du test: {e}")
        print("💡 Vérifiez que votre clé API est valide")
        return False

def main():
    """Fonction principale"""
    print("🚀 Configuration de votre bot de candidature")
    print("=" * 60)
    
    success = setup_openai_api()
    
    if success:
        print("\n🎉 Configuration terminée !")
        print("💡 Vous pouvez maintenant lancer le test de candidature :")
        print("   python3 test_linkedin_real.py")
    else:
        print("\n⚠️ Configuration échouée. Vérifiez les erreurs ci-dessus.")
    
    return success

if __name__ == "__main__":
    main()
