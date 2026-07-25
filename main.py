from fastapi import FastAPI, HTTPException, Query
from pymongo import MongoClient
from typing import Optional

app = FastAPI(title="MongoDB Search Engine Backend")

# =========================================================================
# यहाँ अपना MongoDB Atlas का सही URL डालें
# =========================================================================
MONGO_URI = "mongodb://pawandevprasad03112010_db_user:12345@ac-j92zzlx-shard-00-00.p45qsrf.mongodb.net:27017,ac-j92zzlx-shard-00-01.p45qsrf.mongodb.net:27017,ac-j92zzlx-shard-00-02.p45qsrf.mongodb.net:27017/?ssl=true&replicaSet=atlas-rahm0d-shard-0&authSource=admin&appName=FIRSTMONGODB"

# डेटाबेस से कनेक्शन स्थापित करना
try:
    client = MongoClient(MONGO_URI)
    db = client["gg"]               # तुम्हारा डेटाबेस नाम
    collection = db["txtCities"]     # तुम्हारा कलेक्शन नाम
    print("Database se connection safal ho gaya hai!")
except Exception as e:
    print(f"MongoDB connection error: {e}")


# 1. होम रूट
@app.get("/")
def home():
    return {
        "message": "Kuch bhi search nahi kiya gaya hai.",
        "results": []
    }


# 2. नया रूट - डेटाबेस का सारा डेटा देखने के लिए
@app.get("/api/view-all")
def view_all_data():
    try:
        # collection से सारा डेटा निकालना (_id ko chhod kar)
        all_data = list(collection.find({}, {"_id": 0}))
        
        return {
            "total_documents": len(all_data),
            "data": all_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Data fetch karne mein error aayi: {str(e)}")


# 3. सर्च API - यूजर इनपुट के आधार पर सिमिलर वर्ड्स खोजना
@app.get("/api/search")
def search_database(query: Optional[str] = Query(None, description="User search input")):
    try:
        if not query or query.strip() == "":
            return {
                "query": "",
                "total_results": 0,
                "results": []
            }
        
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
