
from src.planner.grocery_generator import GroceryGenerator


class WeeklyMealPlanner:
    """
    Generate weekly Lebanese meal plans using inventory,
    recipe retrieval and grocery generation.
    """

    def __init__(
        self,
        recipe_retriever,
        inventory_manager,
        grocery_generator=None
    ):
        self.recipe_retriever = recipe_retriever
        self.inventory_manager = inventory_manager

        self.grocery_generator = (
            grocery_generator or GroceryGenerator()
        )

    @staticmethod
    def _validate_positive_integer(value, name):
        """Validate a positive integer parameter."""

        if (
            not isinstance(value, int)
            or isinstance(value, bool)
            or value < 1
        ):
            raise ValueError(
                f"{name} must be a positive integer."
            )

    def _get_inventory_context(self, expiry_window_days):
        """Collect inventory IDs and ingredients nearing expiry."""

        inventory_ids = self.inventory_manager.get_inventory_ids()

        expiring_ingredients = (
            self.inventory_manager.get_expiring_ingredients(
                within_days=expiry_window_days
            )
        )

        expiring_ids = list(dict.fromkeys(
            item["id"]
            for item in expiring_ingredients
            if item.get("id") is not None
        ))

        inventory_details = (
            self.inventory_manager.get_inventory_details()
        )

        return {
            "inventory_ids": inventory_ids,
            "expiring_ids": expiring_ids,
            "expiring_ingredients": expiring_ingredients,
            "inventory_details": inventory_details,
        }

    @staticmethod
    def _prepare_candidates(search_results):
        """Extract unique, verified Lebanese recipes."""

        candidates = []
        seen_recipe_ids = set()

        for result in search_results:
            metadata = result.get("metadata", {})

            # Only accept explicitly identified Lebanese recipes.
            cuisine = metadata.get("cuisine", "")

            if not isinstance(cuisine, str):
                continue

            if cuisine.strip().casefold() != "lebanese":
                continue

            recipe = metadata.get("recipe")

            if not isinstance(recipe, dict):
                continue

            recipe_id = (
                recipe.get("id")
                or metadata.get("id")
            )

            if not recipe_id or recipe_id in seen_recipe_ids:
                continue

            seen_recipe_ids.add(recipe_id)

            candidates.append({
                "recipe_id": recipe_id,
                "recipe_name": (
                    recipe.get("name_en")
                    or recipe.get("name")
                    or metadata.get("name_en")
                    or "Unknown recipe"
                ),
                "recipe": recipe,
                "score": result.get("score", 0.0),
                "semantic_score": result.get(
                    "semantic_score", 0.0
                ),
                "ingredient_coverage": result.get(
                    "ingredient_coverage", 0.0
                ),
                "expiry_coverage": result.get(
                    "expiry_coverage", 0.0
                ),
                "matched_expiring_groups": result.get(
                    "matched_expiring_groups", 0
                ),
                "missing_required_groups": result.get(
                    "missing_required_groups", []
                ),
            })

        return candidates

    @staticmethod
    def _assign_meals(selected_candidates, days, meals_per_day):
        """Assign selected recipes to daily meal slots."""

        weekly_plan = []
        candidate_index = 0

        for day_number in range(1, days + 1):
            daily_meals = []

            for meal_number in range(1, meals_per_day + 1):

                if candidate_index >= len(selected_candidates):
                    break

                candidate = selected_candidates[candidate_index]

                daily_meals.append({
                    "meal_number": meal_number,
                    **candidate,
                })

                candidate_index += 1

            weekly_plan.append({
                "day": day_number,
                "meals": daily_meals,
            })

        return weekly_plan

    def generate_plan(
        self,
        days=7,
        meals_per_day=1,
        expiry_window_days=3,
        query="Lebanese recipes using available ingredients",
        top_k=None
    ):
        """
        Generate a weekly Lebanese meal plan.

        Args:
            days: Number of days to plan.
            meals_per_day: Number of recipes per day.
            expiry_window_days: Expiry priority window.
            query: Semantic recipe search query.
            top_k: Number of recipe candidates to retrieve.

        Returns:
            Weekly plan, selected recipes, grocery list,
            expiry information and summary.
        """

        # Step 1: Validate parameters.
        self._validate_positive_integer(days, "days")
        self._validate_positive_integer(
            meals_per_day,
            "meals_per_day"
        )

        if (
            not isinstance(expiry_window_days, int)
            or isinstance(expiry_window_days, bool)
            or expiry_window_days < 0
        ):
            raise ValueError(
                "expiry_window_days must be a non-negative integer."
            )

        if not isinstance(query, str) or not query.strip():
            raise ValueError(
                "query must be a non-empty string."
            )

        total_meals = days * meals_per_day

        if top_k is None:
            top_k = max(total_meals * 3, total_meals)
        else:
            self._validate_positive_integer(top_k, "top_k")

        # Step 2: Collect inventory information.
        inventory_context = self._get_inventory_context(
            expiry_window_days
        )

        inventory_ids = inventory_context["inventory_ids"]
        expiring_ids = inventory_context["expiring_ids"]

        # Step 3: Retrieve and rank Lebanese recipes.
        search_results = self.recipe_retriever.search(
            query=query.strip(),
            top_k=top_k,
            ingredient_ids=inventory_ids,
            expiring_ids=expiring_ids
        )

        # Step 4: Extract unique Lebanese recipes.
        candidates = self._prepare_candidates(search_results)

        # Step 5: Select recipes without repetition.
        selected_candidates = candidates[:total_meals]

        # Step 6: Assign recipes to days.
        weekly_plan = self._assign_meals(
            selected_candidates,
            days,
            meals_per_day
        )

        # Step 7: Extract original recipes.
        selected_recipes = [
            candidate["recipe"]
            for candidate in selected_candidates
        ]

        # Step 8: Generate the combined grocery list.
        grocery_result = self.grocery_generator.generate(
            recipes=selected_recipes,
            inventory_details=inventory_context[
                "inventory_details"
            ]
        )

        # Step 9: Prepare summary.
        selected_count = len(selected_candidates)

        summary = {
            "requested_days": days,
            "requested_meals": total_meals,
            "planned_meals": selected_count,
            "unfilled_meals": total_meals - selected_count,
            "unique_recipes": selected_count,
            "expiring_ingredients": len(
                inventory_context["expiring_ingredients"]
            ),
            "shopping_items": grocery_result["summary"][
                "shopping_items"
            ],
            "items_to_review": grocery_result["summary"][
                "items_to_review"
            ],
        }

        warnings = []

        if selected_count < total_meals:
            warnings.append(
                f"Only {selected_count} unique Lebanese recipes "
                f"were available for {total_meals} requested meals."
            )

        if not selected_candidates:
            warnings.append(
                "No eligible Lebanese recipes were found."
            )

        # Step 10: Return the complete weekly plan.
        return {
            "weekly_plan": weekly_plan,
            "selected_recipes": selected_recipes,
            "recipe_details": selected_candidates,
            "grocery": grocery_result,
            "expiring_ingredients": inventory_context[
                "expiring_ingredients"
            ],
            "summary": summary,
            "warnings": warnings,
        }
