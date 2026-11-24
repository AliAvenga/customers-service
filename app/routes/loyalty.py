"""Loyalty points: 1 point per euro of an order; tiers bronze, silver (200) and gold (500)."""
from decimal import Decimal

from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.store import customers, tier

router = APIRouter(prefix="/api/customers", tags=["loyalty"])


class Award(BaseModel):
    order_ref: str = Field(min_length=1, max_length=40)
    amount: Decimal = Field(gt=0, max_digits=10, decimal_places=2)


@router.get("/loyalty/{customer_id}")
def balance(customer_id: str) -> dict:
    customer = customers.get(customer_id)
    return {"customer_id": customer_id, "points": customer["points"], "tier": tier(customer["points"])}


@router.post("/loyalty/{customer_id}/awards", status_code=201)
def award(customer_id: str, request: Award) -> dict:
    """409 `already_awarded` when the same order is sent twice."""
    return customers.award(customer_id, request.order_ref, request.amount)
