
import json
import unicodedata
from pathlib import Path


class IngredientNormalizer:

    def __init__(self):
        # Locate project root.
        project_root = Path(__file__).resolve().parents[2]

        data_path = (
            project_root
            / "data"
            / "ingredients"
            / "ingredients_multilingual.json"
        )

        if not data_path.exists():
            raise FileNotFoundError(
                f"Ingredient database not found: {data_path}"
            )

        with data_path.open("r", encoding="utf-8") as file:
            data = json.load(file)

        self.ingredients = data.get("ingredients", [])

        if not isinstance(self.ingredients, list):
            raise ValueError(
                "The JSON file must contain an ingredients list."
            )

        self.aliases = {}
        self._build_aliases()

    @staticmethod
    def _clean_name(name):
        """Normalize English, French and Arabic ingredient names."""

        if not isinstance(name, str):
            return ""

        name = name.strip().casefold()

        # Unicode decomposition.
        name = unicodedata.normalize("NFKD", name)

        # Remove Latin accents but preserve Arabic marks.
        cleaned = []

        for char in name:
            category = unicodedata.category(char)

            if category == "Mn" and "LATIN" in unicodedata.name(
                char, ""
            ):
                continue

            cleaned.append(char)

        name = "".join(cleaned)

        # Remove Arabic tatweel.
        name = name.replace("\u0640", "")

        # Normalize whitespace.
        return " ".join(name.split())

    def _build_aliases(self):
        """Build lookup dictionary from all multilingual aliases."""

        for ingredient in self.ingredients:

            ingredient_id = ingredient.get("id")
            names = ingredient.get("names", {})

            if not ingredient_id or not isinstance(names, dict):
                continue

            english_names = names.get("en", [])

            canonical_name = (
                english_names[0]
                if english_names
                else next(
                    (
                        alias
                        for aliases in names.values()
                        if aliases
                        for alias in aliases
                    ),
                    ingredient_id
                )
            )

            for language_names in names.values():

                if not isinstance(language_names, list):
                    continue

                for name in language_names:

                    key = self._clean_name(name)

                    if not key:
                        continue

                    if (
                        key in self.aliases
                        and self.aliases[key]["id"] != ingredient_id
                    ):
                        raise ValueError(
                            f"Duplicate ingredient alias '{name}' "
                            f"for {ingredient_id} and "
                            f"{self.aliases[key]['id']}"
                        )

                    self.aliases[key] = {
                        "id": ingredient_id,
                        "canonical_name": canonical_name
                    }

    def normalize(self, name):
        """Return canonical ingredient information."""

        if not isinstance(name, str) or not name.strip():
            return None

        key = self._clean_name(name)

        return self.aliases.get(key)

    def normalize_many(self, names):
        """Normalize multiple ingredient names."""

        if isinstance(names, str):
            names = [names]

        if not isinstance(names, (list, tuple)):
            raise TypeError("names must be a string, list or tuple")

        return [
            {
                "original": name,
                "normalized": self.normalize(name)
            }
            for name in names
        ]
