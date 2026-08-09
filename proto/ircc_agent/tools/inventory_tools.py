
from __future__ import print_function
from ircc_agent.utils import _execute_read_query
from ircc_agent.utils.db_helper import _execute_fetchall_query
from typing import Any

def find_alternative_products(sku: str, required_quantity: int, max_results: int = 3) -> dict[str, Any]:
    """
    Finds in-stock alternative products similar to the given SKU based on
    category and tags.

    In production queries a vector similarity search index
    (e.g., Vertex AI Matching Engine, PostgreSQL pgvector) on product embeddings.

    Args:
        sku:         The out-of-stock SKU to find alternatives for.
        max_results: Maximum number of alternatives to return.

    Returns:
        dict with key 'alternatives': list of matching in-stock products
    """

    original_product = _execute_read_query(
        query="SELECT * FROM products WHERE sku = ?",
        params=[sku]
    )

    if not original_product:
        return {"status": "error", "message": f"Given product SKU '{sku}' is invalid."}

    products = _execute_fetchall_query(
        query="""
        SELECT * FROM products WHERE inventory_quantity >= ? AND category = ? AND sku != ?
        """,
        params=[required_quantity, original_product["category"], sku]
    )
    if not products:
        return {"status": "error", "message": f"No in-stock alternative SKU found for '{sku}'."}


    alternatives = []
    for candidate in products:
        score = 0
        original_tags_set = set(tag.strip() for tag in original_product["tags"].split(","))
        candidate_tags_set = set(tag.strip() for tag in candidate["tags"].split(","))
        score += len(candidate_tags_set & original_tags_set)

        if score > 0:
            alternatives.append({
                "sku": candidate["sku"],
                "name": candidate["name"],
                "price": candidate["price"],
                "vendor_name": candidate["vendor_name"],
                "category": candidate["category"],
                "tags": candidate["tags"],
                "in_stock_quantity": candidate.get("inventory_quantity", 0),
                "relevance_score": score
            })

    alternatives.sort(key=lambda x: x["relevance_score"], reverse=True)
    #print(f"The alternatives are: {alternatives}");

    return {
        "status": "success",
        "original_sku": sku,
        "original_name": original_product["name"],
        "alternatives": alternatives[:max_results],
    }