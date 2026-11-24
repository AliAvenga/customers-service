"""Wishlists, with each product's availability read from the inventory service."""
import os

import httpx
from fastapi import APIRouter
from pydantic import BaseModel

from app.store import customers

INVENTORY_SERVICE_URL = os.environ.get("INVENTORY_SERVICE_URL", "http://localhost:8102").rstrip("/")
router = APIRouter(prefix="/api/customers", tags=["wishlist"])


class WishlistItem(BaseModel):
    product_id: str


@router.get("/wishlist/{customer_id}")
def wishlist(customer_id: str) -> dict:
    items = []
    for product_id in customers.get(customer_id)["wishlist"]:
        stock = httpx.get(f"{INVENTORY_SERVICE_URL}/api/inventory/stock/{product_id}", timeout=5)
        level = stock.json()["level"] if stock.status_code == 200 else "unknown"
        items.append({"product_id": product_id, "availability": level})
    return {"customer_id": customer_id, "items": items}


@router.post("/wishlist/{customer_id}", status_code=201)
def add_to_wishlist(customer_id: str, item: WishlistItem) -> dict:
    return {"customer_id": customer_id, "product_ids": customers.add_to_wishlist(customer_id, item.product_id)}
