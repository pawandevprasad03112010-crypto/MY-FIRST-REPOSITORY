from flask import Flask, render_template, request
import requests

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def home():
    results = []
    query = ""
    if request.method == 'POST':
        query = request.form.get('query')
        if query:
            # Google block se bachne ke liye hum DuckDuckGo ya alternative search API ka HTML version use kar sakte hain
            # Jo phone/browser par easily parse ho jata hai bina block ke.
            url = f"https://html.duckduckgo.com/html/?q={query}"
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
            
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(response.text, 'html.parser')
                # DuckDuckGo ke results extract karna
                for a in soup.find_all('a', class_='result__snippet'):
                    results.append(a.text.strip())
                    
    return render_template('index.html', results=results, query=query)

if __name__ == '__main__':
    app.run(debug=True)
    
