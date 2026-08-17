import json
from duckduckgo_search import DDGS
from flask import Flask, render_template_string, request

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="hi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Live Maps JSON Scraper</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background: #f4f4f9; }
        .container { max-width: 750px; margin: auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 0 10px rgba(0,0,0,0.1); }
        input[type="text"] { width: 70%; padding: 10px; font-size: 16px; border: 1px solid #ccc; border-radius: 4px; }
        button { padding: 10px 15px; font-size: 16px; background: #28a745; color: white; border: none; border-radius: 4px; cursor: pointer; }
        button:hover { background: #218838; }
        .copy-btn { background: #007bff; margin-top: 10px; margin-bottom: 10px; }
        pre { background: #272822; color: #f8f8f2; padding: 15px; border-radius: 5px; overflow-x: auto; max-height: 450px; }
    </style>
</head>
<body>
    <div class="container">
        <h2>Live Maps Business Scraper</h2>
        <form method="POST">
            <input type="text" name="location" placeholder="e.g. PG in Kolkata" value="{{ query }}" required>
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


def scrape_maps_free(query):
    results = []
    try:
        with DDGS() as ddgs:
            # Fetching map locations directly
            maps_results = list(ddgs.maps(query, max_results=20))

            for idx, item in enumerate(maps_results, 1):
                results.append(
                    {
                        "id": idx,
                        "title": item.get("title"),
                        "address": item.get("address"),
                        "phone": item.get("phone", "N/A"),
                        "latitude": item.get("latitude"),
                        "longitude": item.get("longitude"),
                    }
                )

        if not results:
            results.append({"message": "No places found for this query."})

    except Exception as e:
        results.append({"error": str(e)})

    return results


@app.route("/", methods=["GET", "POST"])
def index():
    json_data = None
    query = ""
    if request.method == "POST":
        query = request.form.get("location")
        scraped_list = scrape_maps_free(query)
        json_data = json.dumps(scraped_list, indent=4, ensure_ascii=False)

    return render_template_string(
        HTML_TEMPLATE, json_data=json_data, query=query
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
    
