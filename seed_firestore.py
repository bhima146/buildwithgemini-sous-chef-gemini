"""Seed script for Firestore recipes collection."""

from google.cloud import firestore

FIRESTORE_PROJECT = "qwiklabs-gcp-04-6d790e70bcca"

SAMPLE_RECIPES = [
    {
        "id": "lemon-herb-grilled-chicken",
        "title": "Lemon Herb Grilled Chicken",
        "cuisine": "Mediterranean",
        "category": "Dinner",
        "dietary_tags": ["high-protein", "gluten-free", "low-carb"],
        "prep_time_minutes": 15,
        "cook_time_minutes": 20,
        "servings": 4,
        "difficulty": "Easy",
        "ingredients": [
            "4 chicken breasts",
            "2 tbsp olive oil",
            "1 lemon (juiced & zested)",
            "2 cloves garlic (minced)",
            "1 tsp dried oregano",
            "salt and black pepper"
        ],
        "instructions": [
            "Whisk olive oil, lemon juice, zest, garlic, oregano, salt, and pepper in a bowl.",
            "Toss chicken in marinade for 15 minutes.",
            "Grill chicken on medium-high heat for 6-8 minutes per side until internal temp is 165°F.",
            "Rest for 5 minutes before slicing and serving."
        ],
        "calories_per_serving": 320
    },
    {
        "id": "creamy-tuscan-white-bean-soup",
        "title": "Creamy Tuscan White Bean Soup",
        "cuisine": "Italian",
        "category": "Lunch",
        "dietary_tags": ["vegetarian", "vegan", "gluten-free", "high-fiber"],
        "prep_time_minutes": 10,
        "cook_time_minutes": 25,
        "servings": 4,
        "difficulty": "Easy",
        "ingredients": [
            "2 cans cannellini beans (rinsed)",
            "1 onion (diced)",
            "2 carrots (sliced)",
            "3 cloves garlic (minced)",
            "4 cups vegetable broth",
            "2 cups fresh spinach",
            "1 tbsp olive oil",
            "1 tsp dried rosemary"
        ],
        "instructions": [
            "Sauté onion, carrots, and garlic in olive oil for 5 minutes.",
            "Add beans, rosemary, and broth. Simmer for 15 minutes.",
            "Blend half the soup with an immersion blender for creaminess.",
            "Stir in fresh spinach until wilted, season with salt and pepper, and serve warm."
        ],
        "calories_per_serving": 240
    },
    {
        "id": "spicy-thai-basil-beef",
        "title": "Spicy Thai Basil Beef (Pad Krapow)",
        "cuisine": "Thai",
        "category": "Dinner",
        "dietary_tags": ["dairy-free", "high-protein"],
        "prep_time_minutes": 10,
        "cook_time_minutes": 10,
        "servings": 2,
        "difficulty": "Medium",
        "ingredients": [
            "300g ground beef or sliced flank steak",
            "1 cup fresh holy basil leaves",
            "3 bird's eye chilies (minced)",
            "4 cloves garlic (minced)",
            "1 tbsp soy sauce",
            "1 tbsp oyster sauce",
            "1 tsp fish sauce",
            "1 tsp brown sugar",
            "1 tbsp cooking oil"
        ],
        "instructions": [
            "Pound garlic and chilies into a rough paste.",
            "Heat oil in a wok over high heat, fry chili-garlic paste for 30 seconds.",
            "Add beef and stir-fry until browned and cooked through.",
            "Add sauces and sugar, toss for 1 minute.",
            "Turn off heat, fold in basil until wilted, and serve over jasmine rice."
        ],
        "calories_per_serving": 410
    },
    {
        "id": "quinoa-avocado-power-bowl",
        "title": "Quinoa & Roasted Veggie Power Bowl",
        "cuisine": "Contemporary",
        "category": "Lunch",
        "dietary_tags": ["vegetarian", "vegan", "gluten-free"],
        "prep_time_minutes": 15,
        "cook_time_minutes": 20,
        "servings": 2,
        "difficulty": "Easy",
        "ingredients": [
            "1 cup cooked quinoa",
            "1 ripe avocado (sliced)",
            "1 sweet potato (cubed and roasted)",
            "1 cup cherry tomatoes (halved)",
            "2 tbsp pumpkin seeds",
            "2 tbsp tahini-lemon dressing"
        ],
        "instructions": [
            "Divide cooked quinoa between two bowls.",
            "Arrange roasted sweet potatoes, fresh avocado, and cherry tomatoes on top.",
            "Sprinkle with pumpkin seeds and drizzle generously with tahini dressing."
        ],
        "calories_per_serving": 380
    }
]


def seed_database():
    print(f"Connecting to Firestore in project: {FIRESTORE_PROJECT}...")
    db = firestore.Client(project=FIRESTORE_PROJECT)
    collection_ref = db.collection("recipes")

    for item in SAMPLE_RECIPES:
        doc_id = item["id"]
        collection_ref.document(doc_id).set(item)
        print(f"✓ Seeded recipe: {item['title']} ({doc_id})")

    print("\nFirestore recipes collection successfully seeded! 🎉")


if __name__ == "__main__":
    seed_database()
