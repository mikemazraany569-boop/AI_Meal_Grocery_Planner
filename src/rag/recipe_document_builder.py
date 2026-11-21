
import json
from pathlib import Path


class RecipeDocumentBuilder:
    """Build multilingual RAG documents from Lebanese recipes."""

    def __init__(self, ingredients_path=None):
        project_root = Path(__file__).resolve().parents[2]

        if ingredients_path is None:
            ingredients_path = (
                project_root
                / "data"
                / "ingredients"
                / "ingredients_multilingual.json"
            )

        ingredients_path = Path(ingredients_path)

        if not ingredients_path.exists():
            raise FileNotFoundError(
                f"Ingredient database not found: {ingredients_path}"
            )

        with ingredients_path.open("r", encoding="utf-8") as file:
            data = json.load(file)

        self.ingredients = {
            item["id"]: item
            for item in data["ingredients"]
        }

    @staticmethod
    def merge_overlapping_groups(group_records):
        """
        Merge groups sharing canonical IDs.

        Each record is:
            (ingredient_ids, is_optional)

        All alternative IDs are preserved.
        A merged group is optional only when every contributing
        record is optional.
        """

        if not group_records:
            return [], []

        records = []

        for ingredient_ids, is_optional in group_records:
            ids = list(dict.fromkeys(
                ingredient_id
                for ingredient_id in ingredient_ids
                if ingredient_id
            ))

            if ids:
                records.append((ids, bool(is_optional)))

        if not records:
            return [], []

        parent = list(range(len(records)))

        def find(index):
            while parent[index] != index:
                parent[index] = parent[parent[index]]
                index = parent[index]
            return index

        def union(first, second):
            root_first = find(first)
            root_second = find(second)

            if root_first != root_second:
                parent[root_second] = root_first

        # Merge records sharing at least one canonical ID.
        for i in range(len(records)):
            ids_i = set(records[i][0])

            for j in range(i + 1, len(records)):
                ids_j = set(records[j][0])

                if ids_i.intersection(ids_j):
                    union(i, j)

        merged = {}
        optional_status = {}

        # Preserve original record and ingredient ordering.
        for index, (ingredient_ids, is_optional) in enumerate(records):
            root = find(index)

            if root not in merged:
                merged[root] = []
                optional_status[root] = True

            for ingredient_id in ingredient_ids:
                if ingredient_id not in merged[root]:
                    merged[root].append(ingredient_id)

            # Required takes precedence.
            optional_status[root] = (
                optional_status[root] and is_optional
            )

        groups = list(merged.values())
        optional_flags = [
            optional_status[root]
            for root in merged
        ]

        return groups, optional_flags

    def build_ingredient_groups(self, normalized_ingredients):
        """Build deduplicated groups from normalized ingredient records."""

        group_records = []

        for item in normalized_ingredients:
            if not isinstance(item, dict):
                continue

            group_ids = []

            direct_id = item.get("id")
            if direct_id:
                group_ids.append(direct_id)

            for component in item.get("components", []):
                if isinstance(component, dict):
                    ingredient_id = component.get("id")
                    if ingredient_id:
                        group_ids.append(ingredient_id)

            for alternative in item.get("alternatives", []):
                if isinstance(alternative, dict):
                    ingredient_id = alternative.get("id")
                    if ingredient_id:
                        group_ids.append(ingredient_id)

            group_ids = list(dict.fromkeys(group_ids))

            if group_ids:
                group_records.append((
                    group_ids,
                    item.get("optional", False)
                ))

        groups, _ = self.merge_overlapping_groups(group_records)

        return groups

    def build_document(self, recipe):
        """Convert one Lebanese recipe into a searchable RAG document."""

        recipe_id = recipe.get("id", "UNKNOWN")
        name_en = recipe.get("name_en", "Unknown recipe")
        name_ar = recipe.get("name_ar")

        original_ingredients = recipe.get("ingredients_original", [])
        normalized_ingredients = recipe.get("ingredients_normalized", [])
        detailed_ingredients = recipe.get("ingredients_detailed", [])

        ingredient_ids = []
        group_records = []

        canonical = []
        english = []
        arabic = []
        french = []
        alternative_text = []

        # IDs appearing in at least one non-optional detailed record.
        detailed_required_ids = set()

        # Track detailed-record optionality for each canonical ID.
        detailed_optional_status = {}

        def add_ingredient(candidate):
            """Collect multilingual names and canonical ingredient IDs."""

            if not isinstance(candidate, dict):
                return

            ingredient_id = candidate.get("id")

            if not ingredient_id:
                return

            if ingredient_id not in ingredient_ids:
                ingredient_ids.append(ingredient_id)

            ingredient = self.ingredients.get(ingredient_id)

            if not ingredient:
                return

            names = ingredient.get("names", {})

            languages = [
                (english, "en"),
                (arabic, "ar"),
                (french, "fr"),
            ]

            for target, language in languages:
                for alias in names.get(language, []):
                    if alias not in target:
                        target.append(alias)

            canonical_name = (
                candidate.get("canonical_name")
                or (
                    names.get("en", [None])[0]
                    if names.get("en")
                    else None
                )
            )

            if canonical_name and canonical_name not in canonical:
                canonical.append(canonical_name)

        # Process normalized ingredient records.
        for item in normalized_ingredients:

            if not isinstance(item, dict):
                continue

            candidates = []

            if item.get("id"):
                candidates.append({
                    "id": item["id"],
                    "canonical_name": item.get("canonical_name"),
                })

            candidates.extend(item.get("components", []))
            candidates.extend(item.get("alternatives", []))

            group_ids = []

            for candidate in candidates:
                if not isinstance(candidate, dict):
                    continue

                ingredient_id = candidate.get("id")

                if not ingredient_id:
                    continue

                add_ingredient(candidate)

                if ingredient_id not in group_ids:
                    group_ids.append(ingredient_id)

            if group_ids:
                group_records.append((
                    group_ids,
                    item.get("optional", False)
                ))

            # Preserve alternative ingredient descriptions.
            alternatives = item.get("alternatives", [])

            if alternatives:
                choices = [
                    alternative.get("original", "Unknown")
                    for alternative in alternatives
                    if isinstance(alternative, dict)
                ]

                alternative_text.append(
                    f"{item.get('original', 'Unknown')}: "
                    + " OR ".join(choices)
                )

        # Process detailed records without changing their source data.
        for item in detailed_ingredients:

            if not isinstance(item, dict):
                continue

            ingredient_id = item.get("ingredient_id")

            if not ingredient_id:
                continue

            add_ingredient({
                "id": ingredient_id,
                "canonical_name": item.get("canonical_name")
            })

            is_optional = bool(item.get("optional", False))

            if not is_optional:
                detailed_required_ids.add(ingredient_id)

            if ingredient_id not in detailed_optional_status:
                detailed_optional_status[ingredient_id] = is_optional
            else:
                # If any occurrence is required, the ID is required.
                detailed_optional_status[ingredient_id] = (
                    detailed_optional_status[ingredient_id]
                    and is_optional
                )

        # Merge overlapping normalized groups.
        ingredient_groups, group_optional_flags = (
            self.merge_overlapping_groups(group_records)
        )

        # Add detailed-only IDs not represented in normalized groups.
        represented_ids = {
            ingredient_id
            for group in ingredient_groups
            for ingredient_id in group
        }

        for ingredient_id in ingredient_ids:

            if ingredient_id in represented_ids:
                continue

            is_optional = detailed_optional_status.get(
                ingredient_id, False
            )

            ingredient_groups.append([ingredient_id])
            group_optional_flags.append(is_optional)
            represented_ids.add(ingredient_id)

        # Required detailed records override optional classification.
        required_ingredient_groups = []
        optional_ingredient_groups = []

        for group, is_optional in zip(
            ingredient_groups,
            group_optional_flags
        ):
            has_required_detailed_record = bool(
                set(group).intersection(detailed_required_ids)
            )

            if is_optional and not has_required_detailed_record:
                optional_ingredient_groups.append(group)
            else:
                required_ingredient_groups.append(group)

        # Build detailed ingredient descriptions.
        detailed_text = []

        for item in detailed_ingredients:

            if not isinstance(item, dict):
                continue

            name = item.get("name", "Unknown ingredient")
            quantity = item.get("quantity")
            unit = item.get("unit", "")
            usage = item.get("usage")
            optional = item.get("optional", False)

            description = name

            if quantity is not None:
                description += f" — {quantity} {unit}".strip()

            if usage:
                description += f" ({usage})"

            if optional:
                description += " [Optional]"

            detailed_text.append(description)

        # Format recipe instructions.
        instructions = recipe.get("instructions", [])
        instruction_text = []

        for instruction in instructions:

            if isinstance(instruction, str):
                instruction_text.append(instruction)

            elif isinstance(instruction, dict):
                step_text = (
                    instruction.get("text_en")
                    or instruction.get("text")
                    or instruction.get("instruction")
                    or instruction.get("description")
                )

                if step_text is not None:
                    instruction_text.append(str(step_text))

            else:
                instruction_text.append(str(instruction))

        # Check quantity completeness.
        has_quantity_data = any(
            item.get("quantity") is not None
            for item in detailed_ingredients
            if isinstance(item, dict)
        )

        has_complete_quantities = (
            bool(detailed_ingredients)
            and all(
                isinstance(item, dict)
                and item.get("quantity") is not None
                for item in detailed_ingredients
            )
        )

        # Build searchable document content.
        lines = [
            f"Recipe ID: {recipe_id}",
            f"Recipe name: {name_en}",
            "Cuisine: Lebanese",
            f"English ingredients: {', '.join(english)}",
            f"Arabic ingredients: {', '.join(arabic)}",
            f"French ingredients: {', '.join(french)}",
            f"Canonical ingredients: {', '.join(canonical)}",
            f"Original ingredients: {', '.join(original_ingredients)}",
            f"Detailed ingredients and quantities: {'; '.join(detailed_text)}",
            f"Alternative ingredients: {'; '.join(alternative_text)}",
            f"Instructions: {' '.join(instruction_text)}",
        ]

        if name_ar:
            lines.append(f"Arabic recipe name: {name_ar}")

        if recipe.get("source"):
            lines.append(
                "Sources: "
                + json.dumps(recipe["source"], ensure_ascii=False)
            )

        return {
            "page_content": "\n".join(lines),

            "metadata": {
                "id": recipe_id,
                "name_en": name_en,
                "name_ar": name_ar,
                "cuisine": "Lebanese",
                "source": recipe.get("source"),

                "ingredient_ids": ingredient_ids,
                "ingredient_groups": ingredient_groups,

                "required_ingredient_groups": required_ingredient_groups,
                "optional_ingredient_groups": optional_ingredient_groups,

                "alternative_ingredients": alternative_text,

                "has_quantity_data": has_quantity_data,
                "has_complete_quantities": has_complete_quantities,
                "has_quantities": has_complete_quantities,

                "has_instructions": bool(instruction_text),

                # Preserve the original recipe for the meal planner.
                "recipe": recipe,
            },
        }

    def build_documents(self, recipes):
        """Build RAG documents from a collection of recipes."""

        if not isinstance(recipes, list):
            raise TypeError("recipes must be a list of recipe dictionaries.")

        if not all(isinstance(recipe, dict) for recipe in recipes):
            raise TypeError(
                "Every recipe must be a dictionary."
            )

        return [
            self.build_document(recipe)
            for recipe in recipes
        ]
