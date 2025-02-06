from fastapi import APIRouter, HTTPException
from typing import Dict, List

router = APIRouter()

# In-memory cart storage (Replace with database or Shopify cart API later)
cart = {}

from modules.products import PRODUCTS  # Import product data

@router.post("/cart/add")
def add_to_cart(product_id: int, quantity: int = 1):
    """Adds a product to the cart."""
    product = next(
        (p for category in PRODUCTS.values() for p in category if p["id"] == product_id), None
    )

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    if product["stock"] < quantity:
        raise HTTPException(status_code=400, detail="Not enough stock available")

    # Add/update cart
    if product_id in cart:
        cart[product_id]["quantity"] += quantity
    else:
        cart[product_id] = {
            "name": product["name"],
            "price": product["price"],
            "quantity": quantity,
        }

    return {"message": f"Added {quantity}x {product['name']} to cart.", "cart": cart}

@router.get("/cart/view")
def view_cart() -> Dict:
    """Returns the current cart contents."""
    if not cart:
        return {"message": "Your cart is empty."}

    total_price = sum(item["price"] * item["quantity"] for item in cart.values())
    return {"cart": cart, "total_price": f"${total_price:.2f}"}

@router.post("/cart/remove")
def remove_from_cart(product_id: int):
    """Removes a product from the cart."""
    if product_id not in cart:
        raise HTTPException(status_code=404, detail="Product not in cart")

    del cart[product_id]
    return {"message": "Product removed from cart.", "cart": cart}

