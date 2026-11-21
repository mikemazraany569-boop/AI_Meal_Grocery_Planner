
import re


class IngredientPhraseNormalizer:
    """
    Converts recipe ingredient phrases into canonical ingredient records.

    Uses IngredientNormalizer for canonical ID lookups.
    Ambiguous phrases are flagged instead of guessed.
    """

    def __init__(self):
        from src.normalization.ingredient_normalizer import IngredientNormalizer

        self.normalizer = IngredientNormalizer()

        # Safe phrase-level mappings.
        # Keys must be in their cleaned form.
        self.phrase_aliases = {
            "6 cloves of garlic": "garlic",
            "bushel of parsley": "parsley",
            "italian parsley": "parsley",
            "green cilantro": "cilantro",
            "dried chickpeas": "chickpeas",
            "red or yellow onion": "onion",
            "white onions": "onion",
            "yellow or white onion": "onion",
            "onions": "onion",
            "small courgettes": "zucchini",
            "lettuces or romaine lettuce": "lettuce",
            "green or coral lentils": "lentils",
            "shoulder of lamb": "lamb",
            "free range chicken": "chicken",
            "low salt chickpeas": "chickpeas",
            "low salt diced tomatoes": "tomato",
            "cans of chopped tomatoes": "tomato",
            "frozen bag green beans": "green beans",
            "vine leaves": "grape leaves",
            "sea bass scaled and gutted or in fillets": "sea bass",
            "water warm to form a paste": "water",
            "garlic cloves crushed": "garlic",
            "garlic cloves peeled": "garlic",
            "garlic cloves minced": "garlic",
            "garlic cloves": "garlic",
            "onion finely chopped": "onion",
            "onions finely chopped": "onion",
            "white onions sliced": "onion",
            "eggplant sliced into": "eggplant",
            "cinnamon powder": "cinnamon",
            "salt": "salt",
            "multi purpose flour": "flour",
            "ground beef": "beef",
            "finely ground beef": "beef",
            "tahini paste": "tahini",
            "red chili pepper": "chili pepper",
            "tomato paste": "tomato paste",
            "few drops of pomegranate molasses": "pomegranate molasses",
        }

        # Multiple required ingredients.
        self.compound_phrases = {
            "salt and pepper": ["salt", "pepper"],
            "salt and black pepper": ["salt", "black pepper"],
            "salt and sweet pepper": ["salt", "sweet pepper"],
            "tahini and vinegar": ["tahini", "vinegar"],
        }

        # Alternative ingredients: only one option is required.
        self.alternative_phrases = {
            "500 ml water or chicken stock": [
                "water",
                "chicken stock",
            ],
            "finely ground beef": [
                "beef",
                "lamb",
            ],
            "pita chips or crusty bread for dipping": [
                "pita chips",
                "crusty bread",
            ],
        }

        # Ambiguous phrases requiring manual review.
        self.review_phrases = {
            "pepper": "Could mean black pepper or sweet pepper.",
            "coriander": (
                "Could mean coriander seeds or fresh coriander leaves."
            ),
            "lamb ground onions": (
                "Ingredient boundaries are unclear."
            ),
            "dry dough": (
                "The ingredient is not sufficiently specified."
            ),
            "basic vegetables stuffing": (
                "Composite ingredient; components are unknown."
            ),
            "meat": "Meat type is not specified.",
            "tomato juice": (
                "Keep distinct from tomato and tomato paste."
            ),
            "7 spices": (
                "Lebanese spice mixture; composition may vary."
            ),
            "piquant post spicy mint blend": (
                "Branded spice blend."
            ),
            "wheat": (
                "Needs a more specific ingredient form."
            ),
            "medium fat meat": (
                "Meat type and fat percentage are unclear."
            ),
        }

    @staticmethod
    def _clean(text):
        """Standardize text for matching."""
        if not isinstance(text, str):
            return ""

        text = text.casefold().strip()
        text = text.replace(",", " ")
        text = text.replace("-", " ")
        text = re.sub(r"\s+", " ", text)

        return text.strip(" .;:")

    def _lookup(self, candidate):
        """Look up a canonical ingredient."""
        result = self.normalizer.normalize(candidate)

        if result is None:
            return None

        return {
            "id": result["id"],
            "canonical_name": result["canonical_name"],
        }

    def _component(self, candidate):
        """Convert one ingredient name into a canonical component."""
        candidate = self._clean(candidate)

        # First try the existing ingredient database.
        result = self._lookup(candidate)

        if result:
            return {
                "original": candidate,
                **result,
                "status": "matched",
            }

        # Then try the phrase aliases.
        replacement = self.phrase_aliases.get(candidate)

        if replacement:
            result = self._lookup(replacement)

            if result:
                return {
                    "original": candidate,
                    **result,
                    "status": "matched",
                }

        return {
            "original": candidate,
            "id": None,
            "canonical_name": None,
            "status": "needs_review",
        }

    def normalize(self, phrase):
        """Normalize one ingredient phrase."""

        if not isinstance(phrase, str) or not phrase.strip():
            return {
                "original": phrase,
                "components": [],
                "alternatives": [],
                "status": "needs_review",
                "review_reason": "Empty or invalid ingredient phrase.",
            }

        original = phrase
        cleaned = self._clean(phrase)

        # Remove recipe section headings.
        # Example: "Meat Stuffing: ground beef" -> "ground beef"
        if ":" in cleaned:
            cleaned = cleaned.split(":", maxsplit=1)[1].strip()

        # Preserve alternatives found in parentheses.
        # Example: "finely ground beef (or lamb, lean, divided)"
        # becomes "finely ground beef or lamb, lean, divided".
        alternative_match = re.search(
            r"\s*\(or\s+([^)]*)\)",
            cleaned,
        )

        if alternative_match:
            alternative_text = alternative_match.group(1)

            cleaned = (
                cleaned[:alternative_match.start()]
                + " or "
                + alternative_text
            )
        else:
            # Remove ordinary parenthetical notes.
            cleaned = re.sub(r"\([^)]*\)", "", cleaned)

        cleaned = self._clean(cleaned)

        # Remove preparation descriptions and optional notes.
        preparation_patterns = [
            r"\s+optional$",
            r"\s+to taste$",
            r"\s+finely chopped$",
            r"\s+chopped$",
            r"\s+minced$",
            r"\s+crushed$",
            r"\s+peeled$",
            r"\s+sliced$",
            r"\s+diced$",
            r"\s+divided$",
            r"\s+for dipping$",
            r"\s+chop away the stems$",
            r"\s+lean$",
        ]

        # Repeat because removing one suffix may expose another.
        previous = None

        while previous != cleaned:
            previous = cleaned

            for pattern in preparation_patterns:
                cleaned = re.sub(pattern, "", cleaned).strip()

        cleaned = self._clean(cleaned)

        # Check ambiguous phrases before attempting a match.
        if cleaned in self.review_phrases:
            return {
                "original": original,
                "components": [],
                "alternatives": [],
                "status": "needs_review",
                "review_reason": self.review_phrases[cleaned],
            }

        # Handle explicitly defined alternatives.
        if cleaned in self.alternative_phrases:
            components = [
                self._component(item)
                for item in self.alternative_phrases[cleaned]
            ]

            return {
                "original": original,
                "components": [],
                "alternatives": components,
                "status": (
                    "alternatives"
                    if all(
                        c["status"] == "matched"
                        for c in components
                    )
                    else "needs_review"
                ),
            }

        # Resolve known aliases BEFORE splitting generic alternatives.
        known_alias = self.phrase_aliases.get(cleaned)

        if known_alias:
            component = self._component(known_alias)

            if component["status"] == "matched":
                component["original"] = original

                return {
                    "original": original,
                    "components": [component],
                    "alternatives": [],
                    "status": "matched",
                }

        # Handle explicit alternatives separated by "or".
        if " or " in cleaned:
            parts = [
                part.strip()
                for part in cleaned.split(" or ")
            ]

            components = [
                self._component(part)
                for part in parts
            ]

            return {
                "original": original,
                "components": [],
                "alternatives": components,
                "status": (
                    "alternatives"
                    if all(
                        c["status"] == "matched"
                        for c in components
                    )
                    else "needs_review"
                ),
            }

        # Handle compound ingredients.
        if cleaned in self.compound_phrases:
            components = [
                self._component(item)
                for item in self.compound_phrases[cleaned]
            ]

            return {
                "original": original,
                "components": components,
                "alternatives": [],
                "status": (
                    "matched"
                    if all(
                        c["status"] == "matched"
                        for c in components
                    )
                    else "needs_review"
                ),
            }

        # Apply phrase-level aliases.
        candidate = self.phrase_aliases.get(cleaned, cleaned)

        # Match the resulting ingredient.
        component = self._component(candidate)

        if component["status"] == "matched":
            component["original"] = original

            return {
                "original": original,
                "components": [component],
                "alternatives": [],
                "status": "matched",
            }

        return {
            "original": original,
            "components": [component],
            "alternatives": [],
            "status": "needs_review",
            "review_reason": (
                "No reliable canonical ingredient match found."
            ),
        }

    def normalize_many(self, phrases):
        """Normalize multiple ingredient phrases."""

        if isinstance(phrases, str):
            phrases = [phrases]

        if not isinstance(phrases, (list, tuple)):
            raise TypeError(
                "phrases must be a string, list, or tuple"
            )

        return [
            self.normalize(phrase)
            for phrase in phrases
        ]
