"""Signing in (by email, demo accounts only) and customer profiles."""
from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.store import customers, tier

router = APIRouter(prefix="/api/customers", tags=["profiles"])


class SignIn(BaseModel):
    email: str = Field(min_length=3, max_length=120)


def _public(customer: dict) -> dict:
    return {"id": customer["id"], "name": customer["name"], "email": customer["email"]}


@router.post("/sessions")
def sign_in(request: SignIn) -> dict:
    """Demo sign-in: a known email address is enough (no passwords in this demo)."""
    return _public(customers.by_email(request.email))


@router.get("/profiles/{customer_id}")
def profile(customer_id: str) -> dict:
    customer = customers.get(customer_id)
    return {**_public(customer), "tier": tier(customer["points"])}
