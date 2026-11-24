"""In-memory customers, loyalty points and wishlists for the demo. Reset with POST /api/customers/test/reset."""
from __future__ import annotations

import threading
from copy import deepcopy
from decimal import Decimal
from typing import Any

POINTS_PER_EURO = 1
TIERS = ((500, "gold"), (200, "silver"), (0, "bronze"))

_SEED: dict[str, dict[str, Any]] = {
    "C-1": {"id": "C-1", "name": "Ana Silva", "email": "ana@example.com", "points": 120, "wishlist": ["P-300"]},
    "C-2": {"id": "C-2", "name": "Ben Okafor", "email": "ben@example.com", "points": 480, "wishlist": []},
}


class CustomerError(Exception):
    def __init__(self, status: int, code: str, message: str) -> None:
        super().__init__(message)
        self.status, self.code, self.message = status, code, message


def tier(points: int) -> str:
    return next(name for floor, name in TIERS if points >= floor)


class Customers:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self.reset()

    def reset(self) -> None:
        with self._lock:
            self.customers = deepcopy(_SEED)
            self.awarded: set[str] = set()  # order references that already earned points

    def get(self, customer_id: str) -> dict[str, Any]:
        found = self.customers.get(customer_id)
        if found is None:
            raise CustomerError(404, "customer_not_found", f"Customer {customer_id} does not exist.")
        return found

    def by_email(self, email: str) -> dict[str, Any]:
        found = next((item for item in self.customers.values() if item["email"] == email.strip().lower()), None)
        if found is None:
            raise CustomerError(404, "customer_not_found", "No customer has this email address.")
        return found

    def award(self, customer_id: str, order_ref: str, amount: Decimal) -> dict[str, Any]:
        """Points for an order, once per order reference."""
        with self._lock:
            customer = self.get(customer_id)
            if order_ref in self.awarded:
                raise CustomerError(409, "already_awarded", f"Order {order_ref} already earned points.")
            earned = int(amount) * POINTS_PER_EURO
            customer["points"] += earned
            self.awarded.add(order_ref)
            return {"customer_id": customer_id, "earned": earned, "points": customer["points"],
                    "tier": tier(customer["points"])}

    def add_to_wishlist(self, customer_id: str, product_id: str) -> list[str]:
        with self._lock:
            customer = self.get(customer_id)
            if product_id not in customer["wishlist"]:
                customer["wishlist"].append(product_id)
            return customer["wishlist"]


customers = Customers()
