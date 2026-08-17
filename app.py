import json
import urllib.parse
from flask import Flask, render_template_string, request
import requests

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="hi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>G-Maps JSON Scraper</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background: #f4f4f9; }
        .container { max-width: 700px; margin: auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 0 10px rgba(0,0,0,0.1); }
        input[type="text"] { width: 70%; padding: 10px; font-size: 16px; border: 1px solid #ccc; border-radius: 4px; }
        button { padding: 10px 15px; font-size: 16px; background: #28a745; color: white; border: none; border-radius: 4px; cursor: pointer; }
        button:hover { background: #218838; }
        .copy-btn { background: #007bff; margin-top: 10px; margin-bottom: 10px; }
        pre { background: #272822; color: #f8f8f2; padding: 15px; border-radius: 5px; overflow-x: auto; max-height: 400px; }
    </style>
</head>
<body>
    <div class="container">
        <h2>Google Maps Data Scraper</h2>
        <form method="POST">
            <input type="text" name="location" placeholder="e.g. PG in Sector 60 Gurugram" value="{{ query }}" required>
            <button type="submit">Search</button>
        </form>

        {% if json_data %}
            <h3>Scraped Data (JSON):</h3>
            <button class="copy-btn" onclick="copyData()">Copy JSON Data</button>
            <pre id="jsonBlock">{{ json_data }}</pre>
        {% endif %}
    </div>

    <script>
        function copyData() {
            var copyText = document.getElementById("jsonBlock").innerText;
            navigator.clipboard.writeText(copyText);
            alert("JSON Data copied to clipboard!");
        }
    </script>
</body>
</html>
"""


def scrape_gmaps_clean(query):
    encoded_query = urllib.parse.quote(query)
    url = f"https://www.google.com/maps/rpc/ft/s?authuser=0&hl=en&gl=in&pb=!1m2!1s!2s!2m1!1s{encoded_query}!3m1!1s!5m1!1e1"

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            " (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
    }

    results = []

    try:
        res = requests.get(url, headers=headers, timeout=12)
        cleaned_text = res.text.replace(")]}'\n", "")

        lines = cleaned_text.split('"')
        found_names = set()

        for line in lines:
            line_str = line.strip()
            if any(
                k in line_str.lower()
                for k in ["pg", "hostel", "co-living", "stay", "house", "rooms"]
            ) and (5 < len(line_str) < 65):
                if not line_str.startswith("http") and "\\" not in line_str:
                    found_names.add(line_str)

        for idx, name in enumerate(sorted(found_names), 1):
            results.append({"id": idx, "name": name, "search_query": query})

        if not results:
            results.append(
                {"message": "No direct matches found for this keyword."}
            )

    except Exception as e:
        results.append({"error": str(e)})

    return results


@app.route("/", methods=["GET", "POST"])
def index():
    json_data = None
    query = ""
    if request.method == "POST":
        query = request.form.get("location")
        scraped_list = scrape_gmaps_clean(query)
        json_data = json.dumps(scraped_list, indent=4, ensure_ascii=False)

    return render_template_string(
        HTML_TEMPLATE, json_data=json_data, query=query
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
    
