from flask import Flask, render_template_string, request, jsonify
import requests
from bs4 import BeautifulSoup
import json

app = Flask(__name__)

# HTML Template (यूजर इंटरफेस के लिए)
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="hi">
<head>
    <meta charset="UTF-8">
    <title>99acres Broker JSON Scraper</title>
    <style>
        body { font-family: Arial, sans-serif; background: #f4f7f6; margin: 0; padding: 20px; }
        .container { max-width: 700px; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 4px 10px rgba(0,0,0,0.1); margin: auto; }
        h2 { color: #d32f2f; text-align: center; }
        label { font-weight: bold; display: block; margin-top: 15px; }
        input[type="text"] { width: 100%; padding: 10px; margin-top: 5px; border: 1px solid #ccc; border-radius: 4px; box-sizing: border-box; }
        button { background: #d32f2f; color: white; border: none; padding: 12px 20px; margin-top: 20px; width: 100%; border-radius: 4px; font-size: 16px; cursor: pointer; }
        button:hover { background: #b71c1c; }
        .result-box { margin-top: 20px; background: #eef2f3; padding: 15px; border-radius: 4px; word-break: break-all; max-height: 300px; overflow-y: auto; }
    </style>
</head>
<body>
    <div class="container">
        <h2>99acres Broker Scraper</h2>
        <form method="POST" action="/scrape">
            <label for="url">99acres Search URL (डीलर/ब्रोकर फ़िल्टर किया हुआ लिंक):</label>
            <input type="text" id="url" name="url" placeholder="https://www.99acres.com/property-in-..." required>
            <button type="submit">JSON डेटा निकालें</button>
        </form>
    </div>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/scrape', methods=['POST'])
def scrape():
    target_url = request.form.get('url')
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9"
    }

    try:
        response = requests.get(target_url, headers=headers, timeout=15)
        if response.status_code != 200:
            return jsonify({"error": f"Failed to fetch page, status code: {response.status_code}"}), 400

        soup = BeautifulSoup(response.text, 'html.parser')
        
        listings_data = []
        # 99acres के कार्ड्स ढूंढना
        cards = soup.select("article.srpTuple__tupleCard, .projectTuple__card, .tuple__card")

        for card in cards:
            # चेक करें कि ब्रोकर है या नहीं
            posted_by = ""
            posted_elem = card.select_one(".srpTuple__ownerInfo, .tuple__postedBy")
            if posted_elem:
                posted_by = posted_elem.get_text().strip()

            # अगर ओनर है तो स्किप करें (सिर्फ ब्रोकर्स रखें)
            if "owner" in posted_by.lower():
                continue

            title_elem = card.select_one(".srpTuple__des_title, h3, .tuple__title")
            price_elem = card.select_one(".srpTuple__priceList, .tuple__price")
            loc_elem = card.select_one(".srpTuple__subHeading, .tuple__location")
            
            link_elem = card.select_one("a.srpTuple__spacer, a")
            detail_url = ""
            if link_elem and link_elem.has_attr('href'):
                detail_url = link_elem['href']
                if not detail_url.startswith("http"):
                    detail_url = "https://www.99acres.com" + detail_url

            listings_data.append({
                "title": title_elem.get_text().strip() if title_elem else "N/A",
                "price": price_elem.get_text().strip() if price_elem else "N/A",
                "location": loc_elem.get_text().strip() if loc_elem else "N/A",
                "posted_by": posted_by if posted_by else "Dealer/Agent",
                "detail_link": detail_url
            })

        return jsonify({
            "status": "success",
            "total_listings_found": len(listings_data),
            "data": listings_data
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
        
