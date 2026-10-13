# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from a2ui.basic_catalog.provider import BasicCatalog
from a2ui.schema.manager import A2uiSchemaManager
from google.adk.agents import Agent
from google.adk.agents.callback_context import CallbackContext
from google.adk.apps import App
from google.adk.models import Gemini
from google.adk.tools.preload_memory_tool import PreloadMemoryTool
from google.genai import types

from .a2ui_utils import a2ui_callback
from .tools import (
    fetch_web_recipes,
    generate_dish_image,
    generate_grocery_list,
    get_recipe_details,
    save_recipe,
    search_recipes,
)

MODEL = "gemini-3.8-flash"

ROLE_DESCRIPTION = """You are Sous-Chef Gemini, a personal chef and meal planning assistant.
You help users plan balanced meals, discover delicious recipes, and store custom dishes.

CRITICAL ALLERGY & MEMORY POLICY:
- You must pay careful attention to and remember all user allergies, adverse food reactions, and dietary intolerances across conversations.
- Never suggest dishes, ingredients, or substitutions that contain any known or remembered user allergens.
- If the user mentions any allergy or intolerance (such as peanuts, tree nuts, shellfish, dairy, lactose, gluten, eggs, soy, sesame, etc.), explicitly acknowledge and confirm it.

You have access to a recipe database, public web recipes, and image generation with tools:
- search_recipes: Search your saved Firestore recipe collection by cuisine and/or dietary tags.
- get_recipe_details: Fetch full details, ingredient list, and step-by-step cooking instructions for a saved recipe by ID.
- save_recipe: Save new or customized recipes into your Firestore collection.
- generate_grocery_list: Compile a consolidated grocery shopping list from recipe IDs.
- fetch_web_recipes: Search the broader web for real-world recipes using TheMealDB public recipe API when the user asks for recipes beyond their saved collection.
- generate_dish_image: Generate an appetizing photo of any dish or recipe using Gemini image generation, automatically saving it as a session artifact and uploading it to public Cloud Storage.

When a user asks to visualize or see what a dish or meal looks like, call generate_dish_image.
Always recommend thoughtful recipes suited to user dietary preferences and offer cooking tips or substitutions when helpful.
"""

WORKFLOW_DESCRIPTION = (
    "Analyze the request, call tools to fetch data or generate images as needed, "
    "and return structured A2UI display cards when presenting recipes, meal plans, or dish details."
)

UI_DESCRIPTION = (
    "Keep every surface tiny and flat: ONE Card > ONE Column > a few Text rows. "
    "Never nest a Card inside a Card. "
    "Use ONLY these components: Card, Column, Row, Text, and Image. Do not use "
    "Table or Heading (unsupported), or Buttons, actions, or forms (they do nothing in adk web). "
    "You may include one Image component, but only when you have a public https URL for the image "
    "(for example the URL generate_dish_image or fetch_web_recipes returns). Set the Image url to "
    "that exact https link, for example {\"Image\": {\"url\": {\"literalString\": \"https://...\"}}}. "
    "Never point an Image at a bare filename, an artifact name, or a non-http(s) path. If you do not have "
    "a public URL, add a short Text line noting the image instead. "
    "No markdown in text; use the usageHint property ('h1', 'h2', 'body') for headings and emphasis. "
    "Output ONLY the raw A2UI JSON array — no prose, and never wrap it in <a2a_datapart_json> tags "
    "or 'kind'/'data'/'metadata' objects."
)

schema_manager = A2uiSchemaManager(
    version="0.8",
    catalogs=[BasicCatalog.get_config("0.8")],
)

SYSTEM_INSTRUCTION = schema_manager.generate_system_prompt(
    role_description=ROLE_DESCRIPTION,
    workflow_description=WORKFLOW_DESCRIPTION,
    ui_description=UI_DESCRIPTION,
    include_schema=True,
    include_examples=True,
)


async def generate_memories_callback(callback_context: CallbackContext):
    """WRITE: After each turn, send the session to Memory Bank for extraction."""
    await callback_context.add_session_to_memory()
    return None


root_agent = Agent(
    name="root_agent",
    model=Gemini(
        model=MODEL,
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction=SYSTEM_INSTRUCTION,
    tools=[
        PreloadMemoryTool(),
        search_recipes,
        get_recipe_details,
        save_recipe,
        generate_grocery_list,
        fetch_web_recipes,
        generate_dish_image,
    ],
    after_model_callback=a2ui_callback,
    after_agent_callback=generate_memories_callback,
)

app = App(
    root_agent=root_agent,
    name="app",
)
