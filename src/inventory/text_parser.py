
class TextInventoryParser:

    @staticmethod
    def parse_ingredients(text):
        """
        Convert a user's text input into a clean list of ingredients.
        Supports English, Arabic, and French separators.
        """

        if not isinstance(text, str) or not text.strip():
            return []

        # Replace Arabic comma with English comma
        text = text.replace("،", ",")

        # Split ingredients
        ingredients = text.split(",")

        # Clean and remove empty or duplicate items
        cleaned_ingredients = []
        seen = set()

        for ingredient in ingredients:
            ingredient = ingredient.strip()

            if ingredient:
                key = ingredient.casefold()

                if key not in seen:
                    cleaned_ingredients.append(ingredient)
                    seen.add(key)

        return cleaned_ingredients
