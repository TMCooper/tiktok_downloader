import requests
from bs4 import BeautifulSoup
import pyktok as pyk
import subprocess
import os

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

def run_scraper():
    """Exécuter le script scraper.py."""
    try:
        # Exécuter le script scraper.py
        result = subprocess.run(['python', 'scraper.py'], capture_output=True, text=True)
        print("Sortie de scraper.py:")
        print(result.stdout)
        if result.stderr:
            print("Erreurs de scraper.py:")
            print(result.stderr)
    except Exception as e:
        print(f"Erreur lors de l'exécution de scraper.py: {e}")

def main():
    # Exécuter le script scraper.py
    run_scraper()

    # URL de la page contenant les liens
    page_url = 'http://127.0.0.1:5000/view-links'  # Remplacez par l'URL de votre page de liens

    # Récupérer les liens de la page
    links = fetch_links_from_page(page_url)
    
    # Afficher les liens automatiquement
    display_links(links)

if __name__ == "__main__":
    main()
