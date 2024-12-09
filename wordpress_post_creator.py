import requests
import base64
import os
import json
import webbrowser

CONFIG_FILE = 'wordpress_config.json'

def get_wordpress_credentials():
    # Si le fichier de configuration existe, charger les identifiants
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            config = json.load(f)
            return config.get('url'), config.get('username'), config.get('app_token')
    
    # Sinon, demander à l'utilisateur de configurer étape par étape
    print("\n🌐 Configuration Initiale de WordPress")
    
    # Étape 1 : URL du site
    while True:
        url = input("\n1️⃣ Entrez l'URL complète de votre site WordPress (ex: https://mondary.design) : ").strip()
        if url.startswith('http://') or url.startswith('https://'):
            break
        print("❌ L'URL doit commencer par http:// ou https://")
    
    # Étape 2 : Nom d'utilisateur
    username = input("\n2️⃣ Entrez votre nom d'utilisateur WordPress : ").strip()
    
    # Étape 3 : Ouvrir la page de profil pour générer le token
    print("\n3️⃣ Génération du token d'application")
    profile_url = f"{url}/wp-admin/profile.php"
    print(f"🔗 Ouverture de la page de profil : {profile_url}")
    webbrowser.open(profile_url)
    
    print("\nInstructions pour générer un token :")
    print("1. Connectez-vous à votre compte WordPress")
    print("2. Faites défiler jusqu'à 'Tokens d'application'")
    print("3. Créez un nouveau token avec des droits de publication")
    
    while True:
        app_token = input("\nEntrez le token d'application généré : ").strip()
        
        # Vérifier la connexion
        base_url = f"{url}/wp-json/wp/v2/"
        credentials = f"{username}:{app_token}"
        token = base64.b64encode(credentials.encode()).decode('utf-8')
        headers = {
            'Authorization': f'Basic {token}',
            'Content-Type': 'application/json'
        }
        
        try:
            response = requests.get(f"{base_url}posts", headers=headers, params={'per_page': 1})
            if response.status_code == 200:
                # Sauvegarder la configuration
                config = {
                    'url': url,
                    'username': username,
                    'app_token': app_token
                }
                with open(CONFIG_FILE, 'w') as f:
                    json.dump(config, f)
                print("\n✅ Connexion réussie et configuration sauvegardée !")
                return url, username, app_token
            else:
                print("\n❌ Échec de la connexion. Vérifiez vos identifiants.")
        except Exception as e:
            print(f"\n❌ Erreur de connexion : {e}")

def create_wordpress_post():
    # Obtenir les identifiants
    base_url, username, app_token = get_wordpress_credentials()
    
    # Configuration WordPress
    base_url = f"{base_url}/wp-json/wp/v2/"
    
    # Prompt user for post details
    print("\n📝 Création de Post WordPress")
    title = input("Entrez le titre du post : ")
    paragraph1 = input("Entrez le premier paragraphe : ")
    paragraph2 = input("Entrez le second paragraphe : ")

    # Combine paragraphs using Gutenberg block syntax
    content = f"""<!-- wp:paragraph -->
<p>{paragraph1}</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>{paragraph2}</p>
<!-- /wp:paragraph -->"""

    # Prepare headers with authentication
    credentials = f"{username}:{app_token}"
    token = base64.b64encode(credentials.encode()).decode('utf-8')
    headers = {
        'Authorization': f'Basic {token}',
        'Content-Type': 'application/json'
    }

    # Prepare post data
    post_data = {
        'title': title,
        'content': content,
        'status': 'draft'  # Automatically save the post as a draft
    }

    try:
        # Send POST request to create the post
        response = requests.post(f"{base_url}posts", 
                                 json=post_data, 
                                 headers=headers)
        
        # Check the response
        if response.status_code == 201:
            post = response.json()
            print("\n✅ Post créé avec succès !")
            print(f"ID du post : {post['id']}")
            print(f"URL du post : {post['link']}")
        else:
            print("\n❌ Erreur lors de la création du post :")
            print(f"Code de statut : {response.status_code}")
            print(f"Réponse : {response.text}")

    except requests.exceptions.RequestException as e:
        print(f"\n❌ Erreur de requête : {e}")

if __name__ == "__main__":
    create_wordpress_post()
