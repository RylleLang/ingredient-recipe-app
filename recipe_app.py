
import streamlit as st
import torch
from PIL import Image

# --- Streamlit page config and custom CSS for design ---
st.set_page_config(page_title="Ingredient Detector & Recipe Suggester", page_icon="🍳", layout="centered")

st.markdown(
    """
    <style>
    .main {
        background-color: #f8f9fa;
    }
    .stApp {
        background: linear-gradient(120deg, #f8fafc 0%, #e0e7ff 100%);
    }
    .title-style {
        font-size:2.5rem; color:#4f8bf9; font-weight:700; margin-bottom:0.5em;
    }
    .subtitle-style {
        font-size:1.2rem; color:#22223b; margin-bottom:1.5em;
    }
    .recipe-card {
        background: #fff;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(79,139,249,0.08);
        padding: 1.2em 1.5em;
        margin-bottom: 1.2em;
        border-left: 5px solid #4f8bf9;
        color: #22223b;
        transition: box-shadow 0.2s;
    }
    .recipe-card:hover {
        box-shadow: 0 4px 16px rgba(79,139,249,0.18);
    }
    .ingredient-badge {
        display: inline-block;
        background: #e0e7ff;
        color: #4f8bf9;
        border-radius: 8px;
        padding: 0.2em 0.7em;
        margin: 0.1em 0.2em;
        font-size: 0.95em;
    }
    .stMarkdown, .stText, .stSubheader, .stDataFrame, .stTable, .stAlert, .stCodeBlock, .stException, .stCaption, .st-bb, .st-cb, .st-eb, .stTextInput, .stFileUploader, .stImage, .stMarkdown p, .stMarkdown h1, .stMarkdown h2, .stMarkdown h3, .stMarkdown h4, .stMarkdown h5, .stMarkdown h6 {
        color: #22223b !important;
    }
    .stMarkdown strong, .stMarkdown em {
        color: #22223b !important;
    }
    /* Custom subheader icon and style for Suggested Recipes */
    .stSubheader:has(span[data-testid="stMarkdownContainer"]:contains("Suggested Recipes")),
    .stSubheader:has(span:contains("Suggested Recipes")) {
        color: #22223b !important;
    }
    /* Custom scrollbar styling */
    ::-webkit-scrollbar {
        width: 12px;
        background: #e0e7ff;
    }
    ::-webkit-scrollbar-thumb {
        background: #22223b;
        border-radius: 8px;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: #4f8bf9;
    }
    label { color: #22223b !important; }
    .stFileUploader label { color: #22223b !important; }
    </style>
    """,
    unsafe_allow_html=True,
)

# Recipes dictionary
RECIPES = {
    "Scrambled Eggs": {
        "ingredients": {"egg", "salt", "butter"},
        "instructions": "Beat eggs with salt, cook in buttered pan.",
        "nutrition": "Eggs are a great source of protein and healthy fats. Butter adds flavor and energy.",
        "cost": 35,
    },
    "Pancakes": {
        "ingredients": {"flour", "egg", "milk", "sugar", "butter"},
        "instructions": "Mix ingredients and cook on griddle.",
        "nutrition": "Provides carbohydrates for energy and protein from eggs and milk.",
        "cost": 60,
    },
    "Tomato Pasta": {
        "ingredients": {"pasta", "tomato", "salt", "olive oil"},
        "instructions": "Cook pasta, prepare tomato sauce, mix and serve.",
        "nutrition": "Tomatoes are rich in vitamin C and antioxidants. Olive oil is heart-healthy.",
        "cost": 80,
    },
    "Adobo": {
        "ingredients": {"chicken", "soy sauce", "vinegar", "garlic", "bay leaves", "pepper"},
        "instructions": "Marinate chicken in soy sauce and vinegar, cook with garlic, bay leaves, and pepper.",
        "nutrition": "Chicken is a lean protein. Garlic and vinegar may support heart health.",
        "cost": 150,
    },
    "Sinigang": {
        "ingredients": {"pork", "tamarind", "tomato", "radish", "eggplant", "water spinach"},
        "instructions": "Boil pork with tamarind broth, add vegetables and simmer.",
        "nutrition": "Rich in vitamins from vegetables and protein from pork. Tamarind aids digestion.",
        "cost": 120,
    },
    "Nilaga": {
        "ingredients": {"beef", "potato", "corn", "cabbage", "peppercorn"},
        "instructions": "Boil beef with vegetables and peppercorn until tender.",
        "nutrition": "Beef provides iron and protein. Cabbage and potatoes add fiber and vitamins.",
        "cost": 140,
    },
    "Sisig": {
        "ingredients": {"pork", "onion", "chili", "calamansi", "mayonnaise"},
        "instructions": "Grill pork, chop finely, mix with onion, chili, calamansi, and mayonnaise.",
        "nutrition": "Pork is a good source of protein. Calamansi and chili add vitamin C and metabolism-boosting properties.",
        "cost": 110,
    },
    "Spaghetti": {
        "ingredients": {"spaghetti noodles", "tomato sauce", "ground beef", "hotdog", "cheese"},
        "instructions": "Cook noodles, prepare sauce with ground beef and hotdog, mix and top with cheese.",
        "nutrition": "A hearty dish providing carbohydrates, protein, and calcium. Rich in vitamins from tomato sauce.",
        "cost": 90,
    },
    "Lumpia": {
        "ingredients": {"spring roll wrappers", "ground pork", "carrot", "onion", "garlic"},
        "instructions": "Mix ground pork with vegetables, wrap in wrappers, and fry.",
        "nutrition": "Contains protein from pork and vitamins from vegetables. Frying adds fat and calories.",
        "cost": 100,
    },
    "Bistek": {
        "ingredients": {"beef", "soy sauce", "onion", "calamansi", "pepper"},
        "instructions": "Marinate beef in soy sauce and calamansi, cook with onions and pepper.",
        "nutrition": "Beef provides protein and iron. Onions have antioxidants, and calamansi adds vitamin C.",
        "cost": 130,
    },
    "Lechon": {
        "ingredients": {"whole pig", "salt", "pepper", "garlic", "lemongrass"},
        "instructions": "Season pig, stuff with lemongrass, and roast until crispy.",
        "nutrition": "Rich in protein and fat. Garlic and lemongrass add flavor and potential health benefits.",
        "cost": 300,
    },
    "Lugaw": {
        "ingredients": {"rice", "chicken broth", "ginger", "garlic", "onion"},
        "instructions": "Cook rice in broth with ginger, garlic, and onion until porridge consistency.",
        "nutrition": "A comforting dish providing carbohydrates, protein, and vitamins. Ginger and garlic may boost immunity.",
        "cost": 70,
    },
    "Carbonara": {
        "ingredients": {"pasta", "cream", "bacon", "egg yolk", "cheese"},
        "instructions": "Cook pasta, mix with cream, bacon, egg yolk, and cheese.",
        "nutrition": "Rich in carbohydrates, protein, and fat. Provides calcium from cheese and vitamins from egg yolk.",
        "cost": 85,
    },
    "Biko": {
        "ingredients": {"glutinous rice", "coconut milk", "brown sugar"},
        "instructions": "Cook rice with coconut milk and brown sugar until sticky.",
        "nutrition": "A sweet treat providing carbohydrates and fat. Coconut milk adds a rich flavor and calories.",
        "cost": 50,
    },
    "Chicken Curry": {
        "ingredients": {"chicken", "curry powder", "coconut milk", "potato", "carrot", "onion", "garlic"},
        "instructions": "Sauté onion and garlic, add chicken, curry powder, coconut milk, potatoes, and carrots. Simmer until cooked.",
        "nutrition": "Chicken is a lean protein. Curry powder contains antioxidants, and coconut milk provides healthy fats.",
        "cost": 160,
    },
    "Vegetable Stir Fry": {
        "ingredients": {"broccoli", "carrot", "bell pepper", "soy sauce", "garlic", "onion"},
        "instructions": "Stir fry vegetables with garlic and onion, add soy sauce, cook until crisp-tender.",
        "nutrition": "Low in calories, high in vitamins, minerals, and fiber. Garlic and soy sauce add flavor and potential health benefits.",
        "cost": 75,
    },
    "Fruit Salad": {
        "ingredients": {"apple", "banana", "orange", "mango", "yogurt"},
        "instructions": "Chop fruits, mix with yogurt, chill before serving.",
        "nutrition": "Rich in vitamins, minerals, and probiotics (from yogurt). Provides dietary fiber and antioxidants.",
        "cost": 90,
    },
    "Garlic Butter Shrimp": {
        "ingredients": {"shrimp", "garlic", "butter", "lemon", "parsley"},
        "instructions": "Sauté garlic in butter, add shrimp, cook until pink, finish with lemon and parsley.",
        "nutrition": "Shrimp is low in calories and high in protein. Garlic and lemon may boost immunity and add flavor.",
        "cost": 200,
    },
    "Egg Fried Rice": {
        "ingredients": {"rice", "egg", "soy sauce", "carrot", "onion", "peas"},
        "instructions": "Scramble eggs, add vegetables, mix in rice and soy sauce, stir fry until hot.",
        "nutrition": "A complete meal with carbohydrates, protein, and vitamins. Eggs add richness and nutrients.",
        "cost": 70,
    },
    "Beef Tapa": {
        "ingredients": {"beef", "soy sauce", "garlic", "sugar", "vinegar"},
        "instructions": "Marinate beef in soy sauce, garlic, sugar, and vinegar. Fry until cooked.",
        "nutrition": "Beef provides protein and iron. Garlic and vinegar may support heart health. Sugar adds energy.",
        "cost": 140,
    },
    "Mango Float": {
        "ingredients": {"mango", "cream", "condensed milk", "graham crackers"},
        "instructions": "Layer graham crackers, cream mixture, and mango slices. Chill before serving.",
        "nutrition": "A dessert rich in vitamins from mango, and provides calcium and protein from cream and milk.",
        "cost": 120,
    },
    "BLT Sandwich": {
        "ingredients": {"bread", "bacon", "lettuce", "tomato", "mayonnaise"},
        "instructions": "Toast bread, layer bacon, lettuce, tomato, and mayonnaise.",
        "nutrition": "Provides protein, fats, and carbohydrates. Bacon adds flavor, and lettuce and tomato provide vitamins.",
        "cost": 85,
    },
    "Caesar Salad": {
        "ingredients": {"lettuce", "croutons", "parmesan", "chicken", "caesar dressing"},
        "instructions": "Toss lettuce with dressing, top with chicken, croutons, and parmesan.",
        "nutrition": "Romaine lettuce is high in fiber and vitamins. Caesar dressing and parmesan add calcium and flavor.",
        "cost": 95,
    },
    "Omelette": {
        "ingredients": {"egg", "cheese", "onion", "tomato", "bell pepper"},
        "instructions": "Beat eggs, add vegetables and cheese, cook in pan until set.",
        "nutrition": "Eggs are a good source of protein. Vegetables add vitamins, and cheese provides calcium.",
        "cost": 70,
    },
    "Grilled Cheese": {
        "ingredients": {"bread", "cheese", "butter"},
        "instructions": "Butter bread, add cheese, grill until golden brown.",
        "nutrition": "A good source of calcium and protein from cheese. Butter adds flavor and fat.",
        "cost": 50,
    },
    "Mashed Potatoes": {
        "ingredients": {"potato", "butter", "milk", "salt", "pepper"},
        "instructions": "Boil potatoes, mash with butter, milk, salt, and pepper.",
        "nutrition": "Potatoes are high in potassium and vitamin C. Butter and milk add richness and calcium.",
        "cost": 60,
    },
    "Banana Smoothie": {
        "ingredients": {"banana", "milk", "yogurt", "honey"},
        "instructions": "Blend banana, milk, yogurt, and honey until smooth.",
        "nutrition": "Bananas are high in potassium and fiber. Yogurt adds probiotics, and honey provides sweetness and antioxidants.",
        "cost": 80,
    },
    "Avocado Toast": {
        "ingredients": {"bread", "avocado", "salt", "pepper", "lemon"},
        "instructions": "Toast bread, mash avocado with lemon, salt, and pepper, spread on toast.",
        "nutrition": "Avocado is high in healthy fats and fiber. Provides vitamins E, C, B6, and potassium.",
        "cost": 90,
    },
    "Fish Tacos": {
        "ingredients": {"fish", "tortillas", "cabbage", "lime", "mayonnaise", "hot sauce"},
        "instructions": "Cook fish, assemble in tortillas with cabbage, sauce, and lime.",
        "nutrition": "Fish is a great source of lean protein and omega-3 fatty acids. Cabbage is high in fiber and vitamins.",
        "cost": 110,
    },
    "Potato Salad": {
        "ingredients": {"potato", "mayonnaise", "egg", "onion", "mustard"},
        "instructions": "Boil potatoes and eggs, chop, mix with mayonnaise, onion, and mustard.",
        "nutrition": "Potatoes are high in vitamins and fiber. Eggs add protein, and mayonnaise provides fat and flavor.",
        "cost": 75,
    },
    "Chocolate Mug Cake": {
        "ingredients": {"flour", "cocoa powder", "sugar", "milk", "butter"},
        "instructions": "Mix ingredients in mug, microwave until set.",
        "nutrition": "A quick dessert providing carbohydrates and fat. Cocoa powder adds antioxidants.",
        "cost": 45,
    },
    "Yogurt Parfait": {
        "ingredients": {"yogurt", "granola", "strawberries", "blueberries", "honey"},
        "instructions": "Layer yogurt, granola, and fruits in a glass, drizzle with honey.",
        "nutrition": "Rich in probiotics (from yogurt), fiber, and vitamins. Granola adds crunch and energy.",
        "cost": 95,
    },
    "Ham and Cheese Omelette": {
        "ingredients": {"egg", "ham", "cheese", "butter"},
        "instructions": "Beat eggs, pour in pan, add ham and cheese, fold and cook.",
        "nutrition": "Eggs and ham provide protein. Cheese adds calcium, and butter enhances flavor.",
        "cost": 80,
    },
    "Classic Burger": {
        "ingredients": {"ground beef", "bun", "lettuce", "tomato", "cheese", "onion", "ketchup"},
        "instructions": "Shape beef into patty, grill, assemble in bun with toppings.",
        "nutrition": "A hearty meal with protein from beef, carbohydrates from bun, and vitamins from vegetables.",
        "cost": 150,
    },
    # ...existing code...
}

# --- AUTO-GENERATED GENERIC RECIPES FOR ALL INGREDIENTS ---
ADDITIONAL_INGREDIENTS = [
    "Apple",
    "Banana",
    "Cucumber",
    "Orange",
    "Tomato",
    "apple",
    "asparagus",
    "avocado",
    "banana",
    "beef",
    "bell_pepper",
    "bento",
    "blueberries",
    "bread",
    "broccoli",
    "butter",
    "carrot",
    "cauliflower",
    "cheese",
    "chicken",
    "chicken_breast",
    "chocolate",
    "coffee",
    "corn",
    "cucumber",
    "egg",
    "eggs",
    "energy_drink",
    "fish",
    "flour",
    "garlic",
    "goat_cheese",
    "grated_cheese",
    "green_beans",
    "ground_beef",
    "guacamole",
    "ham",
    "heavy_cream",
    "humus",
    "ketchup",
    "leek",
    "lemon",
    "lettuce",
    "lime",
    "mango",
    "marmalade",
    "mayonaise",
    "milk",
    "mushrooms",
    "mustard",
    "nuts",
    "onion",
    "pak_choi",
    "pear",
    "pineapple",
    "potato",
    "potatoes",
    "pudding",
    "rice_ball",
    "salad",
    "sandwich",
    "sausage",
    "shrimp",
    "smoothie",
    "spinach",
    "spring_onion",
    "strawberries",
    "sugar",
    "sweet_potato",
    "tea_a",
    "tea_i",
    "tomato",
    "tomato_sauce",
    "tortillas",
    "turkey",
    "yogurt",
]

# Normalize all existing recipe ingredients for comparison
existing_ingredients = set()
for recipe in RECIPES.values():
    existing_ingredients.update([i.lower() for i in recipe["ingredients"]])


def make_simple_recipe(ingredient):
    name = ingredient.replace("_", " ").title() + " Delight"
    instr = f"Enjoy a simple dish featuring {ingredient.replace('_', ' ')} as the main ingredient. Wash, prepare, and serve as desired!"
    nutrition = "Provides essential vitamins and minerals."
    cost = 30
    return name, {ingredient.lower()}, instr, nutrition, cost


for ingr in ADDITIONAL_INGREDIENTS:
    norm_ingr = ingr.lower().replace("_", " ")
    if norm_ingr not in existing_ingredients:
        name, ingset, instr, nutrition, cost = make_simple_recipe(norm_ingr)
        RECIPES[name] = {"ingredients": ingset, "instructions": instr, "nutrition": nutrition, "cost": cost}


@st.cache_resource
def load_model():
    # Update the path to your trained weights if needed
    return torch.hub.load("ultralytics/yolov5", "custom", path="runs/train/exp16/weights/best.pt", force_reload=True)


def normalize_ingredient(name):
    # Lowercase, replace underscores with spaces, and handle plurals
    name = name.lower().replace("_", " ")
    # Simple plural normalization (e.g., eggs -> egg, potatoes -> potato)
    if name.endswith("es") and name[:-2] + "e" in INGREDIENT_SET:
        name = name[:-2] + "e"
    elif name.endswith("s") and name[:-1] in INGREDIENT_SET:
        name = name[:-1]
    return name


# Build a set of all recipe ingredients for normalization
INGREDIENT_SET = set()
for recipe in RECIPES.values():
    INGREDIENT_SET.update([i.lower() for i in recipe["ingredients"]])


def detect_ingredients(model, image):
    results = model(image)
    # Get detection results: xyxyn[0] columns: x1, y1, x2, y2, conf, cls
    det = results.xyxyn[0].cpu().numpy()
    names = results.names
    detected_list = []
    for *_, conf, cls in det:
        name = names[int(cls)]
        norm = normalize_ingredient(name)
        if norm in INGREDIENT_SET:
            detected_list.append({"name": norm, "confidence": float(conf)})
    # Remove duplicates, keep highest confidence for each ingredient
    dedup = {}
    for d in detected_list:
        if d["name"] not in dedup or d["confidence"] > dedup[d["name"]]["confidence"]:
            dedup[d["name"]] = d
    detected_final = list(dedup.values())
    print("Detected:", detected_final)
    return detected_final


def suggest_recipes(detected_ingredients):
    suggestions = []
    for name, recipe in RECIPES.items():
        matched = recipe["ingredients"].intersection(detected_ingredients)
        if matched:
            suggestions.append(
                (
                    name,
                    recipe["instructions"],
                    matched,
                    recipe["ingredients"],
                    recipe.get("nutrition", "Provides essential nutrients."),
                    recipe.get("cost", 0),
                )
            )
    # Sort by number of matched ingredients (descending)
    suggestions.sort(key=lambda x: len(x[2]), reverse=True)
    return suggestions


st.markdown('<div class="title-style">🍳 Ingredient Detector & Recipe Suggester</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="subtitle-style">Upload an image of your ingredients and get delicious recipe ideas instantly!</div>',
    unsafe_allow_html=True,
)

uploaded_file = st.file_uploader("Upload an image of your ingredients", type=["jpg", "jpeg", "png"])

if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Image", use_container_width=True)
    model = load_model()
    detected = detect_ingredients(model, image)
    if detected:
        st.write(
            "**Detected ingredients:**",
            ", ".join(
                f'<span class="ingredient-badge">{d["name"].capitalize()} ({d["confidence"] * 100:.1f}%)</span>'
                for d in detected
            ),
            unsafe_allow_html=True,
        )
    else:
        st.write("No ingredients detected.")
    recipes = suggest_recipes(set(d["name"] for d in detected))
    if recipes:
        # Use a food/basket emoji for the subheader
        st.markdown(
            '<div style="display:flex;align-items:center;font-size:1.5rem;color:#22223b;font-weight:600;margin-top:1.5em;margin-bottom:0.5em;"><span style="font-size:2rem;margin-right:0.5em;">🧺</span>Suggested Recipes:</div>',
            unsafe_allow_html=True,
        )
        for name, instr, matched, all_ings, nutrition, cost in recipes:
            matched_html = " ".join([f"<span class='ingredient-badge'>{i}</span>" for i in matched])
            needed_html = " ".join([f"<span class='ingredient-badge'>{i}</span>" for i in all_ings])
            buy_note = ""
            if len(matched) < len(all_ings):
                buy_note = f'<div style="color:#b26a00;font-size:0.97em;margin-bottom:0.3em;">Estimated cost to buy all needed ingredients: <b>₱{cost}</b></div>'
            else:
                buy_note = f'<div style="color:#388e3c;font-size:0.97em;margin-bottom:0.3em;">Estimated cost for this recipe: <b>₱{cost}</b></div>'
            st.markdown(
                f"""<div class="recipe-card">
                <div style="font-size:1.2rem;font-weight:600;margin-bottom:0.3em;">{name}</div>
                <div style="margin-bottom:0.5em;">
                    <span style="font-size:0.98em;color:#4f8bf9;font-weight:500;">Matched ingredients:</span> {matched_html}
                </div>
                <div style="margin-bottom:0.5em;">
                    <span style="font-size:0.98em;color:#4f8bf9;font-weight:500;">Needed:</span> {needed_html}
                </div>
                <div style="font-size:1.05em;margin-bottom:0.5em;">{instr}</div>
                <div style="font-size:0.98em;color:#388e3c;"><b>Nutrition/Benefit:</b> {nutrition}</div>
                {buy_note}
            </div>""",
                unsafe_allow_html=True,
            )
    else:
        st.info("No matching recipes found.")
else:
    st.markdown(
        '<div style="margin-top:2em; color:#4f8bf9; font-size:1.1rem;">👈 Upload an image to get started!</div>',
        unsafe_allow_html=True,
    )
