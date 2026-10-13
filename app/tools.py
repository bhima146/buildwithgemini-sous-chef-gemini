"""Firestore tools for recipes collection."""

import re
from typing import Any
from google.cloud import firestore
from google.adk.tools import ToolContext

FIRESTORE_PROJECT = "qwiklabs-gcp-04-6d790e70bcca"


def _get_firestore_client() -> firestore.Client:
    return firestore.Client(project=FIRESTORE_PROJECT)


def search_recipes(
    cuisine: str = "",
    dietary_tag: str = "",
    max_results: int = 5,
) -> list[dict[str, Any]]:
    """Search recipes in the collection by cuisine and/or dietary restrictions.

    Args:
        cuisine: Optional cuisine name to filter by (e.g. 'Mediterranean', 'Italian', 'Thai').
        dietary_tag: Optional dietary tag (e.g. 'vegetarian', 'gluten-free', 'vegan', 'high-protein').
        max_results: Maximum number of recipes to return (default 5).

    Returns:
        A list of matching recipe dictionaries.
    """
    db = _get_firestore_client()
    query = db.collection("recipes")

    if cuisine:
        query = query.where("cuisine", "==", cuisine.strip().title())

    docs = query.limit(20).stream()
    recipes = []
    dietary_tag_lower = dietary_tag.strip().lower()

    for doc in docs:
        data = doc.to_dict()
        data["id"] = doc.id
        if dietary_tag_lower:
            tags = [t.lower() for t in data.get("dietary_tags", [])]
            if dietary_tag_lower not in tags:
                continue
        recipes.append(data)
        if len(recipes) >= max_results:
            break

    return recipes


def get_recipe_details(recipe_id: str) -> dict[str, Any]:
    """Retrieve full details, ingredients, and instructions for a recipe by its ID.

    Args:
        recipe_id: The document ID of the recipe (e.g., 'lemon-herb-grilled-chicken').

    Returns:
        The recipe dictionary with full details, or an error dictionary if not found.
    """
    db = _get_firestore_client()
    doc = db.collection("recipes").document(recipe_id.strip()).get()
    if not doc.exists:
        return {"error": f"Recipe with ID '{recipe_id}' not found."}
    data = doc.to_dict()
    data["id"] = doc.id
    return data


def save_recipe(
    title: str,
    cuisine: str,
    category: str,
    ingredients: list[str],
    instructions: list[str],
    dietary_tags: list[str] | None = None,
    prep_time_minutes: int = 15,
    cook_time_minutes: int = 20,
    servings: int = 4,
    difficulty: str = "Easy",
    calories_per_serving: int = 350,
) -> dict[str, Any]:
    """Save a new recipe or user custom recipe to the Firestore database.

    Args:
        title: Title of the dish (e.g., 'Avocado Toast with Poached Egg').
        cuisine: Cuisine style (e.g., 'American', 'Mexican', 'Italian').
        category: Meal category (e.g., 'Breakfast', 'Lunch', 'Dinner', 'Dessert').
        ingredients: List of ingredient strings with measurements.
        instructions: Step-by-step cooking instructions.
        dietary_tags: Optional list of dietary tags (e.g., ['vegetarian', 'high-protein']).
        prep_time_minutes: Preparation time in minutes.
        cook_time_minutes: Cooking time in minutes.
        servings: Number of servings.
        difficulty: Difficulty level ('Easy', 'Medium', 'Hard').
        calories_per_serving: Estimated calories per serving.

    Returns:
        Confirmation dictionary with the assigned recipe ID.
    """
    db = _get_firestore_client()
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", title.strip().lower()).strip("-")
    recipe_id = slug or "custom-recipe"

    recipe_data = {
        "id": recipe_id,
        "title": title.strip(),
        "cuisine": cuisine.strip().title(),
        "category": category.strip().title(),
        "ingredients": ingredients,
        "instructions": instructions,
        "dietary_tags": dietary_tags or [],
        "prep_time_minutes": prep_time_minutes,
        "cook_time_minutes": cook_time_minutes,
        "servings": servings,
        "difficulty": difficulty.strip().title(),
        "calories_per_serving": calories_per_serving,
    }

    db.collection("recipes").document(recipe_id).set(recipe_data)
    return {"status": "success", "message": f"Recipe '{title}' saved successfully.", "recipe_id": recipe_id}


def generate_grocery_list(recipe_ids: list[str]) -> dict[str, Any]:
    """Generate a consolidated grocery shopping list from one or more recipes.

    Args:
        recipe_ids: List of recipe IDs to compile ingredients for (e.g., ['lemon-herb-grilled-chicken', 'creamy-tuscan-white-bean-soup']).

    Returns:
        A dictionary with recipes included and the consolidated list of grocery items.
    """
    db = _get_firestore_client()
    recipes_included = []
    items = []

    for rid in recipe_ids:
        doc = db.collection("recipes").document(rid.strip()).get()
        if doc.exists:
            data = doc.to_dict()
            recipes_included.append(data.get("title", rid))
            items.extend(data.get("ingredients", []))

    # Clean and deduplicate while preserving order
    unique_items = list(dict.fromkeys(items))

    return {
        "recipes": recipes_included,
        "total_items": len(unique_items),
        "grocery_list": unique_items,
    }


def fetch_web_recipes(search_term: str, max_results: int = 3) -> list[dict[str, Any]]:
    """Search for real-world recipes across the web using TheMealDB open public API.

    Args:
        search_term: Dish name or ingredient to search (e.g. 'chicken', 'pasta', 'salmon').
        max_results: Max recipes to return (default 3).

    Returns:
        List of simplified recipe dictionaries containing title, category, cuisine, ingredients, instructions, and thumbnail image.
    """
    import os
    import requests

    api_key = os.getenv("THEMEALDB_API_KEY", "1")
    url = f"https://www.themealdb.com/api/json/v1/{api_key}/search.php"

    try:
        response = requests.get(url, params={"s": search_term.strip()}, timeout=8)
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        return [{"error": f"Failed to fetch recipes from public API: {str(e)}"}]

    meals = data.get("meals") or []
    results = []

    for meal in meals[:max_results]:
        ingredients = []
        for i in range(1, 21):
            ing = meal.get(f"strIngredient{i}")
            measure = meal.get(f"strMeasure{i}")
            if ing and ing.strip():
                measurement = f"{measure.strip()} " if measure and measure.strip() else ""
                ingredients.append(f"{measurement}{ing.strip()}")

        results.append({
            "id": meal.get("idMeal"),
            "title": meal.get("strMeal"),
            "category": meal.get("strCategory"),
            "cuisine": meal.get("strArea"),
            "image_url": meal.get("strMealThumb"),
            "ingredients": ingredients,
            "instructions": meal.get("strInstructions", "").strip(),
            "source_url": meal.get("strSource"),
        })

    return results


GCS_BUCKET_NAME = "sous-chef-gemini-assets-qwiklabs-gcp-04-6d790e70bcca"


def generate_dish_image(
    dish_name: str,
    visual_description: str,
    tool_context: ToolContext,
) -> dict[str, Any]:
    """Generate a photo of a dish, save it to the session artifacts, and upload to public Cloud Storage.

    Args:
        dish_name: Name of the dish (e.g. 'Lemon Herb Grilled Chicken').
        visual_description: Visual details describing plating, garnishes, and colors.
        tool_context: ADK ToolContext to save session artifacts.

    Returns:
        Dictionary with public image URL and confirmation.
    """
    import uuid
    from google import genai
    from google.cloud import storage
    from google.genai import types

    prompt = (
        f"A professional culinary photograph of {dish_name}. {visual_description}. "
        "Appetizing presentation on a clean plate, natural restaurant lighting, shallow depth of field, high detail."
    )

    genai_client = genai.Client(
        vertexai=True,
        project=FIRESTORE_PROJECT,
        location="global",
    )

    response = genai_client.models.generate_content(
        model="gemini-3.1-flash-lite-image",
        contents=prompt,
        config=types.GenerateContentConfig(
            response_modalities=["IMAGE"],
        ),
    )

    image_bytes = None
    mime_type = "image/jpeg"
    part_to_save = None

    for part in response.parts:
        if part.inline_data:
            image_bytes = part.inline_data.data
            mime_type = part.inline_data.mime_type or "image/jpeg"
            part_to_save = part
            break

    if not image_bytes:
        return {"error": "Failed to generate image from model."}

    # 1. Save to ADK ToolContext artifact for Playground Artifacts panel
    slug = re.sub(r"[^a-zA-Z0-9]+", "_", dish_name.strip().lower()).strip("_")
    artifact_filename = f"{slug or 'dish'}.jpg"
    tool_context.save_artifact(
        filename=artifact_filename,
        artifact=part_to_save,
        custom_metadata={"dish_name": dish_name, "type": "dish_image"},
    )

    # 2. Upload to public Cloud Storage bucket
    storage_client = storage.Client(project=FIRESTORE_PROJECT)
    bucket = storage_client.bucket(GCS_BUCKET_NAME)
    object_name = f"dishes/{slug}_{uuid.uuid4().hex[:8]}.jpg"
    blob = bucket.blob(object_name)
    blob.upload_from_string(image_bytes, content_type=mime_type)

    public_url = f"https://storage.googleapis.com/{GCS_BUCKET_NAME}/{object_name}"

    return {
        "status": "success",
        "dish_name": dish_name,
        "artifact_filename": artifact_filename,
        "image_url": public_url,
        "message": f"Generated image for {dish_name} and saved as artifact.",
    }
