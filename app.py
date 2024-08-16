from flask import Flask, request, jsonify, render_template_string
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time

app = Flask(__name__)
is_ready = False
received_links = []  # Variable pour stocker les liens reçus

def fetch_html_with_selenium(url):
    global is_ready
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    driver = webdriver.Chrome(options=chrome_options)
    driver.get(url)
    
    # Attendre que le contenu initial soit chargé
    time.sleep(5)
    
    # Défilement pour charger plus de contenu si nécessaire
    last_height = driver.execute_script("return document.body.scrollHeight")
    
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)  # Attendre que le contenu soit chargé après le défilement
        
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height
    
    html = driver.page_source
    driver.quit()
    
    is_ready = True
    return html

@app.route('/', methods=['GET', 'POST'])
def index():
    global is_ready
    html_content = ''
    if request.method == 'POST':
        is_ready = False  # Réinitialiser l'état
        tiktok_url = request.form['url']
        html_content = fetch_html_with_selenium(tiktok_url)
        html_content = beautify_html(html_content)
        return render_template_string(html_template, html_content=html_content)
    return render_template_string(html_template, html_content=html_content)

@app.route('/status', methods=['GET'])
def status():
    global is_ready
    return jsonify({'status': 'ready' if is_ready else 'not ready'})

@app.route('/links', methods=['POST'])
def receive_links():
    """Recevoir les liens vidéo et les stocker."""
    global received_links
    data = request.get_json()
    if 'links' in data:
        received_links = data['links']
        return jsonify({'status': 'success', 'message': 'Liens reçus avec succès!'}), 200
    return jsonify({'status': 'error', 'message': 'Aucun lien trouvé dans la demande.'}), 400

@app.route('/view-links', methods=['GET'])
def view_links():
    """Afficher tous les liens reçus."""
    return render_template_string(links_template, links=received_links)

def beautify_html(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    return soup.prettify()

html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>HTML Content Fetcher</title>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/prism/1.28.0/themes/prism-okaidia.min.css" rel="stylesheet" />
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 20px;
        }
        pre {
            padding: 15px;
            border-radius: 5px;
            border: 1px solid #ccc;
        }
        h1 {
            color: #333;
        }
        label {
            font-weight: bold;
        }
        input[type="text"] {
            width: 80%;
            padding: 5px;
            margin-right: 10px;
        }
        button {
            padding: 5px 10px;
            font-size: 16px;
            cursor: pointer;
        }
    </style>
</head>
<body>
    <h1>HTML Content Fetcher</h1>
    <form method="POST">
        <label for="url">Enter URL:</label>
        <input type="text" id="url" name="url" required>
        <button type="submit">Fetch HTML</button>
    </form>
    
    <h2>HTML Content:</h2>
    <pre><code class="language-html">{{ html_content | e }}</code></pre>

    <script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.28.0/prism.min.js"></script>
</body>
</html>
"""

links_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Video Links</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 20px;
        }
        ul {
            list-style-type: none;
            padding: 0;
        }
        li {
            margin: 5px 0;
        }
        a {
            text-decoration: none;
            color: #007bff;
        }
        a:hover {
            text-decoration: underline;
        }
    </style>
</head>
<body>
    <h1>Video Links</h1>
    <ul>
        {% for link in links %}
            <li><a href="{{ link }}" target="_blank">{{ link }}</a></li>
        {% endfor %}
    </ul>
</body>
</html>
"""

if __name__ == '__main__':
    app.run(debug=True)
