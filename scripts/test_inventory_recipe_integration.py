
import sys
from pathlib import Path
from datetime import date, timedelta

# 1. Configure project path BEFORE importing src
PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# 2. Import project modules
from src.inventory.inventory_manager import InventoryManager
from src.rag.recipe_retriever import RecipeRetriever
from src.rag.recipe_index_manager import RecipeIndexManager


def main():

    # 3. Create inventory
    inventory = InventoryManager()

    today = date.today()

    ingredients = [
        ("eggplant", 2, "pieces", (today + timedelta(days=1)).isoformat()),
        ("tahini", 100, "grams", (today + timedelta(days=30)).isoformat()),
        ("lemon", 3, "pieces", today.isoformat()),
        ("garlic", 5, "cloves", None),
        ("salt", 1, "teaspoon", None),
        ("olive oil", 100, "ml", None)
    ]

    # 4. Add ingredients
    print("ADDING INGREDIENTS")
    for name, quantity, unit, expiry_date in ingredients:

        success = inventory.add_ingredient(
            name,
            quantity=quantity,
            unit=unit,
            expiry_date=expiry_date
        )

        print(f"{name}: {'Added' if success else 'Not added'}")

    # 5. Display inventory
    print("\nINVENTORY DETAILS")

    for item in inventory.get_inventory_details():
        print(item)

    # 6. Extract canonical ingredient IDs
    inventory_ids = inventory.get_inventory_ids()

    print("\nINVENTORY INGREDIENT IDs")
    print(inventory_ids)

    # 7. Detect ingredients expiring within 3 days
    expiring_ingredients = inventory.get_expiring_ingredients(
        within_days=3
    )

    expiring_ids = [
        item["id"]
        for item in expiring_ingredients
        if item["id"] is not None
    ]

    print("\nINGREDIENTS EXPIRING WITHIN 3 DAYS")

    for item in expiring_ingredients:
        print(item)

    print("\nEXPIRING INGREDIENT IDs")
    print(expiring_ids)

    # 8. Load saved recipe index
    retriever = RecipeRetriever()
    manager = RecipeIndexManager()

    print("\nLOADING SAVED RECIPE INDEX")
    print(manager.load(retriever))

    # 9. Search using inventory and expiry information
    results = retriever.search(
        query="Lebanese recipes using my available ingredients",
        top_k=5,
        ingredient_ids=inventory_ids,
        expiring_ids=expiring_ids
    )

    # 10. Display recipe recommendations
    print("\nEXPIRY-AWARE LEBANESE RECIPE RESULTS")
    print("=" * 55)

    for result in results:

        metadata = result["metadata"]

        print(f"\n{metadata['id']} - {metadata['name_en']}")

        print(f"Combined score: {result['score']:.4f}")
        print(f"Semantic score: {result['semantic_score']:.4f}")

        print(
            f"Required coverage: "
            f"{result['ingredient_coverage']:.2%}"
        )

        print(
            f"Expiry coverage: "
            f"{result['expiry_coverage']:.2%}"
        )

        print(
            f"Matched expiring groups: "
            f"{result['matched_expiring_groups']}"
        )

        print(
            f"Missing required groups: "
            f"{result['missing_required_groups']}"
        )

    print("\nEXPIRY-AWARE INTEGRATION COMPLETED")


if __name__ == "__main__":
    main()
