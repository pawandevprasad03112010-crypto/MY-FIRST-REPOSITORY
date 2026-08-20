from flask import Flask, render_template, request
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def home():
    results = []
    query = ""
    if request.method == 'POST':
        query = request.form.get('query')
        if query:
            formatted_query = query.replace(" ", "+")
            # Hum ek doosra simple search engine use karenge jo block nahi karta
            url = f"https://lite.duckduckgo.com/lite/"
            
            payload = {'q': query}
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
            
            response = requests.post(url, data=payload, headers=headers)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # DuckDuckGo Lite ke results class 'result-snippet' ya 'result-link' mein hote hain
                for td in soup.find_all('td', class_='result-snippet'):
                    text = td.get_text().strip()
                    if text:
                        results.append(text)
                        
                # Agar upar wale se na mile toh saare links nikal lo
                if not results:
                    for a in soup.find_all('a', class_='result-link'):
                        text = a.get_text().strip()
                        if text:
                            results.append(text)
                            
    return render_template('index.html', results=results, query=query)

if __name__ == '__main__':
    app.run(debug=True)
    
