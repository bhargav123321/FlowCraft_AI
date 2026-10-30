import streamlit as st
from components.workflow_diagram import render_workflow_diagram_component

# ============================================================
# WORKFLOW OPERATION VISUALS
# ============================================================

OPERATION_DETAILS = {
    "remove_duplicates": {
        "title": "Remove Duplicates",
        "icon": "🧹",
        "color": "🟢",
        "description": "Remove repeated records from the dataset."
    },
    "drop_missing": {
        "title": "Drop Missing Values",
        "icon": "🗑️",
        "color": "🟡",
        "description": "Remove rows containing missing values."
    },
    "filter_rows": {
        "title": "Filter Rows",
        "icon": "🔍",
        "color": "🟣",
        "description": "Filter records using specified conditions."
    },
    "validate_range": {
        "title": "Validate Numeric Range",
        "icon": "📏",
        "color": "🔵",
        "description": "Check whether values are within the allowed range."
    },
    "group_aggregate": {
        "title": "Group and Aggregate",
        "icon": "📊",
        "color": "🟣",
        "description": "Group records and calculate summary statistics."
    },
    "sort_rows": {
        "title": "Sort Rows",
        "icon": "↕️",
        "color": "🔵",
        "description": "Sort records in ascending or descending order."
    },
    "generate_report": {
        "title": "Generate Report",
        "icon": "📑",
        "color": "🟢",
        "description": "Generate a summary report from the dataset."
    }
}


# ============================================================
# WORKFLOW PREVIEW
# ============================================================

def render_workflow_preview(
    steps,
    workflow_name: str = "Generated Workflow",
    dataset_name: str = "Dataset",
    status: str = "Pending",
    show_diagram: bool = True
):
    """
    Render visual workflow preview including a pipeline diagram image and step cards.
    No code or raw JSON is displayed.
    """
    if not steps:
        st.info(
            "✨ No workflow steps generated yet. "
            "Enter a request to generate your workflow."
        )
        return

    # Visual Workflow Pipeline Diagram Image
    if show_diagram:
        st.markdown("### 🖼️ Workflow Pipeline Diagram")
        st.caption("Visual architecture and execution flow for this workflow.")
        render_workflow_diagram_component(
            steps=steps,
            workflow_name=workflow_name,
            dataset_name=dataset_name,
            status=status,
            key_prefix=f"preview_{status.lower()}"
        )
        st.markdown("---")

    st.markdown("### 📋 Step-by-Step Operations")
    st.caption(f"Total operations in sequence: {len(steps)}")

    # Display each workflow step
    for index, step in enumerate(steps, start=1):
        operation = step.get("operation", "unknown") if isinstance(step, dict) else getattr(step, "operation", "unknown")
        description = step.get("description", "") if isinstance(step, dict) else getattr(step, "description", "")

        details = OPERATION_DETAILS.get(
            operation,
            {
                "title": operation.replace("_", " ").title(),
                "icon": "⚙️",
                "color": "⚪",
                "description": "Execute workflow operation."
            }
        )

        with st.container(border=True):
            col1, col2, col3 = st.columns([0.7, 4, 1.2])

            with col1:
                st.markdown(f"### {details['icon']}")

            with col2:
                st.markdown(f"**Step {index}: {details['title']}**")
                st.caption(description or details["description"])

            with col3:
                badge_label = "🟢 Completed" if status.lower() == "completed" else "🟡 Pending Approval"
                st.caption(badge_label)

            # Additional operation parameters
            with st.expander("View operation parameters"):
                col_name = step.get("column") if isinstance(step, dict) else getattr(step, "column", None)
                if col_name:
                    st.write(f"**Target Column:** {col_name}")

                group_by = step.get("group_by") if isinstance(step, dict) else getattr(step, "group_by", None)
                if group_by:
                    st.write(f"**Group By:** {', '.join(group_by)}")

                agg_col = step.get("aggregate_column") if isinstance(step, dict) else getattr(step, "aggregate_column", None)
                if agg_col:
                    st.write(f"**Aggregate Column:** {agg_col}")

                agg = step.get("aggregation") if isinstance(step, dict) else getattr(step, "aggregation", None)
                if agg:
                    st.write(f"**Calculation:** {agg.title()}")

                cond = step.get("condition") if isinstance(step, dict) else getattr(step, "condition", None)
                if cond:
                    st.write(f"**Condition:** {cond.replace('_', ' ').title()}")

                val = step.get("value") if isinstance(step, dict) else getattr(step, "value", None)
                if val is not None:
                    st.write(f"**Comparison Value:** {val}")

                min_v = step.get("min_value") if isinstance(step, dict) else getattr(step, "min_value", None)
                if min_v is not None:
                    st.write(f"**Minimum Value:** {min_v}")

                max_v = step.get("max_value") if isinstance(step, dict) else getattr(step, "max_value", None)
                if max_v is not None:
                    st.write(f"**Maximum Value:** {max_v}")

                sort_o = step.get("sort_order") if isinstance(step, dict) else getattr(step, "sort_order", None)
                if sort_o:
                    st.write(f"**Sort Order:** {sort_o.title()}")

        if index < len(steps):
            st.markdown("<div style='text-align:center;'>⬇️</div>", unsafe_allow_html=True)
