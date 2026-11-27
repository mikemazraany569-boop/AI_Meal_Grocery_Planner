
import logging
import re
import sys
from datetime import date
from html import escape
from io import BytesIO
from pathlib import Path

import streamlit as st

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    PageBreak,
    HRFlowable,
)

logger = logging.getLogger(__name__)

# ============================================================
# PROJECT PATH
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# ============================================================
# PROJECT IMPORTS
# ============================================================

from src.rag.recipe_retriever import RecipeRetriever
from src.rag.recipe_index_manager import RecipeIndexManager
from src.planner.weekly_meal_planner import WeeklyMealPlanner
from src.vision.detection_inventory_service import DetectionInventoryService

# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Lebanese Meal & Grocery Planner",
    page_icon="🍽️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================================
# SESSION STATE
# ============================================================

def initialize_state():
    defaults = {
        "inventory": [],
        "input_method": None,
        "inventory_confirmed": False,
        "detection_result": None,
        "detection_saved": False,
        "detection_service": None,
        "last_detection_error": None,
        "detection_session_id": 0,
        "recipe_retriever": None,
        "weekly_meal_planner": None,
        "meal_plan_result": None,
        "grocery_result": None,
        "service_error": None,
        "index_load_info": None,
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


initialize_state()


def sync_inventory_from_manager():
    """Synchronize the UI inventory with InventoryManager."""

    service = st.session_state.detection_service

    if service is not None:
        st.session_state.inventory = (
            service.inventory_manager.get_inventory_details()
        )


def initialize_services():
    """Initialize inventory, recipe retrieval, and meal planning."""

    if st.session_state.detection_service is None:
        st.session_state.detection_service = DetectionInventoryService()

    if st.session_state.recipe_retriever is None:
        retriever = RecipeRetriever()
        index_manager = RecipeIndexManager()

        load_info = index_manager.load(retriever)

        invalid_documents = [
            doc
            for doc in retriever.documents
            if not isinstance(
                doc.get("metadata", {}).get("recipe"),
                dict,
            )
        ]

        if invalid_documents:
            raise ValueError(
                "The saved recipe index does not contain the original "
                "recipe dictionaries in metadata['recipe']. "
                "Rebuild and save the recipe index using the current "
                "RecipeDocumentBuilder."
            )

        st.session_state.recipe_retriever = retriever
        st.session_state.index_load_info = load_info

    if st.session_state.weekly_meal_planner is None:
        st.session_state.weekly_meal_planner = WeeklyMealPlanner(
            recipe_retriever=st.session_state.recipe_retriever,
            inventory_manager=(
                st.session_state.detection_service.inventory_manager
            ),
        )


try:
    initialize_services()

except Exception as exc:
    logger.exception(
        "Failed to initialize recipe-planning services."
    )

    st.session_state.service_error = (
        f"{type(exc).__name__}: {exc}"
    )


# ============================================================
# INVENTORY MANAGEMENT
# ============================================================

def reset_inventory():
    """Clear inventory and generated results."""

    service = st.session_state.detection_service

    if service is not None:
        service.inventory_manager.clear_inventory()

    st.session_state.inventory = []
    st.session_state.input_method = None
    st.session_state.inventory_confirmed = False
    st.session_state.detection_result = None
    st.session_state.detection_saved = False
    st.session_state.last_detection_error = None
    st.session_state.meal_plan_result = None
    st.session_state.grocery_result = None

    st.session_state.detection_session_id += 1


# ============================================================
# GROCERY LIST RENDERING
# ============================================================

def render_grocery_value(value):
    """Render grocery results returned as dictionaries or lists."""

    if isinstance(value, dict):

        for key, item in value.items():
            st.markdown(
                f"**{str(key).replace('_', ' ').title()}**"
            )
            render_grocery_value(item)

    elif isinstance(value, list):

        if not value:
            st.caption("None")

        for item in value:

            if isinstance(item, dict):

                name = (
                    item.get("canonical_name")
                    or item.get("ingredient")
                    or item.get("name")
                    or item.get("ingredient_name")
                )

                if name:

                    quantity = item.get(
                        "missing_quantity",
                        item.get("quantity"),
                    )

                    unit = item.get("unit", "")

                    suffix = (
                        f" — {quantity} {unit}".strip()
                        if quantity is not None
                        else ""
                    )

                    st.write(f"- {name}{suffix}")

                    other_fields = {
                        key: val
                        for key, val in item.items()
                        if key not in {
                            "canonical_name",
                            "ingredient",
                            "name",
                            "ingredient_name",
                            "missing_quantity",
                            "quantity",
                            "unit",
                        }
                    }

                    if other_fields:
                        with st.expander(f"Details: {name}"):
                            st.json(other_fields)

                else:
                    st.json(item)

            else:
                st.write(f"- {item}")

    else:
        st.write(value)


# ============================================================
# PDF GENERATION HELPERS
# ============================================================

def pdf_safe_text(value):
    """Convert values into safe printable PDF text."""

    if value is None:
        return ""

    if isinstance(value, (dict, list)):
        return escape(str(value))

    return escape(str(value)).replace("\n", "<br/>")


def add_pdf_value(story, value, styles):
    """Render nested ingredient, instruction, or grocery data."""

    if isinstance(value, dict):

        for key, item in value.items():

            title = str(key).replace("_", " ").title()

            story.append(
                Paragraph(
                    pdf_safe_text(title),
                    styles["Heading3"],
                )
            )

            add_pdf_value(story, item, styles)

    elif isinstance(value, list):

        if not value:
            story.append(
                Paragraph("None", styles["Normal"])
            )
            return

        for item in value:

            if isinstance(item, dict):

                name = (
                    item.get("canonical_name")
                    or item.get("ingredient")
                    or item.get("name")
                    or item.get("ingredient_name")
                )

                if name:

                    quantity = item.get(
                        "missing_quantity",
                        item.get("quantity"),
                    )

                    unit = item.get("unit", "")

                    suffix = (
                        f" — {quantity} {unit}".strip()
                        if quantity is not None
                        else ""
                    )

                    story.append(
                        Paragraph(
                            f"• {pdf_safe_text(name)}"
                            f"{pdf_safe_text(suffix)}",
                            styles["Normal"],
                        )
                    )

                else:

                    for key, val in item.items():
                        story.append(
                            Paragraph(
                                f"<b>{pdf_safe_text(key)}:</b> "
                                f"{pdf_safe_text(val)}",
                                styles["Normal"],
                            )
                        )

                story.append(Spacer(1, 4))

            else:

                story.append(
                    Paragraph(
                        f"• {pdf_safe_text(item)}",
                        styles["Normal"],
                    )
                )

    else:

        story.append(
            Paragraph(
                pdf_safe_text(value),
                styles["Normal"],
            )
        )


def build_meal_plan_pdf(result, grocery_result=None):
    """Generate a downloadable PDF containing the weekly meal plan."""

    buffer = BytesIO()

    document = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=1.8 * cm,
        leftMargin=1.8 * cm,
        topMargin=1.8 * cm,
        bottomMargin=1.8 * cm,
        title="Lebanese Weekly Meal Plan",
        author="Lebanese Meal & Grocery Planner",
    )

    styles = getSampleStyleSheet()

    styles.add(
        ParagraphStyle(
            name="MainTitle",
            parent=styles["Title"],
            fontSize=21,
            leading=26,
            alignment=TA_CENTER,
            textColor=colors.HexColor("#245B45"),
            spaceAfter=12,
        )
    )

    styles.add(
        ParagraphStyle(
            name="DayHeading",
            parent=styles["Heading2"],
            fontSize=15,
            textColor=colors.HexColor("#245B45"),
            spaceBefore=12,
            spaceAfter=8,
        )
    )

    styles.add(
        ParagraphStyle(
            name="RecipeHeading",
            parent=styles["Heading3"],
            fontSize=12,
            textColor=colors.HexColor("#333333"),
            spaceBefore=8,
            spaceAfter=4,
        )
    )

    story = []

    # TITLE

    story.append(
        Paragraph(
            "Lebanese Weekly Meal Plan",
            styles["MainTitle"],
        )
    )

    story.append(
        Paragraph(
            "Your personalized meal plan and grocery list",
            styles["Normal"],
        )
    )

    story.append(Spacer(1, 12))

    # SUMMARY

    summary = result.get("summary", {})

    story.append(
        Paragraph(
            "Meal Plan Summary",
            styles["Heading2"],
        )
    )

    summary_items = [
        ("Planned meals", summary.get("planned_meals", 0)),
        (
            "Expiring ingredients",
            summary.get("expiring_ingredients", 0),
        ),
        (
            "Missing grocery items",
            summary.get("shopping_items", 0),
        ),
    ]

    for label, value in summary_items:
        story.append(
            Paragraph(
                f"<b>{label}:</b> {pdf_safe_text(value)}",
                styles["Normal"],
            )
        )

    story.append(Spacer(1, 12))

    story.append(
        HRFlowable(
            width="100%",
            color=colors.grey,
        )
    )

    # WEEKLY MEAL PLAN

    story.append(
        Paragraph(
            "Your Weekly Meals",
            styles["Heading1"],
        )
    )

    for day_plan in result.get("weekly_plan", []):

        day_number = day_plan.get("day", "?")

        story.append(
            Paragraph(
                f"Day {pdf_safe_text(day_number)}",
                styles["DayHeading"],
            )
        )

        meals = day_plan.get("meals", [])

        if not meals:
            story.append(
                Paragraph(
                    "No recipe available for this day.",
                    styles["Normal"],
                )
            )
            continue

        for meal in meals:

            recipe_name = meal.get(
                "recipe_name",
                "Unnamed recipe",
            )

            story.append(
                Paragraph(
                    pdf_safe_text(recipe_name),
                    styles["RecipeHeading"],
                )
            )

            coverage = meal.get("ingredient_coverage", 0)

            if isinstance(coverage, (int, float)):
                story.append(
                    Paragraph(
                        f"Ingredient coverage: {coverage:.0%}",
                        styles["Normal"],
                    )
                )

            recipe = meal.get("recipe", {})

            if isinstance(recipe, dict):

                description = (
                    recipe.get("description")
                    or recipe.get("description_en")
                )

                if description:
                    story.append(Spacer(1, 4))

                    story.append(
                        Paragraph(
                            pdf_safe_text(description),
                            styles["Normal"],
                        )
                    )

                ingredients = recipe.get(
                    "ingredients",
                    recipe.get("ingredients_detailed", []),
                )

                if ingredients:
                    story.append(
                        Paragraph(
                            "Ingredients",
                            styles["Heading4"],
                        )
                    )

                    add_pdf_value(
                        story,
                        ingredients,
                        styles,
                    )

                instructions = (
                    recipe.get("instructions")
                    or recipe.get("preparation")
                    or recipe.get("steps")
                )

                if instructions:
                    story.append(
                        Paragraph(
                            "Preparation",
                            styles["Heading4"],
                        )
                    )

                    add_pdf_value(
                        story,
                        instructions,
                        styles,
                    )

            story.append(Spacer(1, 10))

        story.append(
            HRFlowable(
                width="100%",
                color=colors.lightgrey,
            )
        )

    # GROCERY LIST

    story.append(PageBreak())

    story.append(
        Paragraph(
            "Grocery Shopping List",
            styles["Heading1"],
        )
    )

    if grocery_result:

        grocery_summary = grocery_result.get("summary", {})

        story.append(
            Paragraph(
                f"Shopping items: "
                f"{pdf_safe_text(grocery_summary.get('shopping_items', 0))}",
                styles["Normal"],
            )
        )

        story.append(
            Paragraph(
                f"Items to review: "
                f"{pdf_safe_text(grocery_summary.get('items_to_review', 0))}",
                styles["Normal"],
            )
        )

        story.append(Spacer(1, 10))

        grocery_items = {
            key: value
            for key, value in grocery_result.items()
            if key != "summary"
        }

        if grocery_items:
            add_pdf_value(
                story,
                grocery_items,
                styles,
            )
        else:
            story.append(
                Paragraph(
                    "No missing ingredients.",
                    styles["Normal"],
                )
            )

    else:
        story.append(
            Paragraph(
                "No grocery list was generated.",
                styles["Normal"],
            )
        )

    document.build(story)

    buffer.seek(0)

    return buffer.getvalue()


# ============================================================
# MEAL PLAN GENERATION
# ============================================================

def generate_meal_plan(
    days=7,
    meals_per_day=1,
    expiry_window_days=3,
):
    """Run the weekly planner and retain both outputs."""

    if st.session_state.service_error:
        raise RuntimeError(st.session_state.service_error)

    if st.session_state.weekly_meal_planner is None:
        raise RuntimeError(
            "The weekly meal planner is not initialized."
        )

    sync_inventory_from_manager()

    if not st.session_state.inventory:
        raise ValueError(
            "Your inventory is empty. Add ingredients first."
        )

    result = st.session_state.weekly_meal_planner.generate_plan(
        days=days,
        meals_per_day=meals_per_day,
        expiry_window_days=expiry_window_days,
        top_k=max(days * meals_per_day * 3, 50),
    )

    st.session_state.meal_plan_result = result
    st.session_state.grocery_result = result.get("grocery")

    return result


# ============================================================
# CUSTOM CSS AND HEADER
# ============================================================

st.markdown(
    """
    <style>
        .main-title {
            font-size: 36px;
            font-weight: 700;
            color: #245B45;
        }

        .subtitle {
            font-size: 16px;
            color: #777777;
        }

        .feature-card {
            padding: 22px;
            border-radius: 14px;
            background-color: #F3F7F2;
            border: 1px solid #DDE8DC;
            min-height: 150px;
        }

        div.stButton > button {
            border-radius: 9px;
            font-weight: 600;
            min-height: 42px;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="main-title">'
    '🍽️ Lebanese Meal & Grocery Planner'
    '</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="subtitle">'
    'Plan your meals • Reduce food waste • Discover Lebanese recipes'
    '</div>',
    unsafe_allow_html=True,
)

st.divider()


# ============================================================
# SIDEBAR NAVIGATION
# ============================================================

st.sidebar.title("🍽️ Navigation")

page = st.sidebar.radio(
    "Choose a section:",
    [
        "Home",
        "My Inventory",
        "Meal Planner",
        "Grocery List",
    ],
)

st.sidebar.divider()

st.sidebar.caption(
    "AI-powered meal planning using authentic Lebanese recipes."
)

st.sidebar.caption(
    "Languages: English | العربية | Français"
)

if st.session_state.service_error:
    st.error(
        "The recipe-planning services could not be initialized:\n\n"
        + st.session_state.service_error
    )


# ============================================================
# HOME PAGE
# ============================================================

if page == "Home":

    st.subheader("Welcome to your kitchen assistant!")

    st.write(
        "Generate personalized weekly meal plans using the ingredients "
        "already available in your kitchen."
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(
            '<div class="feature-card"><h3>🥬 Inventory</h3>'
            '<p>Manage your available ingredients.</p></div>',
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            '<div class="feature-card"><h3>🍲 Meal Planning</h3>'
            '<p>Discover Lebanese meals for your week.</p></div>',
            unsafe_allow_html=True,
        )

    with col3:
        st.markdown(
            '<div class="feature-card"><h3>🛒 Grocery List</h3>'
            '<p>Calculate the ingredients you still need.</p></div>',
            unsafe_allow_html=True,
        )

    st.divider()

    st.subheader("Your kitchen")

    if st.session_state.detection_service is not None:

        sync_inventory_from_manager()

        st.metric(
            "Inventory entries",
            len(st.session_state.inventory),
        )

    else:
        st.info("Inventory service is not available.")

    st.write(
        "Open **Meal Planner** to add ingredients and generate your 7-day plan."
    )


# ============================================================
# MY INVENTORY PAGE
# ============================================================

elif page == "My Inventory":

    st.header("🥬 My Kitchen Inventory")

    if st.session_state.detection_service is not None:
        sync_inventory_from_manager()

    inventory = st.session_state.inventory

    if not inventory:

        st.info(
            "Your inventory is currently empty. "
            "Go to Meal Planner to add ingredients."
        )

    else:

        st.success(
            f"{len(inventory)} ingredient records saved."
        )

        for index, ingredient in enumerate(inventory, start=1):

            if isinstance(ingredient, dict):

                name = ingredient.get(
                    "name",
                    "Unknown ingredient",
                )

                quantity = ingredient.get("quantity", "")
                unit = ingredient.get("unit", "")

                expiry = (
                    ingredient.get("expiry_date")
                    or "Not specified"
                )

                st.write(
                    f"**{index}. {name}** — "
                    f"{quantity} {unit} | Expiry: {expiry}"
                )

            else:
                st.write(f"{index}. {ingredient}")

        st.caption(
            f"Input method: "
            f"{st.session_state.input_method or 'Not specified'}"
        )

        if st.button(
            "Clear my inventory",
            type="secondary",
        ):
            reset_inventory()

            st.success(
                "Inventory and generated results cleared."
            )

            st.rerun()


# ============================================================
# MEAL PLANNER PAGE
# ============================================================

elif page == "Meal Planner":

    st.header("🍲 Generate Your Weekly Meal Plan")

    st.write(
        "Provide your available ingredients using photos or manual entry."
    )

    photo_tab, text_tab = st.tabs(
        [
            "📸 Upload Photos",
            "✍️ Write Ingredients",
        ]
    )

    # --------------------------------------------------------
    # PHOTO INPUT
    # --------------------------------------------------------

    with photo_tab:

        st.subheader("Upload refrigerator or pantry photos")

        st.write(
            "Select multiple JPG, JPEG, PNG, or WEBP images. "
            "Review detected ingredients before adding them to your inventory."
        )

        uploaded_files = st.file_uploader(
            "Choose one or more images",
            type=["jpg", "jpeg", "png", "webp"],
            accept_multiple_files=True,
            key="fridge_upload_multiple",
        )

        if uploaded_files:

            st.caption(
                f"{len(uploaded_files)} file(s) selected."
            )

            preview_columns = st.columns(
                min(3, len(uploaded_files))
            )

            for index, uploaded_file in enumerate(uploaded_files):

                with preview_columns[index % len(preview_columns)]:

                    st.image(
                        uploaded_file,
                        caption=uploaded_file.name,
                        use_container_width=True,
                    )

            if st.button(
                "🔍 Analyze uploaded images",
                type="primary",
                use_container_width=True,
                key="analyze_uploaded_images",
                disabled=(
                    st.session_state.detection_service is None
                ),
            ):

                try:

                    with st.spinner(
                        "Analyzing images. This may take a little time..."
                    ):

                        st.session_state.detection_result = (
                            st.session_state.detection_service.detect_and_map(
                                uploaded_files,
                                confidence=0.25,
                            )
                        )

                    st.session_state.detection_saved = False
                    st.session_state.last_detection_error = None
                    st.session_state.input_method = "photo"
                    st.session_state.inventory_confirmed = False

                    # Give every analysis a new set of checkbox keys.
                    st.session_state.detection_session_id += 1

                    st.success(
                        "Image analysis completed. Review the results below."
                    )

                except Exception as error:

                    logger.exception(
                        "Image analysis failed."
                    )

                    st.session_state.last_detection_error = str(error)

                    st.error(
                        f"Could not analyze the uploaded images: {error}"
                    )

        if st.session_state.last_detection_error:
            st.error(st.session_state.last_detection_error)

        detection_result = st.session_state.detection_result

        if detection_result:

            st.divider()

            st.subheader("Detection summary")

            metric1, metric2, metric3 = st.columns(3)

            metric1.metric(
                "Images selected",
                detection_result.get("total_images", 0),
            )

            metric2.metric(
                "Images analyzed",
                detection_result.get("successful_images", 0),
            )

            metric3.metric(
                "Recognized ingredients",
                len(detection_result.get("recognized", [])),
            )

            skipped_files = detection_result.get(
                "skipped_files",
                [],
            )

            if skipped_files:

                with st.expander(
                    f"Files skipped ({len(skipped_files)})"
                ):

                    for skipped in skipped_files:

                        st.write(
                            f"**{skipped.get('filename', 'Unknown')}**: "
                            f"{skipped.get('reason', 'Not processed')}"
                        )

            recognized = detection_result.get(
                "recognized",
                [],
            )

            if recognized and not st.session_state.detection_saved:

                st.subheader("Confirm detected ingredients")

                st.write(
                    "Select the ingredients that are actually present. "
                    "Adjust quantities and add expiry dates if known."
                )

                confirmed_ingredients = []

                detection_session_id = (
                    st.session_state.detection_session_id
                )

                for index, item in enumerate(recognized):

                    canonical_name = item.get(
                        "canonical_name",
                        "Unknown",
                    )

                    detected_label = item.get(
                        "detected_label",
                        canonical_name,
                    )

                    confidence = item.get(
                        "max_confidence",
                        item.get("confidence", 0.0),
                    )

                    # Validate confidence before using it.
                    try:
                        confidence_value = float(confidence)

                        if not 0 <= confidence_value <= 1:
                            confidence_value = 0.0

                    except (TypeError, ValueError):
                        confidence_value = 0.0

                    confidence_percent = (
                        f"{confidence_value * 100:.1f}%"
                    )

                    # Predictions below 40% require manual review.
                    low_confidence = confidence_value < 0.40

                    checkbox_key = (
                        f"confirm_detected_"
                        f"{detection_session_id}_{index}"
                    )

                    with st.container(border=True):

                        if low_confidence:

                            st.warning(
                                "Low-confidence prediction. "
                                "Please verify this ingredient carefully "
                                "before adding it."
                            )

                        selected = st.checkbox(
                            f"{canonical_name} · "
                            f"confidence {confidence_percent}",
                            value=not low_confidence,
                            key=checkbox_key,
                        )

                        st.caption(
                            f"Model label: {detected_label} | "
                            f"Detections: {item.get('detection_count', 1)} | "
                            f"Images: {item.get('image_count', 1)}"
                        )

                        if selected:

                            qty_col, unit_col, expiry_col = st.columns(
                                [1, 1, 1.5]
                            )

                            with qty_col:

                                quantity = st.number_input(
                                    "Quantity",
                                    min_value=0.01,
                                    value=1.0,
                                    step=1.0,
                                    key=(
                                        f"detected_quantity_"
                                        f"{detection_session_id}_{index}"
                                    ),
                                )

                            with unit_col:

                                unit = st.selectbox(
                                    "Unit",
                                    [
                                        "piece",
                                        "g",
                                        "kg",
                                        "ml",
                                        "L",
                                        "bunch",
                                        "clove",
                                        "can",
                                        "pack",
                                    ],
                                    key=(
                                        f"detected_unit_"
                                        f"{detection_session_id}_{index}"
                                    ),
                                )

                            with expiry_col:

                                has_expiry = st.checkbox(
                                    "Add expiry date",
                                    key=(
                                        f"has_expiry_"
                                        f"{detection_session_id}_{index}"
                                    ),
                                )

                                expiry_date = None

                                if has_expiry:

                                    expiry_date = st.date_input(
                                        "Expiry date",
                                        value=date.today(),
                                        key=(
                                            f"detected_expiry_"
                                            f"{detection_session_id}_{index}"
                                        ),
                                    ).isoformat()

                            confirmed_ingredients.append(
                                {
                                    "recognized": True,
                                    "canonical_name": canonical_name,
                                    "confirmed": True,
                                    "quantity": quantity,
                                    "unit": unit,
                                    "expiry_date": expiry_date,
                                }
                            )

                if st.button(
                    "✅ Save confirmed ingredients to inventory",
                    type="primary",
                    use_container_width=True,
                    key="save_detected_ingredients",
                    disabled=(
                        st.session_state.detection_service is None
                    ),
                ):

                    if not confirmed_ingredients:

                        st.warning(
                            "Select at least one detected ingredient "
                            "before saving."
                        )

                    else:

                        try:

                            save_result = (
                                st.session_state.detection_service
                                .add_confirmed_ingredients(
                                    confirmed_ingredients
                                )
                            )

                            sync_inventory_from_manager()

                            st.session_state.input_method = "photo"

                            st.session_state.inventory_confirmed = bool(
                                save_result.get("added")
                            )

                            st.session_state.detection_saved = bool(
                                save_result.get("added")
                            )

                            st.session_state.meal_plan_result = None
                            st.session_state.grocery_result = None

                            if save_result.get("added"):

                                st.success(
                                    "Added to inventory: "
                                    + ", ".join(save_result["added"])
                                )

                            if save_result.get("rejected"):

                                with st.expander("Items not added"):

                                    for rejected in save_result["rejected"]:

                                        st.write(
                                            rejected.get(
                                                "reason",
                                                "Could not add item",
                                            )
                                        )

                            if not save_result.get("added"):

                                st.warning(
                                    "No new ingredients were added. "
                                    "Check the rejected items above."
                                )

                            else:
                                st.rerun()

                        except Exception as error:

                            logger.exception(
                                "Could not save detected ingredients."
                            )

                            st.error(
                                "Could not save the confirmed ingredients: "
                                f"{error}"
                            )

            elif st.session_state.detection_saved:

                st.success(
                    "Confirmed detections have been saved to My Inventory."
                )

            else:

                st.info(
                    "No recognized ingredients were returned. "
                    "You can enter them manually in the text tab."
                )

            unrecognized = detection_result.get(
                "unrecognized",
                [],
            )

            if unrecognized:

                with st.expander(
                    f"Unrecognized model labels ({len(unrecognized)})"
                ):

                    st.write(
                        "These labels could not be matched to the ingredient "
                        "database. Add food ingredients manually in the text tab."
                    )

                    for item in unrecognized:

                        label = item.get(
                            "detected_label",
                            item.get("label", "Unknown"),
                        )

                        st.write(f"• {label}")

            with st.expander("Per-image detection details"):

                for image_result in detection_result.get(
                    "per_image",
                    [],
                ):
                    st.write(image_result)

        st.caption(
            "Detection note: this application uses a specialized "
            "35-class fruit and vegetable YOLOv8n model. "
            "It can still miss ingredients or produce false predictions, "
            "especially with unfamiliar foods, poor lighting, or unusual "
            "camera angles. Predictions below 40% confidence are "
            "unchecked by default. Always verify ingredients before saving."
        )

    # --------------------------------------------------------
    # MANUAL TEXT INPUT
    # --------------------------------------------------------

    with text_tab:

        st.subheader("Enter your kitchen ingredients")

        st.write(
            "Enter ingredients in English, Arabic, or French, "
            "separated by commas or new lines."
        )

        ingredient_text = st.text_area(
            "What ingredients do you have?",
            placeholder=(
                "Example:\n"
                "Tomatoes, onions, rice, lentils, potatoes\n"
                "طماطم، بصل، أرز، عدس\n"
                "Tomates, oignons, riz, lentilles"
            ),
            height=160,
            key="ingredient_text",
        )

        if st.button(
            "Save my ingredients",
            type="primary",
            use_container_width=True,
            key="save_text_ingredients",
            disabled=(
                st.session_state.detection_service is None
            ),
        ):

            ingredients = [
                item.strip()
                for item in re.split(
                    r"[,;\n،]+",
                    ingredient_text,
                )
                if item.strip()
            ]

            if not ingredients:

                st.warning(
                    "Please enter at least one ingredient."
                )

            else:

                added = []
                rejected = []

                for ingredient in ingredients:

                    success = (
                        st.session_state.detection_service
                        .inventory_manager
                        .add_ingredient(
                            ingredient=ingredient,
                            quantity=1,
                            unit="piece",
                        )
                    )

                    if success:
                        added.append(ingredient)
                    else:
                        rejected.append(ingredient)

                sync_inventory_from_manager()

                st.session_state.input_method = "text"

                st.session_state.inventory_confirmed = bool(
                    st.session_state.inventory
                )

                st.session_state.meal_plan_result = None
                st.session_state.grocery_result = None

                if added:

                    st.success(
                        f"Added {len(added)} ingredient(s) to inventory."
                    )

                    st.write("### Added ingredients")

                    for ingredient in added:
                        st.write(f"🥬 {ingredient}")

                if rejected:

                    st.warning(
                        "These ingredients were not added, possibly because "
                        "they already exist in your inventory: "
                        + ", ".join(rejected)
                    )

                if not added and not rejected:
                    st.warning("No ingredients were added.")

    # --------------------------------------------------------
    # GENERATE WEEKLY MEAL PLAN
    # --------------------------------------------------------

    st.divider()

    st.subheader("Generate your meal plan")

    sync_inventory_from_manager()

    if st.session_state.inventory:

        st.success(
            f"Your inventory is ready: "
            f"{len(st.session_state.inventory)} ingredient entries."
        )

        meals_per_day = st.selectbox(
            "Meals per day",
            options=[1, 2, 3],
            index=0,
            key="meals_per_day",
        )

        expiry_window = st.slider(
            "Prioritize ingredients expiring within (days)",
            min_value=0,
            max_value=14,
            value=3,
            key="expiry_window",
        )

        if st.button(
            "🍽️ Generate 7-Day Lebanese Meal Plan",
            type="primary",
            use_container_width=True,
            disabled=(
                bool(st.session_state.service_error)
                or st.session_state.weekly_meal_planner is None
            ),
        ):

            try:

                with st.spinner(
                    "Retrieving Lebanese recipes and preparing your meal plan..."
                ):

                    result = generate_meal_plan(
                        days=7,
                        meals_per_day=meals_per_day,
                        expiry_window_days=expiry_window,
                    )

                st.success(
                    "Your weekly meal plan and grocery list are ready."
                )

            except Exception as error:

                logger.exception(
                    "Meal plan generation failed."
                )

                st.error(
                    f"Could not generate the meal plan: {error}"
                )

    else:

        st.info(
            "First upload and confirm detections, "
            "or enter your ingredients manually."
        )

    # --------------------------------------------------------
    # DISPLAY EXISTING MEAL PLAN
    # --------------------------------------------------------

    result = st.session_state.meal_plan_result

    if result:

        st.divider()

        st.subheader("Your 7-Day Lebanese Meal Plan")

        for day_plan in result.get("weekly_plan", []):

            with st.expander(
                f"Day {day_plan.get('day', '?')}",
                expanded=True,
            ):

                if not day_plan.get("meals"):

                    st.info(
                        "No recipe was available for this day."
                    )

                for meal in day_plan.get("meals", []):

                    st.markdown(
                        f"**Meal {meal.get('meal_number', '')}: "
                        f"{meal.get('recipe_name', 'Unnamed recipe')}**"
                    )

                    coverage = meal.get(
                        "ingredient_coverage",
                        0,
                    )

                    st.caption(
                        "Ingredient coverage: "
                        f"{coverage:.0%}"
                        if isinstance(coverage, (int, float))
                        else "Ingredient coverage unavailable"
                    )

                    recipe = meal.get("recipe", {})

                    if isinstance(recipe, dict):

                        description = (
                            recipe.get("description")
                            or recipe.get("description_en")
                        )

                        if description:
                            st.write(description)

        # MEAL PLAN SUMMARY

        summary = result.get("summary", {})

        st.subheader("Meal Plan Summary")

        col1, col2, col3 = st.columns(3)

        col1.metric(
            "Planned meals",
            summary.get("planned_meals", 0),
        )

        col2.metric(
            "Expiring ingredients",
            summary.get("expiring_ingredients", 0),
        )

        col3.metric(
            "Missing grocery items",
            summary.get("shopping_items", 0),
        )

        for warning in result.get("warnings", []):
            st.warning(warning)

        st.info(
            "Your grocery list has been generated automatically. "
            "Open Grocery List to view it."
        )

        # ----------------------------------------------------
        # DOWNLOAD MEAL PLAN AS PDF
        # ----------------------------------------------------

        st.divider()

        st.subheader("📄 Download Your Meal Plan")

        try:

            pdf_data = build_meal_plan_pdf(
                result=result,
                grocery_result=st.session_state.grocery_result,
            )

            st.download_button(
                label="⬇️ Download Meal Plan as PDF",
                data=pdf_data,
                file_name="lebanese_weekly_meal_plan.pdf",
                mime="application/pdf",
                type="primary",
                use_container_width=True,
                key="download_meal_plan_pdf",
            )

        except Exception as error:

            logger.exception(
                "PDF generation failed."
            )

            st.error(
                f"Could not generate the PDF: {error}"
            )


# ============================================================
# GROCERY LIST PAGE
# ============================================================

elif page == "Grocery List":

    st.header("🛒 My Grocery List")

    grocery_result = st.session_state.grocery_result

    if not grocery_result:

        st.info(
            "Generate your 7-day Lebanese meal plan first. "
            "The missing ingredients will appear here automatically."
        )

    else:

        summary = grocery_result.get("summary", {})

        col1, col2 = st.columns(2)

        col1.metric(
            "Shopping items",
            summary.get("shopping_items", 0),
        )

        col2.metric(
            "Items to review",
            summary.get("items_to_review", 0),
        )

        st.subheader("Ingredients to buy")

        grocery_items = {
            key: value
            for key, value in grocery_result.items()
            if key != "summary"
        }

        if grocery_items:

            render_grocery_value(grocery_items)

        else:

            st.success(
                "No missing ingredients were returned."
            )

        if summary.get("items_to_review", 0):

            st.warning(
                "Some grocery quantities or ingredient matches need review. "
                "Check the details above."
            )

        with st.expander("Grocery calculation details"):
            st.json(grocery_result)
