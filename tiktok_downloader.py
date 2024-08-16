import requests
from bs4 import BeautifulSoup
import pyktok as pyk
import os
import re
import time

def fetch_html_from_api(api_url, target_url):
    """Demander à l'API de récupérer le contenu HTML."""
    print("Demande à l'API de récupérer le contenu HTML...")
    try:
        response = requests.post(api_url, data={'url': target_url})
        response.raise_for_status()
        print("Le contenu HTML a été récupéré avec succès.")
        html_content = response.text
        return html_content
    except requests.RequestException as e:
        print(f"Erreur lors de la récupération du contenu HTML: {e}")
        return None

def check_if_ready(api_url):
    """Vérifier si l'API est prête pour l'analyse."""
    print("Vérification de l'état de l'API...")
    while True:
        try:
            response = requests.get(f'{api_url.rstrip("/")}/status')
            response.raise_for_status()
            status = response.json().get('status')
            if status == 'ready':
                print("L'API est prête pour l'analyse.")
                return True
            else:
                print("L'API n'est pas encore prête. Attente...")
                time.sleep(2)
        except requests.RequestException as e:
            print(f"Erreur lors de la vérification de l'état de l'API: {e}")
            time.sleep(2)  # Attendre avant de réessayer

def extract_tiktok_video_links(html_content):
    """Extraire les liens vidéo TikTok du contenu HTML en supprimant les doublons."""
    pattern = r'https://www\.tiktok\.com/@[\w.-]+/video/\d+'
    links = re.findall(pattern, html_content)
    
    # Utiliser un ensemble (set) pour éliminer les doublons
    unique_links = set(links)
    
    return list(unique_links)

def send_links_to_api(api_url, video_links):
    """Envoyer les liens vidéo à l'API."""
    print("Envoi des liens vidéo à l'API...")
    try:
        response = requests.post(f'{api_url.rstrip("/")}/links', json={'links': video_links})
        response.raise_for_status()
        print("Les liens vidéo ont été envoyés avec succès.")
        print("Réponse de l'API:", response.json())
    except requests.RequestException as e:
        print(f"Erreur lors de l'envoi des liens vidéo à l'API: {e}")

def fetch_links_from_page(url):
    """Récupérer le contenu de la page et extraire les liens vidéo."""
    try:
        # Envoyer une requête GET pour récupérer le contenu de la page
        response = requests.get(url)
        response.raise_for_status()  # Vérifier les erreurs HTTP
        html_content = response.text
        
        # Analyser le contenu HTML
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Trouver tous les liens vidéo
        links = []
        for a_tag in soup.find_all('a', href=True):
            link = a_tag['href']
            if link.startswith('https://www.tiktok.com/@') and '/video/' in link:
                # Nettoyer le lien pour le format correct
                cleaned_link = link.strip()
                links.append(cleaned_link)
                
                # Télécharger le lien
                save_video(cleaned_link)

        return links
    except requests.RequestException as e:
        print(f"Erreur lors de la récupération des liens: {e}")
        return []

def save_video(link):
    """Télécharger et sauvegarder la vidéo à l'emplacement spécifié."""
    # Déterminer le chemin de destination
    base_path = os.path.dirname(os.path.abspath(__file__))  # Répertoire du script
    videos_path = os.path.join(base_path, 'Vidéo')  # Sous-répertoire pour les vidéos
    
    # Créer le répertoire s'il n'existe pas
    if not os.path.exists(videos_path):
        os.makedirs(videos_path)
    
    # Changer le répertoire de travail pour la durée du téléchargement
    original_directory = os.getcwd()
    os.chdir(videos_path)
    
    try:
        # Appeler pyktok pour sauvegarder la vidéo
        pyk.save_tiktok(link, True)  # Ne spécifiez pas output_dir ici
    finally:
        # Rétablir le répertoire de travail d'origine
        os.chdir(original_directory)

def display_links(links):
    """Afficher les liens automatiquement."""
    if not links:
        print("Aucun lien trouvé.")
        return

    print(f"Nombre de liens vidéo trouvés: {len(links)}")
    for link in links:
        print(link)

def main():
    choix = input("Voulez vous télécharger une vidéo (V) ou un playlist de vidéo (P) ? : ")

    while choix not in ["V", "v", "P", "p"]:
        choix = input("Veulliez saisir P ou V : ")

    if choix in ["P", "p"]:
        api_url = 'http://127.0.0.1:5000/'  # Remplace par l'URL de ton API Flask si elle est différente

        # Demander à l'utilisateur de saisir l'URL cible
        target_url = input("Veuillez entrer l'URL de la playlist TikTok : ")

        # Demander à l'API de récupérer le contenu HTML
        html_content = fetch_html_from_api(api_url, target_url)
        
        if html_content:
            # Attendre que l'API indique qu'elle est prête pour l'analyse
            if check_if_ready(api_url):
                # Extraire les liens vidéo TikTok
                video_links = extract_tiktok_video_links(html_content)
                
                # Afficher le nombre de liens trouvés et les liens eux-mêmes
                print(f"Nombre de liens vidéo trouvés: {len(video_links)}")
                if len(video_links) == 0:
                    print("Aucun lien vidéo trouvé. Voici un extrait du HTML où les liens pourraient apparaître:")
                    print(html_content[:5000])  # Afficher les 5000 premiers caractères du HTML
                else:
                    for link in video_links:
                        print(link)
                    
                    # Envoyer les liens à l'API
                    send_links_to_api(api_url, video_links)

        # URL de la page contenant les liens
        page_url = 'http://127.0.0.1:5000/view-links'  # Remplacez par l'URL de votre page de liens

        # Récupérer les liens de la page
        links = fetch_links_from_page(page_url)
        
        # Afficher les liens automatiquement
        display_links(links)
    
    if choix in ["V", "v"]:
        lien_vid = input("Quelle est votre vidéo ? : ")
        # Déterminer le chemin de destination
        base_path = os.path.dirname(os.path.abspath(__file__))  # Répertoire du script
        videos_path = os.path.join(base_path, 'Vidéo')  # Sous-répertoire pour les vidéos
        
        # Créer le répertoire s'il n'existe pas
        if not os.path.exists(videos_path):
            os.makedirs(videos_path)
        
        # Changer le répertoire de travail pour la durée du téléchargement
        original_directory = os.getcwd()
        os.chdir(videos_path)
        
        try:
            # Appeler pyktok pour sauvegarder la vidéo
            pyk.save_tiktok(lien_vid, True)
            print(f"Vidéo téléchargée et sauvegardée dans {videos_path}")
        finally:
            # Rétablir le répertoire de travail d'origine
            os.chdir(original_directory)

if __name__ == "__main__":
    main()
