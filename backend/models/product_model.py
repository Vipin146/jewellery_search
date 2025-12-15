# backend/app/models/product_model.py
from pydantic import BaseModel
from typing import Optional

class ProductOut(BaseModel):
    product_id: Optional[str]
    tag_label: Optional[str]
    category: Optional[str]
    subitem: Optional[str]
    metal_category_name: Optional[str]
    gender: Optional[str]
    weight: Optional[str]
    thumbnail: Optional[str]
    url: Optional[str]
