"""Customers service of the demo shop: sign-in, profiles, loyalty points and wishlists."""
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.routes import loyalty, profiles, wishlist
from app.store import CustomerError, customers

app = FastAPI(title="Customers service", version="0.1.0")
for module in (profiles, loyalty, wishlist):
    app.include_router(module.router)


@app.exception_handler(CustomerError)
def customer_error(_: Request, error: CustomerError) -> JSONResponse:
    return JSONResponse(status_code=error.status, content={"error": error.code, "message": error.message})


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "service": "customers-service"}


@app.post("/api/customers/test/reset", status_code=204)
def reset() -> None:
    """Back to the seeded customers, so every test starts from the same points and wishlists."""
    customers.reset()
