from typing import List, Dict, Any, Optional
from app.models.product import ProductSnapshot

PRICE_CHANGE_THRESHOLD = 0.01  # 1% minimum to count as a change


def detect_changes(
    old_snapshots: List[ProductSnapshot],
    new_products: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """
    Compare latest stored snapshots with freshly fetched product data.
    Returns a list of change dictionaries ready for notification generation.
    """
    changes: List[Dict[str, Any]] = []

    old_by_store: Dict[str, ProductSnapshot] = {s.store_name: s for s in old_snapshots}
    new_by_store: Dict[str, Dict] = {p["store_name"]: p for p in new_products}

    # Check changes for stores we've seen before
    for store_name, new in new_by_store.items():
        old = old_by_store.get(store_name)

        if old is None:
            # Brand-new store appearing in results
            changes.append({
                "type": "new_seller",
                "store": store_name,
                "new_price": new.get("price"),
                "in_stock": new.get("in_stock", True),
                "message": (
                    f"New seller available: {store_name} now carries this product"
                    + (f" for ${new['price']:.2f}" if new.get("price") else "")
                ),
            })
            continue

        # ── Price change detection ───────────────────────────────────────────
        old_price: Optional[float] = old.price
        new_price: Optional[float] = new.get("price")

        if old_price and new_price:
            pct_change = (new_price - old_price) / old_price

            if pct_change <= -PRICE_CHANGE_THRESHOLD:
                savings = old_price - new_price
                changes.append({
                    "type": "price_drop",
                    "store": store_name,
                    "old_price": old_price,
                    "new_price": new_price,
                    "change_pct": round(pct_change * 100, 2),
                    "message": (
                        f"💰 Price drop on {store_name}! "
                        f"${old_price:.2f} → ${new_price:.2f} "
                        f"(save ${savings:.2f}, {abs(pct_change)*100:.1f}% off)"
                    ),
                })
            elif pct_change >= PRICE_CHANGE_THRESHOLD:
                changes.append({
                    "type": "price_increase",
                    "store": store_name,
                    "old_price": old_price,
                    "new_price": new_price,
                    "change_pct": round(pct_change * 100, 2),
                    "message": (
                        f"📈 Price increased on {store_name}: "
                        f"${old_price:.2f} → ${new_price:.2f} "
                        f"({pct_change*100:.1f}% increase)"
                    ),
                })

        # ── Stock status change ──────────────────────────────────────────────
        was_in_stock = old.in_stock
        now_in_stock = new.get("in_stock", True)

        if not was_in_stock and now_in_stock:
            changes.append({
                "type": "restock",
                "store": store_name,
                "new_price": new_price,
                "message": (
                    f"✅ Back in stock on {store_name}!"
                    + (f" Current price: ${new_price:.2f}" if new_price else "")
                ),
            })
        elif was_in_stock and not now_in_stock:
            changes.append({
                "type": "out_of_stock",
                "store": store_name,
                "message": f"❌ Now out of stock on {store_name}",
            })

    return changes
