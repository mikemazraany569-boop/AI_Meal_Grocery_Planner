from src.recipe.recipe_loader import RecipeLoader
from src.rag.recipe_document_builder import RecipeDocumentBuilder


def test_build_documents():
    recipes = RecipeLoader().load_recipes()
    builder = RecipeDocumentBuilder()

    documents = builder.build_documents(recipes)

    assert len(documents) == 5

    for document in documents:
        assert document["page_content"]
        assert document["metadata"]["id"]
        assert document["metadata"]["ingredient_ids"]
        assert document["metadata"]["ingredient_groups"]
        assert document["metadata"]["has_instructions"]


def test_instructions_contain_real_text():
    recipes = RecipeLoader().load_recipes()
    builder = RecipeDocumentBuilder()

    document = builder.build_document(recipes[0])

    assert "Prick the aubergines" in document["page_content"]
    assert "Instructions: 1 2 3" not in document["page_content"]


def test_multilingual_ingredients():
    recipes = RecipeLoader().load_recipes()
    builder = RecipeDocumentBuilder()

    document = builder.build_document(recipes[0])
    content = document["page_content"]

    assert "English ingredients:" in content
    assert "Arabic ingredients:" in content
    assert "French ingredients:" in content


def test_alternative_ingredients_are_grouped():
    recipes = RecipeLoader().load_recipes()
    builder = RecipeDocumentBuilder()

    recipe = next(r for r in recipes if r["id"] == "LB026")
    document = builder.build_document(recipe)

    assert any(
        len(group) > 1
        for group in document["metadata"]["ingredient_groups"]
    )