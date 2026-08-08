from fastapi import FastAPI, Request, Form, status
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from pymongo import MongoClient
import re
import os

app = FastAPI(title="Purple Gold Search Engine")

# Templates Setup
templates = Jinja2Templates(directory="templates")

# ==============================================================================
# 🔗 APNA MONGODB ATLAS URL YAHAN BHAREIN
# ==============================================================================
# Render ke Environment Variables me set karein ya direct quote me string daalein
MONGO_URI = os.environ.get("MONGO_URI", "mongodb+srv://pawandevprasad03112010_db_user:12345@firstmongodb.p45qsrf.mongodb.net/?appName=FIRSTMONGODB")

# Aapke Screenshot Ke According Exact Names Set Kiye Gaye Hain:
DB_NAME = "gg"
COLLECTION_NAME = "txtCities"

client = MongoClient(MONGO_URI)
db = client[DB_NAME]
collection = db[COLLECTION_NAME]
# ==============================================================================

USER_CREDENTIALS = {"admin": "12345"}

# --- AUTHENTICATION ROUTES ---

@app.get("/", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse(request=request, name="login.html")

@app.post("/login")
async def login(request: Request, username: str = Form(...), password: str = Form(...)):
    if username in USER_CREDENTIALS and USER_CREDENTIALS[username] == password:
        response = RedirectResponse(url="/search-page", status_code=status.HTTP_303_SEE_OTHER)
        response.set_cookie(key="user_session", value=username)
        return response
    else:
        return templates.TemplateResponse(
            request=request, 
            name="login.html", 
            context={"error": "Galat Username ya Password! Wapas try karein."}
        )

@app.get("/search-page", response_class=HTMLResponse)
async def search_page(request: Request):
    user = request.cookies.get("user_session")
    if not user:
        return RedirectResponse(url="/")
    return templates.TemplateResponse(
        request=request, 
        name="index.html", 
        context={"user": user}
    )

@app.get("/logout")
async def logout():
    response = RedirectResponse(url="/")
    response.delete_cookie("user_session")
    return response

# --- REALTIME AUTOCOMPLETE SEARCH API ---
@app.get("/api/search")
async def api_search(q: str = ""):
    query = q.strip()
    if not query:
        return JSONResponse([])

    regex_pattern = re.compile(re.escape(query), re.IGNORECASE)

    # AAPKE DATABASE FIELDS KE ACCORDING UPDATED SEARCH FILTER:
    search_filter = {
        "$or": [
            {"name": regex_pattern},
            {"city": regex_pattern},
            {"sector": regex_pattern},
            {"location": regex_pattern},
            {"phone_no": regex_pattern}
        ]
    }

    results = list(collection.find(search_filter, {"_id": 0}).limit(15))
    return JSONResponse(results)

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("app:app", host="0.0.0.0", port=port)
    
