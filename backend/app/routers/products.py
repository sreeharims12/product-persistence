from typing import List
from fastapi import APIRouter, Query
from app.services.product_search import search_products
from app.schemas.product import ProductResult

router = APIRouter()


@router.get("/search", response_model=List[ProductResult])
def search(q: str = Query(..., min_length=1, description="Product name to search for")):
    """
    Search for products across all registered providers.
    Returns a list of product results with price, stock, and rating data.
    """
    results = search_products(q)
    return [
        ProductResult(
            product_name=r.product_name,
            store_name=r.store_name,
            price=r.price,
            currency=r.currency,
            in_stock=r.in_stock,
            rating=r.rating,
            review_count=r.review_count,
            image_url=r.image_url,
            product_url=r.product_url,
        )
        for r in results
    ]
