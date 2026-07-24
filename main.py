from fastapi import FastAPI, HTTPException, Query
from pymongo import MongoClient
from typing import Optional

app = FastAPI(title="MongoDB Search Engine Backend")

# =========================================================================
# यहाँ अपना MongoDB Atlas का सही URL डालें (पासवर्ड जरूर बदल लें)
# =========================================================================
MONGO_URI = "mongodb://pawandevprasad03112010_db_user:12345@ac-j92zzlx-shard-00-00.p45qsrf.mongodb.net:27017,ac-j92zzlx-shard-00-01.p45qsrf.mongodb.net:27017,ac-j92zzlx-shard-00-02.p45qsrf.mongodb.net:27017/?ssl=true&replicaSet=atlas-rahm0d-shard-0&authSource=admin&appName=FIRSTMONGODB"

# डेटाबेस से कनेक्शन स्थापित करना
try:
    client = MongoClient(MONGO_URI)
    db = client["gg"]               # तुम्हारा डेटाबेस नाम
    collection = db["txtcities"]     # तुम्हारा कलेक्शन नाम
    print("Database se connection safal ho gaya hai!")
except Exception as e:
    print(f"MongoDB connection error: {e}")


# 1. होम रूट - जब कुछ भी सर्च न किया जाए, तो यह खाली डेटा देगा
@app.get("/")
def home():
    return {
        "message": "Kuch bhi search nahi kiya gaya hai.",
        "results": []
    }


# 2. सर्च API - यूजर इनपुट के आधार पर सिमिलर वर्ड्स खोजना
@app.get("/api/search")
def search_database(query: Optional[str] = Query(None, description="User search input")):
    try:
        # अगर यूजर ने कुछ भी इनपुट नहीं दिया है, तो खाली रिजल्ट भेजो
        if not query or query.strip() == "":
            return {
                "query": "",
                "total_results": 0,
                "results": []
            }
        
        # डेटाबेस में यूजर इनपुट से मिलते-जुलते (Similar / Regex) वर्ड्स ढूंढना
        search_filter = {"info_text": {"$regex": query, "$options": "i"}}
        results = list(collection.find(search_filter, {"_id": 0}))
        
        if not results:
            return {
                "query": query,
                "total_results": 0,
                "message": "Aapke input se milta-julta koi data nahi mila.",
                "results": []
            }
        
        return {
            "query": query,
            "total_results": len(results),
            "results": results
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Search karne mein error aayi: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
