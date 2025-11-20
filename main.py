import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List

from database import db, create_document, get_documents
from schemas import AuditRequest, Article

app = FastAPI(title="Squeeze Marketing Brokerage API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Squeeze Marketing Brokerage Backend running"}

@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }
    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
            response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
                response["connection_status"] = "Connected"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:80]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:80]}"
    return response

# -------------------------------------------------------------
# Lead capture: Marketing Governance Audit
# -------------------------------------------------------------

@app.post("/api/audit", status_code=201)
def create_audit(request: AuditRequest):
    try:
        inserted_id = create_document("auditrequest", request)
        return {"ok": True, "id": inserted_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# -------------------------------------------------------------
# Knowledge Hub (simple CMS endpoints)
# -------------------------------------------------------------

class ArticleCreate(BaseModel):
    title: str
    summary: str
    content: str
    author: str
    tags: List[str] = []
    published: bool = False

@app.get("/api/articles")
def list_articles(published: bool = True):
    try:
        filt = {"published": published} if published else {}
        docs = get_documents("article", filt, limit=50)
        # Normalize ObjectId and dates for JSON
        for d in docs:
            d["id"] = str(d.pop("_id", ""))
            if "published_at" in d and d["published_at"]:
                d["published_at"] = str(d["published_at"])  # ISO-like
            if "created_at" in d:
                d["created_at"] = str(d["created_at"])
        return {"items": docs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/articles", status_code=201)
def create_article(payload: ArticleCreate):
    try:
        from slugify import slugify  # optional helper
    except Exception:
        def slugify(s: str):
            return s.lower().strip().replace(" ", "-")
    try:
        article = Article(
            title=payload.title,
            slug=slugify(payload.title),
            summary=payload.summary,
            content=payload.content,
            author=payload.author,
            tags=payload.tags,
            published=payload.published,
            published_at=None,
        )
        inserted_id = create_document("article", article)
        return {"ok": True, "id": inserted_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
