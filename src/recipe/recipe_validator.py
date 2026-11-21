
class RecipeValidator:
    """Validate the structure and completeness of Lebanese recipe records."""

    REQUIRED_FIELDS = ["id", "name_en", "ingredients_original"]

    def validate(
        self,
        recipes,
        valid_ingredient_ids=None,
        ingredient_database=None,
    ):
        errors = []
        warnings = []
        seen_ids = set()

        if not isinstance(recipes, list):
            return {
                "valid": False,
                "total_recipes": 0,
                "errors": ["Recipes must be provided as a list."],
                "warnings": [],
            }

        # Build an ingredient lookup when full database records are supplied.
        ingredient_lookup = {}

        if isinstance(ingredient_database, list):
            ingredient_lookup = {
                item["id"]: item
                for item in ingredient_database
                if isinstance(item, dict) and item.get("id")
            }

        elif isinstance(ingredient_database, dict):
            ingredient_lookup = ingredient_database

        # Combine IDs from both validation inputs.
        known_ids = set(valid_ingredient_ids or [])
        known_ids.update(ingredient_lookup.keys())

        def check_mapping(recipe_id, ingredient_id, canonical_name, location):
            """Check an ingredient ID and its canonical name."""

            if not ingredient_id:
                warnings.append(
                    f"{recipe_id}: missing ingredient ID at {location}."
                )
                return

            if known_ids and ingredient_id not in known_ids:
                errors.append(
                    f"{recipe_id}: unknown ingredient ID "
                    f"'{ingredient_id}' at {location}."
                )
                return

            if ingredient_lookup:
                record = ingredient_lookup.get(ingredient_id)

                if record is None:
                    errors.append(
                        f"{recipe_id}: ingredient '{ingredient_id}' "
                        "is missing from the ingredient database."
                    )
                    return

                names = record.get("names", {})
                english_names = names.get("en", [])

                expected_name = (
                    english_names[0] if english_names else None
                )

                if (
                    canonical_name
                    and expected_name
                    and canonical_name != expected_name
                ):
                    errors.append(
                        f"{recipe_id}: canonical name mismatch for "
                        f"{ingredient_id} at {location}. "
                        f"Expected '{expected_name}', "
                        f"got '{canonical_name}'."
                    )

                elif not canonical_name:
                    warnings.append(
                        f"{recipe_id}: missing canonical name for "
                        f"'{ingredient_id}' at {location}."
                    )

        for index, recipe in enumerate(recipes):
            label = f"Recipe at index {index}"

            if not isinstance(recipe, dict):
                errors.append(f"{label}: must be a dictionary.")
                continue

            recipe_id = recipe.get("id") or label

            # 1. Required fields
            for field in self.REQUIRED_FIELDS:
                if not recipe.get(field):
                    errors.append(
                        f"{recipe_id}: missing '{field}'."
                    )

            # 2. Unique recipe IDs
            if recipe.get("id"):
                if recipe_id in seen_ids:
                    errors.append(
                        f"{recipe_id}: duplicate recipe ID."
                    )
                seen_ids.add(recipe_id)

            # 3. Original ingredients
            original = recipe.get("ingredients_original")

            if not isinstance(original, list):
                errors.append(
                    f"{recipe_id}: ingredients_original must be a list."
                )
            elif not original:
                warnings.append(
                    f"{recipe_id}: no original ingredients."
                )

            # 4. Instructions
            instructions = recipe.get("instructions")

            if not isinstance(instructions, list) or not instructions:
                warnings.append(
                    f"{recipe_id}: instructions are missing or invalid."
                )

            # 5. Detailed ingredients
            detailed = recipe.get("ingredients_detailed")

            if not isinstance(detailed, list) or not detailed:
                warnings.append(
                    f"{recipe_id}: detailed ingredients are missing."
                )
            else:
                normalized_records = recipe.get(
                    "ingredients_normalized", []
                )

                # A detailed ingredient can omit its direct ID when its
                # normalized record represents two or more alternatives.
                alternative_names = {
                    str(item.get("original", "")).strip().casefold()
                    for item in normalized_records
                    if isinstance(item, dict)
                    and isinstance(item.get("alternatives"), list)
                    and len(item["alternatives"]) >= 2
                }

                for item_index, item in enumerate(detailed):
                    location = f"ingredients_detailed[{item_index}]"

                    if not isinstance(item, dict):
                        errors.append(
                            f"{recipe_id}: {location} must be a dictionary."
                        )
                        continue

                    ingredient_name = item.get("name")

                    if not ingredient_name:
                        warnings.append(
                            f"{recipe_id}: ingredient name missing at "
                            f"{location}."
                        )

                    ingredient_id = item.get("ingredient_id")

                    if ingredient_id is None:
                        normalized_name = str(
                            ingredient_name or ""
                        ).strip().casefold()

                        if normalized_name not in alternative_names:
                            check_mapping(
                                recipe_id,
                                ingredient_id,
                                item.get("canonical_name"),
                                location,
                            )
                    else:
                        check_mapping(
                            recipe_id,
                            ingredient_id,
                            item.get("canonical_name"),
                            location,
                        )

            # 6. Normalized ingredients
            normalized = recipe.get("ingredients_normalized")

            if not isinstance(normalized, list):
                errors.append(
                    f"{recipe_id}: ingredients_normalized must be a list."
                )
                continue

            for item_index, item in enumerate(normalized):
                location = f"ingredients_normalized[{item_index}]"

                if not isinstance(item, dict):
                    errors.append(
                        f"{recipe_id}: {location} must be a dictionary."
                    )
                    continue

                components = item.get("components", [])
                alternatives = item.get("alternatives", [])

                if not isinstance(components, list):
                    errors.append(
                        f"{recipe_id}: components must be a list."
                    )
                    continue

                if not isinstance(alternatives, list):
                    errors.append(
                        f"{recipe_id}: alternatives must be a list."
                    )
                    continue

                # Check ordinary ingredient components.
                for component_index, component in enumerate(components):
                    component_location = (
                        f"{location}.components[{component_index}]"
                    )

                    if not isinstance(component, dict):
                        errors.append(
                            f"{recipe_id}: {component_location} "
                            "must be a dictionary."
                        )
                        continue

                    check_mapping(
                        recipe_id,
                        component.get("id"),
                        component.get("canonical_name"),
                        component_location,
                    )

                # Check alternative candidates individually.
                for alternative_index, alternative in enumerate(alternatives):
                    alternative_location = (
                        f"{location}.alternatives[{alternative_index}]"
                    )

                    if not isinstance(alternative, dict):
                        errors.append(
                            f"{recipe_id}: {alternative_location} "
                            "must be a dictionary."
                        )
                        continue

                    check_mapping(
                        recipe_id,
                        alternative.get("id"),
                        alternative.get("canonical_name"),
                        alternative_location,
                    )

                # An unresolved alternative requires human review.
                if item.get("status") == "needs_review":
                    warnings.append(
                        f"{recipe_id}: ingredient '{item.get('original', 'unknown')}' "
                        "requires review."
                    )

        # 7. Source validation
        for recipe in recipes:
            if not isinstance(recipe, dict):
                continue

            recipe_id = recipe.get("id", "Unknown recipe")
            sources = recipe.get("source")

            if not isinstance(sources, list) or not sources:
                warnings.append(
                    f"{recipe_id}: source information is missing or invalid."
                )
                continue

            for source_index, source in enumerate(sources):
                if not isinstance(source, dict):
                    errors.append(
                        f"{recipe_id}: source at index {source_index} "
                        "must be a dictionary."
                    )
                    continue

                if not source.get("name"):
                    warnings.append(
                        f"{recipe_id}: source name is missing."
                    )

                url = source.get("url")

                if not isinstance(url, str) or not url.startswith(
                    ("https://", "http://")
                ):
                    warnings.append(
                        f"{recipe_id}: source at index {source_index} "
                        "has a missing or invalid URL."
                    )

                if not source.get("source_type"):
                    warnings.append(
                        f"{recipe_id}: source type is missing."
                    )

        return {
            "valid": len(errors) == 0,
            "total_recipes": len(recipes),
            "errors": errors,
            "warnings": warnings,
        }
