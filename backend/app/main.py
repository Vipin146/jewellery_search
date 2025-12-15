# backend/app/main.py
from fastapi import FastAPI, Query
from app.services.data_loader import DataLoader
from app.services.search_engine import SearchEngine
from app.config import settings

app = FastAPI(title="Manual Search Engine")

# Load data
loader = DataLoader(settings.PRODUCTS_PATH)
df = loader.load()
engine = SearchEngine(df)

@app.get("/health")
def health():
    return {"status": "ok", "total_products": len(df)}

@app.get("/autocomplete")
def autocomplete(q: str = Query(..., min_length=1), limit: int = 8):
    return engine.autocomplete(q, top_n=limit)

@app.get("/search")
def search(
    q: str = Query(..., min_length=1),
    limit: int = 10,
    weight: float | None = None
):
    results = engine.search_products(q, top_n=limit, weight_pref=weight)

    out = []
    for _, r in results.iterrows():
        out.append({
            "product_id": r['jbo_own_products_id'],
            "tag_label": r['tag_label'],
            "category": r['categoty_name'],
            "subitem": r['subitem_name'],
            "metal_category_name": r['metal_category_name'],
            "gender": r['gender'],
            "weight": r['product_weight'],
            "thumbnail": r['image'],
            "url": r['URL'],
        })

    return {
        "query": q,
        "reason": results.attrs.get('reason'),
        "results": out,
        "count": len(out)
    }

@app.get("/debug/explain")
def explain(q: str, index: int):
    return engine.explain(q, index)
