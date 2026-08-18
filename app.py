from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import requests
from bs4 import BeautifulSoup
import re
import urllib.parse
import time

app = FastAPI()
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "results": [], "query": ""})

@app.post("/", response_class=HTMLResponse)
def search_pgs(request: Request, query: str = Form(...)):
    user_input = query.strip()
    if not user_input:
        user_input = "Sector 90 Gurgaon"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9,hi;q=0.8"
    }

    seen_phones = set()
    pg_list = []

    for page in range(1, 4):
        search_query = f"PG hostel contact number {user_input}"
        url = f"https://html.duckduckgo.com/html/?q={urllib.parse.quote(search_query)}&s={(page-1)*30}"
        
        try:
            response = requests.post(url, data={'q': search_query}, headers=headers, timeout=8)
            if response.status_code != 200:
                continue

            soup = BeautifulSoup(response.text, 'html.parser')
            results = soup.find_all('div', class_='result__body')

            for result in results:
                text = result.get_text(separator=' ')
                phone_matches = re.findall(r'(?:\+91[\-\s]?)?[6-9]\d{9}', text)
                
                for phone in phone_matches:
                    clean_phone = phone.replace("+91", "").replace("-", "").replace(" ", "").strip()
                    if clean_phone.startswith("0"):
                        clean_phone = clean_phone[1:]
                        
                    if clean_phone not in seen_phones and len(clean_phone) == 10:
                        seen_phones.add(clean_phone)
                        
                        title_elem = result.find('h2', class_='result__title')
                        name = title_elem.get_text().strip() if title_elem else "PG Residency"
                        name = re.sub(r'(?i)(contact|number|phone|details|kolkata|gurgaon|sector).*', '', name).strip()
                        if not name:
                            name = "PG Accommodation"
                        
                        pg_data = f"Name = {name[:45]}\nPhone number = {clean_phone}\nRent = sin= dou= tri= fou="
                        pg_list.append(pg_data)
                        
        except Exception:
            continue
        time.sleep(0.5)

    return templates.TemplateResponse("index.html", {
        "request": request, 
        "results": pg_list, 
        "query": user_input
    })
    
