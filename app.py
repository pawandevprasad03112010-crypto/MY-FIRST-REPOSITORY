import os
import time
from flask import Flask, request, jsonify
from flask_cors import CORS
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

app = Flask(__name__)
CORS(app) # Frontend fetch calls allow karne ke liye

def get_headless_driver():
    options = webdriver.ChromeOptions()
    # Cloud environments (Render/Linux) ke liye essential flags
    options.add_argument('--headless=new')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36')
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    return driver

@app.route('/api/search', methods=['GET'])
def search_properties():
    location = request.args.get('location')
    if not location:
        return jsonify({'error': 'Location parameter is required'}), 400

    driver = get_headless_driver()
    properties_list = []

    try:
        # Step 1: Target Page Open Karna
        driver.get("https://www.99acres.com")
        time.sleep(3)

        # Step 2: Search Bar Location Handle Karna
        search_box = driver.find_element(By.XPATH, '//input[@type="text" or @placeholder="Search..."]')
        search_box.clear()
        search_box.send_keys(location)
        time.sleep(2)
        search_box.send_keys(Keys.ENTER)
        time.sleep(5)

        # Step 3: Elements & Photos Extract Karna
        cards = driver.find_elements(By.XPATH, '//div[contains(@class, "srpTuple__tupleDetails")]')

        for card in cards:
            try:
                title = card.find_element(By.XPATH, './/h2 | .//a[contains(@class, "srpTuple__propertyName")]').text
            except:
                title = "N/A"

            try:
                price = card.find_element(By.XPATH, './/td[contains(@id, "srp_tuple_price")] | .//span[contains(@class, "srpTuple__price")]').text
            except:
                price = "N/A"

            try:
                area_loc = card.find_element(By.XPATH, './/section[contains(@class, "srpTuple__tupleTitle")]').text
            except:
                area_loc = "N/A"

            try:
                url = card.find_element(By.XPATH, './/a').get_attribute('href')
            except:
                url = "N/A"

            try:
                # Property Image URL fetch karna
                img_element = card.find_element(By.XPATH, './/img')
                image_url = img_element.get_attribute('src')
            except:
                image_url = "https://via.placeholder.com/300x200"

            properties_list.append({
                'title': title,
                'price': price,
                'location': area_loc,
                'url': url,
                'imageUrl': image_url
            })

    except Exception as e:
        print(f"Error during execution: {e}")
    finally:
        driver.quit()

    return jsonify(properties_list)

if __name__ == '__main__':
    # Render Dynamic Port allocate karta hai
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
    
