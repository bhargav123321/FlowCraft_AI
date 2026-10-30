"""
Workflow Pipeline Diagram Generator for FlowCraft AI.

Renders high-resolution, production-quality visual pipeline diagrams as PNG images
using Pillow (PIL), replacing any raw code or JSON displays with intuitive graphics.
"""

import io
import os
import streamlit as st
from PIL import Image, ImageDraw, ImageFont


# Visual operation metadata
OPERATION_META = {
    "remove_duplicates": {
        "title": "Remove Duplicates",
        "tag": "Deduplicate",
        "color": (16, 185, 129),      # Emerald
        "bg": (20, 39, 41),
    },
    "drop_missing": {
        "title": "Drop Missing Values",
        "tag": "Clean Missing",
        "color": (245, 158, 11),      # Amber
        "bg": (42, 34, 25),
    },
    "filter_rows": {
        "title": "Filter Rows",
        "tag": "Data Filter",
        "color": (168, 85, 247),      # Purple
        "bg": (38, 26, 54),
    },
    "validate_range": {
        "title": "Validate Numeric Range",
        "tag": "Range Check",
        "color": (59, 130, 246),      # Blue
        "bg": (22, 35, 58),
    },
    "group_aggregate": {
        "title": "Group and Aggregate",
        "tag": "Aggregation",
        "color": (236, 72, 153),      # Pink/Magenta
        "bg": (45, 24, 42),
    },
    "sort_rows": {
        "title": "Sort Rows",
        "tag": "Ordering",
        "color": (14, 165, 233),      # Sky Blue
        "bg": (20, 36, 52),
    },
    "generate_report": {
        "title": "Generate Report",
        "tag": "Summary Report",
        "color": (34, 197, 94),       # Green
        "bg": (21, 40, 32),
    },
}

DEFAULT_META = {
    "title": "Workflow Step",
    "tag": "Operation",
    "color": (129, 140, 248),         # Indigo
    "bg": (27, 31, 56),
}


def _get_font(size: int, bold: bool = False) -> ImageFont.ImageFont:
    """Safely obtain a high quality TrueType font, or fallback to default."""
    font_candidates = (
        ["C:/Windows/Fonts/segoeuib.ttf", "C:/Windows/Fonts/arialbd.ttf", "C:/Windows/Fonts/calibrib.ttf"]
        if bold
        else ["C:/Windows/Fonts/segoeui.ttf", "C:/Windows/Fonts/arial.ttf", "C:/Windows/Fonts/calibri.ttf"]
    )
    for candidate in font_candidates:
        if os.path.exists(candidate):
            try:
                return ImageFont.truetype(candidate, size)
            except Exception:
                continue
    try:
        return ImageFont.load_default()
    except Exception:
        return None


def generate_workflow_diagram(
    steps: list,
    workflow_name: str = "Workflow Execution Pipeline",
    dataset_name: str = "Dataset",
    status: str = "Completed"
) -> bytes:
    """
    Generate an elegant visual pipeline diagram image for a list of workflow steps.
    Returns PNG image bytes suitable for `st.image` and download buttons.
    """
    width = 1000
    card_width = 880
    card_x = (width - card_width) // 2
    step_card_height = 92
    connector_height = 36
    header_height = 140
    io_node_height = 54
    footer_height = 50

    total_steps = max(1, len(steps))
    total_height = (
        header_height
        + io_node_height           # Input node
        + connector_height
        + (total_steps * step_card_height)
        + ((total_steps - 1) * connector_height)
        + connector_height
        + io_node_height           # Output node
        + footer_height
    )

    # 1. Canvas initialization
    img = Image.new("RGBA", (width, total_height), (11, 16, 32, 255))
    draw = ImageDraw.Draw(img)

    # Fonts
    title_font = _get_font(24, bold=True)
    subtitle_font = _get_font(13, bold=False)
    node_title_font = _get_font(15, bold=True)
    node_body_font = _get_font(12, bold=False)
    badge_font = _get_font(11, bold=True)
    small_tag_font = _get_font(10, bold=True)

    # Header gradient banner
    banner_height = 110
    draw.rounded_rectangle(
        [(card_x, 20), (card_x + card_width, banner_height)],
        radius=14,
        fill=(30, 27, 75, 255),
        outline=(99, 102, 241, 180),
        width=2
    )

    # Top Tag
    draw.rounded_rectangle(
        [(card_x + 20, 32), (card_x + 180, 54)],
        radius=11,
        fill=(79, 70, 229, 220)
    )
    draw.text((card_x + 32, 36), "FLOWCRAFT AI PIPELINE", fill=(255, 255, 255, 255), font=small_tag_font)

    # Workflow title
    clean_title = workflow_name if workflow_name else "Workflow Pipeline"
    if len(clean_title) > 48:
        clean_title = clean_title[:45] + "..."
    draw.text((card_x + 20, 62), f"⚡ {clean_title}", fill=(255, 255, 255, 255), font=title_font)

    # Header status badge (Right side)
    is_completed = str(status).lower() == "completed"
    badge_text = "EXECUTION SUCCESSFUL ✓" if is_completed else "READY TO EXECUTE ⚡"
    badge_color = (16, 185, 129, 230) if is_completed else (245, 158, 11, 230)
    badge_w = 190
    draw.rounded_rectangle(
        [(card_x + card_width - badge_w - 20, 48), (card_x + card_width - 20, 80)],
        radius=12,
        fill=badge_color
    )
    draw.text((card_x + card_width - badge_w - 6, 56), badge_text, fill=(255, 255, 255, 255), font=badge_font)

    current_y = header_height

    # 2. Input Dataset Node
    draw.rounded_rectangle(
        [(card_x + 100, current_y), (card_x + card_width - 100, current_y + io_node_height)],
        radius=12,
        fill=(23, 31, 54, 255),
        outline=(71, 85, 105, 255),
        width=1
    )
    draw.text(
        (card_x + 120, current_y + 16),
        f"📂 Input Dataset:  {dataset_name or 'Uploaded CSV'}",
        fill=(226, 232, 240, 255),
        font=node_title_font
    )
    draw.rounded_rectangle(
        [(card_x + card_width - 210, current_y + 14), (card_x + card_width - 120, current_y + io_node_height - 14)],
        radius=10,
        fill=(51, 65, 85, 255)
    )
    draw.text((card_x + card_width - 198, current_y + 19), "SOURCE DATA", fill=(148, 163, 184, 255), font=small_tag_font)

    current_y += io_node_height

    # Helper: draw connector arrow
    def draw_connector(start_y, height):
        mid_x = width // 2
        draw.line([(mid_x, start_y), (mid_x, start_y + height - 8)], fill=(99, 102, 241, 200), width=3)
        arrow_y = start_y + height - 8
        draw.polygon(
            [(mid_x - 6, arrow_y), (mid_x + 6, arrow_y), (mid_x, arrow_y + 8)],
            fill=(129, 140, 248, 255)
        )

    # 3. Steps Loop
    draw_connector(current_y, connector_height)
    current_y += connector_height

    for idx, step in enumerate(steps, start=1):
        op = step.get("operation", "unknown") if isinstance(step, dict) else getattr(step, "operation", "unknown")
        desc = step.get("description", "") if isinstance(step, dict) else getattr(step, "description", "")
        meta = OPERATION_META.get(op, DEFAULT_META)

        # Build detailed parameter summary text
        param_details = []
        col = step.get("column") if isinstance(step, dict) else getattr(step, "column", None)
        cond = step.get("condition") if isinstance(step, dict) else getattr(step, "condition", None)
        val = step.get("value") if isinstance(step, dict) else getattr(step, "value", None)
        grp = step.get("group_by") if isinstance(step, dict) else getattr(step, "group_by", None)
        agg_col = step.get("aggregate_column") if isinstance(step, dict) else getattr(step, "aggregate_column", None)
        agg = step.get("aggregation") if isinstance(step, dict) else getattr(step, "aggregation", None)

        if col:
            param_details.append(f"Column: {col}")
        if cond and val is not None:
            param_details.append(f"{cond.replace('_', ' ')} {val}")
        if grp:
            param_details.append(f"Group: {', '.join(grp)}")
        if agg_col and agg:
            param_details.append(f"Calc: {agg} of {agg_col}")

        detail_str = " | ".join(param_details) if param_details else desc
        if len(detail_str) > 75:
            detail_str = detail_str[:72] + "..."

        # Step card container
        card_rect = [(card_x, current_y), (card_x + card_width, current_y + step_card_height)]
        draw.rounded_rectangle(
            card_rect,
            radius=14,
            fill=(20, 27, 45, 255),
            outline=meta["color"] + (180,),
            width=2
        )

        # Step Number badge (Left pill)
        step_badge_w = 64
        draw.rounded_rectangle(
            [(card_x + 16, current_y + 18), (card_x + 16 + step_badge_w, current_y + step_card_height - 18)],
            radius=10,
            fill=meta["color"] + (230,)
        )
        draw.text(
            (card_x + 28, current_y + 35),
            f"{idx:02d}",
            fill=(255, 255, 255, 255),
            font=_get_font(18, bold=True)
        )

        # Step title and tag
        title_x = card_x + 94
        draw.text(
            (title_x, current_y + 20),
            meta["title"],
            fill=(248, 250, 252, 255),
            font=node_title_font
        )
        draw.text(
            (title_x, current_y + 48),
            detail_str or meta["tag"],
            fill=(148, 163, 184, 255),
            font=node_body_font
        )

        # Status badge (Right pill)
        step_status = "COMPLETED ✓" if is_completed else "APPROVED"
        status_color = (16, 185, 129, 255) if is_completed else (99, 102, 241, 255)
        status_w = 115
        draw.rounded_rectangle(
            [(card_x + card_width - status_w - 20, current_y + 32), (card_x + card_width - 20, current_y + 60)],
            radius=8,
            fill=status_color
        )
        draw.text(
            (card_x + card_width - status_w - 10, current_y + 40),
            step_status,
            fill=(255, 255, 255, 255),
            font=badge_font
        )

        current_y += step_card_height

        # Connect to next or output
        if idx < total_steps:
            draw_connector(current_y, connector_height)
            current_y += connector_height

    # 4. Final Output Node
    draw_connector(current_y, connector_height)
    current_y += connector_height

    draw.rounded_rectangle(
        [(card_x + 100, current_y), (card_x + card_width - 100, current_y + io_node_height)],
        radius=12,
        fill=(16, 42, 35, 255),
        outline=(16, 185, 129, 255),
        width=2
    )
    draw.text(
        (card_x + 120, current_y + 16),
        "🎯 Final Outputs: Cleaned Dataset, Aggregations & Charts Ready",
        fill=(167, 243, 208, 255),
        font=node_title_font
    )
    draw.rounded_rectangle(
        [(card_x + card_width - 210, current_y + 14), (card_x + card_width - 120, current_y + io_node_height - 14)],
        radius=10,
        fill=(5, 150, 105, 255)
    )
    draw.text((card_x + card_width - 198, current_y + 19), "SUCCESS", fill=(255, 255, 255, 255), font=small_tag_font)

    current_y += io_node_height + 15

    # 5. Footer
    draw.text(
        (card_x + card_width // 2 - 130, current_y),
        "⚡ FlowCraft AI — Safe Predefined Execution Engine",
        fill=(100, 116, 139, 255),
        font=subtitle_font
    )

    # Convert to PNG buffer
    buffer = io.BytesIO()
    img.save(buffer, format="PNG", optimize=True)
    buffer.seek(0)
    return buffer.getvalue()


def render_workflow_diagram_component(
    steps: list,
    workflow_name: str = "Workflow Pipeline",
    dataset_name: str = "Dataset",
    status: str = "Completed",
    key_prefix: str = "diag"
):
    """
    Render the workflow pipeline diagram image in Streamlit with a download button.
    """
    if not steps:
        return

    png_bytes = generate_workflow_diagram(
        steps=steps,
        workflow_name=workflow_name,
        dataset_name=dataset_name,
        status=status
    )

    st.image(
        png_bytes,
        caption=f"Workflow Pipeline Diagram — {workflow_name}",
        use_container_width=True
    )

    st.download_button(
        "⬇️ Download Pipeline Diagram (PNG Image)",
        data=png_bytes,
        file_name="flowcraft_workflow_pipeline.png",
        mime="image/png",
        key=f"{key_prefix}_download_png"
    )
