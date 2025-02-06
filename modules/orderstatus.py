from fastapi import APIRouter, HTTPException
import requests
import os
from typing import Optional

router = APIRouter()

# Shopify API credentials (Replace with actual credentials)
SHOPIFY_STORE_URL = "https://yourstore.myshopify.com/admin/api/2023-01"
SHOPIFY_ACCESS_TOKEN = os.getenv("SHOPIFY_ACCESS_TOKEN")

headers = {
    "X-Shopify-Access-Token": SHOPIFY_ACCESS_TOKEN,
    "Content-Type": "application/json"
}

@router.get("/orderstatus")
def get_order_status(order_id: Optional[str] = None, email: Optional[str] = None):
    if not order_id and not email:
        raise HTTPException(status_code=400, detail="Provide either an order ID or an email")

    if order_id:
        url = f"{SHOPIFY_STORE_URL}/orders/{order_id}.json"
    elif email:
        url = f"{SHOPIFY_STORE_URL}/orders.json?email={email}"

    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Failed to retrieve order details")
    
    data = response.json()
    orders = data.get("orders", []) if email else [data.get("order")]
    
    if not orders:
        raise HTTPException(status_code=404, detail="No orders found")
    
    order_info = []
    for order in orders:
        order_info.append({
            "order_id": order["id"],
            "email": order["email"],
            "status": order["financial_status"],
            "fulfillment_status": order["fulfillment_status"],
            "tracking": order["fulfillments"][0]["tracking_url"] if order["fulfillments"] else None
        })
    
    return {"orders": order_info}
