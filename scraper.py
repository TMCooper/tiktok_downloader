import requests
import re
import time

def fetch_html_from_api(api_url, target_url):
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

def main():
    api_url = 'http://127.0.0.1:5000/'  # Remplace par l'URL de ton API Flask si elle est différente
    target_url = 'https://vm.tiktok.com/ZGecpFCgv/'  # Remplace par l'URL que tu veux analyser
    
    # Demande à l'API de récupérer le contenu HTML
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

if __name__ == "__main__":
    main()
