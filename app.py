import asyncio
import json
from flask import Flask, render_template_string, request
from playwright.async_api import async_playwright

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
        input[type="text"] { width: 75%; padding: 10px; font-size: 16px; border: 1px solid #ccc; border-radius: 4px; }
        button { padding: 10px 15px; font-size: 16px; background: #28a745; color: white; border: none; border-radius: 4px; cursor: pointer; }
        button:hover { background: #218838; }
        .copy-btn { background: #007bff; margin-top: 10px; }
        pre { background: #272822; color: #f8f8f2; padding: 15px; border-radius: 5px; overflow-x: auto; max-height: 400px; }
    </style>
</head>
<body>
    <div class="container">
        <h2>Google Maps Scraper (JSON Output)</h2>
        <form method="POST">
            <input type="text" name="location" placeholder="e.g. PG in Sector 60 Gurugram" value="{{ query }}" required>
            <button type="submit">Search</button>
        </form>

        {% if json_data %}
            <h3>Scraped JSON Data:</h3>
            <button class="copy-btn" onclick="copyData()">Copy JSON</button>
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


async def scrape_gmaps(query):
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True, args=["--no-sandbox", "--disable-setuid-sandbox"]
        )
        page = await browser.new_page()

        url = f"https://www.google.com/maps/search/{query.replace(' ', '+')}"
        await page.goto(url, timeout=60000)
        await page.wait_for_timeout(4000)

        # Scrolling to get results
        try:
            scrollable = page.locator('div[role="feed"]')
            for _ in range(2):
                await scrollable.evaluate(
                    "node => node.scrollTop = node.scrollHeight"
                )
                await page.wait_for_timeout(1500)
        except Exception:
            pass

        # Parse Data
        places = await page.locator("div.Nv2PK").all()
        results = []

        for place in places:
            try:
                name = await place.locator("div.qBF1Pd").inner_text()
                rating = (
                    await place.locator("span.MW432").inner_text()
                    if await place.locator("span.MW432").count() > 0
                    else "N/A"
                )
                info = (
                    await place.locator("div.W4E33").inner_text()
                    if await place.locator("div.W4E33").count() > 0
                    else "N/A"
                )

                results.append(
                    {"name": name, "rating": rating, "details": info}
                )
            except Exception:
                continue

        await browser.close()
        return results


@app.route("/", methods=["GET", "POST"])
def index():
    json_data = None
    query = ""
    if request.method == "POST":
        query = request.form.get("location")
        scraped_list = asyncio.run(scrape_gmaps(query))
        json_data = json.dumps(scraped_list, indent=4, ensure_ascii=False)

    return render_template_string(
        HTML_TEMPLATE, json_data=json_data, query=query
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
    
