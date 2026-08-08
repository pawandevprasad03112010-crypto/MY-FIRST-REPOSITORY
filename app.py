from fastapi import FastAPI, Request, Form, Depends, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from pymongo import MongoClient
import re

app = FastAPI(title="Purple Gold Search Engine")

# Templates Setup
templates = Jinja2Templates(directory="templates")

# ==============================================================================
# 🔗 APNA HOSTED MONGODB CONNECTION DETAILS YAHAN BHAREIN
# ==============================================================================
# Example Atlas URL: "mongodb+srv://<username>:<password>@cluster0.mongodb.net/?retryWrites=true&w=majority"
MONGO_URI = "mongodb+srv://pawandevprasad03112010_db_user:<db_password>@firstmongodb.p45qsrf.mongodb.net/?appName=FIRSTMONGODB"
DB_NAME = "gg" 
COLLECTION_NAME = "txtCities"

client = MongoClient(MONGO_URI)
db = client[DB_NAME]
collection = db[COLLECTION_NAME]
# ==============================================================================

# Dummy Username & Password Login Credentials
USER_CREDENTIALS = {"admin": "12345"}

# --- AUTHENTICATION ROUTES ---

@app.get("/", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login")
async def login(request: Request, username: str = Form(...), password: str = Form(...)):
    if username in USER_CREDENTIALS and USER_CREDENTIALS[username] == password:
        response = RedirectResponse(url="/search-page", status_code=status.HTTP_303_SEE_OTHER)
        response.set_cookie(key="user_session", value=username)
        return response
    else:
        return templates.TemplateResponse("login.html", {
            "request": request, 
            "error": "Galat Username ya Password! Wapas try karein."
        })

@app.get("/search-page", response_class=HTMLResponse)
async def search_page(request: Request):
    user = request.cookies.get("user_session")
    if not user:
        return RedirectResponse(url="/")
    return templates.TemplateResponse("index.html", {"request": request, "user": user})

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

    # Prefix / Word Match Query (Regex)
    regex_pattern = re.compile(re.escape(query), re.IGNORECASE)

    # Aapke database ki fields par dynamic search filter
    search_filter = {
        "$or": [
            {"title": regex_pattern},
            {"category": regex_pattern},
            {"description": regex_pattern},
            {"brand": regex_pattern}
        ]
    }

    # Mongo DB Query execution
    # _id Object को JSON compatible banane ke liye exclude (0) kiya hai
    results = list(collection.find(search_filter, {"_id": 0}).limit(10))
    return JSONResponse(results)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
    
