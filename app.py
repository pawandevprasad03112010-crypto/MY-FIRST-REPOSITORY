import os
import time
from flask import Flask, render_template_string, request, jsonify
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from pymongo import MongoClient
from datetime import datetime

app = Flask(__name__)

# =========================================================
# ⚙️ AAPKI MONGODB SETTINGS (YAHAN DETAILS DAALEIN)
# =========================================================
MONGO_URI = os.getenv("MONGO_URI", "YOUR_MONGO_DB_URI_HERE")
DB_NAME = "apne_database_ka_naam"           
COLLECTION_NAME = "apne_collection_ka_naam"   

client = None
db = None
properties_col = None

try:
    if MONGO_URI and "mongodb" in MONGO_URI:
        client = MongoClient(MONGO_URI)
        db = client[DB_NAME]
        properties_col = db[COLLECTION_NAME]
        print(f"MongoDB Connected Successfully to DB: '{DB_NAME}' & Collection: '{COLLECTION_NAME}'")
    else:
        print("MongoDB URI configurable nahi hai. Scraped data UI mein dikhega par DB mein save nahi hoga.")
except Exception as e:
    print(f"MongoDB Connection Error: {e}")


def get_headless_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36")
    
    # Render cloud ke liye automatic Chrome setup
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    return driver

def scrape_99acres(location_query):
    driver = None
    properties_data = []
    try:
        driver = get_headless_driver()
        formatted_loc = location_query.lower().strip().replace(" ", "-")
        target_url = f"https://www.99acres.com/property-in-{formatted_loc}-ffid"
        
        print(f"Opening URL: {target_url}")
        driver.get(target_url)
        time.sleep(5)

        soup = BeautifulSoup(driver.page_source, 'html.parser')
        cards = soup.find_all('div', class_='tupleNew__tupleWrap')
        if not cards:
            cards = soup.find_all('div', class_='mb-srp__card') or soup.find_all('div', class_='srpTuple__tupleDetails')

        for card in cards:
            try:
                title_elem = card.find('a', class_='tupleNew__propertyHeading') or card.find('h2') or card.find('a', class_='body_med')
                title = title_elem.text.strip() if title_elem else "Property Listing"

                price_elem = card.find('td', id='srp_tuple_price') or card.find('div', class_='tupleNew__price') or card.find('span', class_='configurationCards__cardPrice')
                price = price_elem.text.strip() if price_elem else "Price on Call"

                area_elem = card.find('td', id='srp_tuple_bedroom') or card.find('div', class_='tupleNew__area') or card.find('span', class_='configurationCards__cardArea')
                area = area_elem.text.strip() if area_elem else "N/A"

                dealer_elem = card.find('div', class_='tupleNew__dealerName') or card.find('div', class_='srpTuple__postedBy')
                dealer_name = dealer_elem.text.strip() if dealer_elem else "Owner / Dealer"

                link = title_elem['href'] if title_elem and title_elem.has_attr('href') else "#"
                if link != "#" and not link.startswith("http"):
                    link = "https://www.99acres.com" + link

                item = {
                    "location_searched": location_query,
                    "title": title,
                    "price": price,
                    "area": area,
                    "posted_by": dealer_name,
                    "link": link,
                    "phone_note": "Click Link to View Mobile Number on 99acres",
                    "scraped_at": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
                }
                properties_data.append(item)
            except Exception:
                continue

    except Exception as e:
        print(f"Scraping Error: {e}")
    finally:
        if driver:
            driver.quit()

    # Database Insertion
    if properties_col is not None and properties_data:
        try:
            properties_col.insert_many(properties_data)
            print(f"Success! {len(properties_data)} items MongoDB collection '{COLLECTION_NAME}' mein save ho gaye!")
        except Exception as db_e:
            print(f"DB Insert Error: {db_e}")

    return properties_data

# Frontend HTML UI Template
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="hi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>99acres Real Estate Data Extractor</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
        body { background-color: #f4f7f6; color: #333; padding: 20px; }
        .container { max-width: 900px; margin: 0 auto; background: white; padding: 30px; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.08); }
        h1 { color: #0056b3; margin-bottom: 10px; font-size: 26px; text-align: center; }
        p.subtitle { text-align: center; color: #666; margin-bottom: 25px; font-size: 14px; }
        .search-box { display: flex; gap: 10px; margin-bottom: 25px; }
        input[type="text"] { flex: 1; padding: 14px 18px; border: 2px solid #ddd; border-radius: 8px; font-size: 16px; outline: none; transition: 0.3s; }
        input[type="text"]:focus { border-color: #0056b3; }
        button { padding: 14px 28px; background-color: #0056b3; color: white; border: none; border-radius: 8px; font-size: 16px; font-weight: bold; cursor: pointer; transition: 0.3s; }
        button:hover { background-color: #003d80; }
        .loader { display: none; text-align: center; margin: 20px 0; font-weight: bold; color: #0056b3; }
        .card-list { display: flex; flex-direction: column; gap: 15px; margin-top: 20px; }
        .card { border: 1px solid #e1e8ed; border-radius: 8px; padding: 18px; background: #fafbfc; transition: 0.2s; }
        .card:hover { border-color: #0056b3; box-shadow: 0 2px 8px rgba(0,0,0,0.05); }
        .card-title { font-size: 18px; color: #111; font-weight: bold; margin-bottom: 8px; }
        .card-detail { font-size: 14px; color: #555; margin-bottom: 5px; }
        .price { color: #2e7d32; font-weight: bold; font-size: 16px; }
        .badge { background: #e3f2fd; color: #1565c0; padding: 3px 8px; border-radius: 4px; font-size: 12px; display: inline-block; margin-bottom: 8px; }
        .btn-link { display: inline-block; margin-top: 10px; padding: 8px 14px; background: #25d366; color: white; text-decoration: none; border-radius: 5px; font-size: 13px; font-weight: bold; }
        .btn-link:hover { background: #1eb954; }
        .status-badge { font-size: 12px; background: #fff3cd; color: #856404; padding: 4px 8px; border-radius: 4px; border: 1px solid #ffeeba; margin-top: 6px; display: inline-block; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🏢 99acres Real Estate Data Extractor</h1>
        <p class="subtitle">Location enter karein aur cloud server se real-time property data extract karke MongoDB mein save karein.</p>
        
        <div class="search-box">
            <input type="text" id="locationInput" placeholder="Location (e.g. Noida Sector 62, Indiranagar Bangalore)">
            <button onclick="startScrape()">Search & Save</button>
        </div>

        <div class="loader" id="loader">⏳ Data scraping & Database saving in progress... (10-20 sec wait karein).</div>

        <div id="resultsCount" style="font-weight: bold; margin-bottom: 10px;"></div>
        <div class="card-list" id="results"></div>
    </div>

    <script>
        async function startScrape() {
            const loc = document.getElementById('locationInput').value.trim();
            if(!loc) { alert('Kripya koi location enter karein!'); return; }

            const loader = document.getElementById('loader');
            const resultsDiv = document.getElementById('results');
            const countDiv = document.getElementById('resultsCount');

            loader.style.display = 'block';
            resultsDiv.innerHTML = '';
            countDiv.innerHTML = '';

            try {
                const response = await fetch(`/api/scrape?location=${encodeURIComponent(loc)}`);
                const data = await response.json();

                loader.style.display = 'none';

                if(data.status !== "success" || data.data.length === 0) {
                    resultsDiv.innerHTML = '<p style="text-align:center; color:red;">Data nahi mila ya block ho gaya. Kripya doosri location try karein.</p>';
                    return;
                }

                countDiv.innerText = `Total Extracted & Saved Properties: ${data.data.length}`;

                data.data.forEach(item => {
                    const card = document.createElement('div');
                    card.className = 'card';
                    card.innerHTML = `
                        <span class="badge">📍 ${item.location_searched}</span>
                        <div class="card-title">${item.title}</div>
                        <div class="card-detail">💰 Price: <span class="price">${item.price}</span> | 📐 Area: ${item.area}</div>
                        <div class="card-detail">👤 Posted By: <strong>${item.posted_by}</strong></div>
                        <div class="status-badge">📞 ${item.phone_note}</div><br>
                        <a href="${item.link}" target="_blank" class="btn-link">View Details & Contact Owner ➔</a>
                    `;
                    resultsDiv.appendChild(card);
                });
            } catch (err) {
                loader.style.display = 'none';
                resultsDiv.innerHTML = '<p style="text-align:center; color:red;">Error processing request!</p>';
            }
        }
    </script>
</body>
</html>
"""

@app.route("/")
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route("/api/scrape", methods=["GET"])
def api_scrape():
    location = request.args.get("location", "Noida")
    results = scrape_99acres(location)
    return jsonify({
        "status": "success",
        "count": len(results),
        "data": results
    })

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
        
