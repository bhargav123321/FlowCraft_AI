
import hashlib
import json
from pathlib import Path

import pandas as pd
import streamlit as st

from components.sidebar import render_sidebar
from components.workflow_preview import render_workflow_preview
from components.charts import render_data_visualizations

from backend.utils.csv_handler import (
    load_csv_file,
    get_dataset_overview,
    get_column_information
)
from backend.utils.validators import analyze_data_quality

from backend.core.workflow_generator import generate_workflow
from backend.core.workflow_schema import WorkflowDefinition
from backend.core.workflow_executor import execute_workflow

from backend.services.history_service import (
    initialize_database,
    save_workflow_history,
    get_workflow_history,
    get_workflow_by_id,
    delete_workflow_history,
    clear_workflow_history
)


# ============================================================
# 1. PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="FlowCraft AI | Workflow Studio",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

initialize_database()


# ============================================================
# 2. CUSTOM CSS
# ============================================================

st.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(
            135deg, #0B1020 0%, #11152A 50%, #17132D 100%
        );
        color: #F1F5F9;
    }

    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 1450px;
    }

    section[data-testid="stSidebar"] {
        background: #10172A;
        border-right: 1px solid #28334F;
    }

    .hero-container {
        padding: 35px;
        border-radius: 22px;
        background: linear-gradient(
            120deg, #31216B, #4338A8, #5B4BE8
        );
        margin-bottom: 28px;
        box-shadow: 0 12px 35px rgba(0,0,0,0.25);
    }

    .hero-title {
        color: white;
        font-size: 38px;
        font-weight: 800;
        margin-bottom: 12px;
    }

    .hero-description {
        color: #E0E7FF;
        font-size: 16px;
        line-height: 1.7;
    }

    .section-heading {
        font-size: 23px;
        font-weight: 750;
        color: #F8FAFC;
        margin-top: 25px;
        margin-bottom: 15px;
    }

    div[data-testid="stMetric"] {
        background: #171F36;
        border: 1px solid #303B5B;
        border-radius: 13px;
        padding: 17px;
    }

    div[data-testid="stMetricLabel"] {
        color: #AAB5CC;
    }

    div[data-testid="stMetricValue"] {
        color: #FFFFFF;
    }

    div.stButton > button {
        border: none;
        border-radius: 10px;
        padding: 11px 20px;
        font-weight: 650;
        background: linear-gradient(100deg, #7C3AED, #6366F1);
        color: white;
        transition: 0.2s ease;
    }

    div.stButton > button:hover {
        background: linear-gradient(100deg, #6D28D9, #4F46E5);
        color: white;
        transform: translateY(-1px);
    }

    hr {
        border-color: #29334D;
    }
    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# 3. SESSION STATE
# ============================================================

DEFAULT_STATE = {
    "dataset": None,
    "dataset_name": None,
    "dataset_fingerprint": None,
    "workflow_request": "",
    "generated_workflow": None,
    "execution_result": None,
    "last_error": None
}

for key, value in DEFAULT_STATE.items():
    if key not in st.session_state:
        st.session_state[key] = value


# ============================================================
# 4. HELPER FUNCTIONS
# ============================================================

def reset_workflow_state():
    st.session_state.generated_workflow = None
    st.session_state.execution_result = None
    st.session_state.last_error = None


def set_dataset(file_bytes, filename):

    fingerprint = hashlib.sha256(file_bytes).hexdigest()

    if fingerprint == st.session_state.dataset_fingerprint:
        return

    dataframe = load_csv_file(file_bytes, filename)

    st.session_state.dataset = dataframe
    st.session_state.dataset_name = filename
    st.session_state.dataset_fingerprint = fingerprint

    reset_workflow_state()

    st.success(f"Successfully loaded {filename}.")


# ============================================================
# 5. DATASET OVERVIEW
# ============================================================

def show_dataset_overview(df):

    overview = get_dataset_overview(df)

    st.markdown("## 📊 Dataset Overview")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total Rows", f"{overview['total_rows']:,}")
    col2.metric("Total Columns", overview["total_columns"])
    col3.metric("Missing Values", overview["missing_values"])
    col4.metric("Duplicate Rows", overview["duplicate_rows"])

    st.markdown("### Dataset Preview")

    st.dataframe(
        df.head(10),
        use_container_width=True,
        hide_index=True
    )

    st.markdown("### Column Information")

    column_info = get_column_information(df)

    st.dataframe(
        column_info,
        use_container_width=True,
        hide_index=True
    )

    st.markdown("### Data Quality Analysis")

    quality_report = analyze_data_quality(df)

    if quality_report.empty:
        st.success("No issues detected by configured checks.")
    else:
        st.dataframe(
            quality_report,
            use_container_width=True,
            hide_index=True
        )

        st.download_button(
            "⬇️ Download Data Quality Report",
            data=quality_report.to_csv(index=False),
            file_name="data_quality_report.csv",
            mime="text/csv"
        )


# ============================================================
# 6. EXECUTION RESULTS
# ============================================================

def show_execution_logs(logs):

    st.markdown("## 📋 Execution Summary")

    if not logs:
        st.info("No execution details available.")
        return

    operation_names = {
        "remove_duplicates": "Remove duplicate records",
        "drop_missing": "Remove missing values",
        "filter_rows": "Filter records",
        "validate_range": "Validate value ranges",
        "group_aggregate": "Group and summarize data",
        "sort_rows": "Sort records",
        "generate_report": "Generate data report"
    }

    for index, log in enumerate(logs, start=1):

        if not isinstance(log, dict):
            continue

        operation = log.get("operation", "")
        friendly_name = operation_names.get(
            operation, "Data processing"
        )

        with st.container(border=True):

            st.markdown(
                f"**Step {log.get('step_number', index)}: {friendly_name}**"
            )

            message = log.get("message", "")

            if message:
                st.write(message)

            rows_affected = log.get("rows_affected")

            if rows_affected is not None:
                st.caption(f"Records affected: {rows_affected}")


def show_aggregation_results(aggregation_results):

    if not aggregation_results:
        return

    st.markdown("## 📊 Aggregation Results")

    for index, item in enumerate(aggregation_results, start=1):

        description = item.get(
            "description", "Aggregation Result"
        )

        result_df = item.get("result_df")

        st.markdown(f"### {description}")

        if not isinstance(result_df, pd.DataFrame):
            st.warning("Aggregation result is unavailable.")
            continue

        if result_df.empty:
            st.info("This aggregation returned no records.")
            continue

        st.dataframe(
            result_df,
            use_container_width=True,
            hide_index=True
        )

        st.download_button(
            f"⬇️ Download Aggregation {index}",
            data=result_df.to_csv(index=False),
            file_name=f"aggregation_{index}.csv",
            mime="text/csv",
            key=f"aggregation_download_{index}"
        )


def show_generated_reports(reports):

    if not reports:
        return

    st.markdown("## 📑 Generated Reports")

    for index, report in enumerate(reports, start=1):

        if not isinstance(report, dict):
            continue

        with st.container(border=True):

            st.markdown(f"### 📊 Dataset Summary — Report {index}")

            col1, col2, col3, col4 = st.columns(4)

            col1.metric(
                "Total Rows",
                report.get("total_rows", 0)
            )

            col2.metric(
                "Total Columns",
                report.get("total_columns", 0)
            )

            col3.metric(
                "Missing Values",
                report.get("missing_values", 0)
            )

            col4.metric(
                "Duplicate Rows",
                report.get("duplicate_rows", 0)
            )

            columns = report.get("columns", [])

            if columns:
                dtype_map = report.get("column_data_types", {})

                column_table = pd.DataFrame({
                    "Column Name": columns,
                    "Data Type": [
                        dtype_map.get(column, "Unknown")
                        for column in columns
                    ]
                })

                st.markdown("#### Dataset Columns")

                st.dataframe(
                    column_table,
                    use_container_width=True,
                    hide_index=True
                )

            missing_by_column = report.get(
                "missing_values_by_column", {}
            )

            if missing_by_column:

                missing_table = pd.DataFrame([
                    {
                        "Column Name": column,
                        "Missing Values": count
                    }
                    for column, count in missing_by_column.items()
                ])

                st.markdown("#### Missing Values by Column")

                st.dataframe(
                    missing_table,
                    use_container_width=True,
                    hide_index=True
                )


def show_execution_results(execution_result):

    if not execution_result:
        return

    result_df = execution_result.get("result_df")
    execution_logs = execution_result.get("execution_logs", [])
    aggregation_results = execution_result.get(
        "aggregation_results", []
    )
    generated_reports = execution_result.get(
        "generated_reports", []
    )

    st.markdown("---")
    st.markdown("## 🎉 Workflow Execution Completed")

    st.success("Your approved workflow executed successfully.")

    if isinstance(result_df, pd.DataFrame):

        col1, col2 = st.columns(2)

        col1.metric("Processed Rows", f"{len(result_df):,}")
        col2.metric("Processed Columns", len(result_df.columns))

        st.markdown("### 📄 Processed Dataset")

        st.dataframe(
            result_df,
            use_container_width=True,
            hide_index=True
        )

        st.download_button(
            "⬇️ Download Processed CSV",
            data=result_df.to_csv(index=False),
            file_name="flowcraft_processed_dataset.csv",
            mime="text/csv",
            key="processed_csv_download"
        )

    show_aggregation_results(aggregation_results)

    if isinstance(result_df, pd.DataFrame) and not result_df.empty:

        with st.expander(
            "📈 Visualize Processed Dataset",
            expanded=True
        ):
            render_data_visualizations(result_df)

    show_execution_logs(execution_logs)
    show_generated_reports(generated_reports)


# ============================================================
# 7. SIDEBAR NAVIGATION
# ============================================================

selected_page = render_sidebar()


# ============================================================
# 8. DASHBOARD
# ============================================================

if selected_page == "Dashboard":

    hero_image_path = (
        Path(__file__).parent
        / "assets"
        / "flowcraft_hero.png"
    )

    if hero_image_path.exists():

        st.image(
            str(hero_image_path),
            use_container_width=True
        )

    else:

        st.title("⚡ FlowCraft AI")

        st.write(
            "Transform natural language into executable data workflows. "
            "Upload your CSV, describe what you want, review the generated "
            "workflow, and execute it safely."
        )

    st.markdown("---")

    st.markdown("## 📂 Upload Your Dataset")

    upload_col, sample_col = st.columns([2, 1])

    with upload_col:

        uploaded_file = st.file_uploader(
            "Choose a CSV file",
            type=["csv"],
            help="Maximum upload size: 20 MB."
        )

        if uploaded_file is not None:

            try:
                set_dataset(
                    uploaded_file.getvalue(),
                    uploaded_file.name
                )

            except Exception as error:
                st.error(f"Unable to load CSV: {error}")

    with sample_col:

        st.markdown("#### Try Sample Dataset")

        if st.button(
            "📚 Load Sample Dataset",
            use_container_width=True
        ):

            sample_path = (
                Path(__file__).parent
                / "data"
                / "sample"
                / "students.csv"
            )

            try:

                if not sample_path.exists():
                    raise FileNotFoundError(
                        "Sample dataset not found."
                    )

                st.session_state.dataset_fingerprint = None

                set_dataset(
                    sample_path.read_bytes(),
                    "students.csv"
                )

                st.rerun()

            except Exception as error:
                st.error(f"Unable to load sample dataset: {error}")

    if st.session_state.dataset is not None:

        df = st.session_state.dataset

        st.markdown("---")

        st.success(
            f"Dataset loaded: {st.session_state.dataset_name}"
        )

        show_dataset_overview(df)

        st.markdown("---")

        st.markdown("## 🧠 Describe Your Workflow")

        st.caption(
            "Explain what you want to do with your uploaded dataset."
        )

        example_prompts = [
            "Remove duplicates, drop missing values, and generate a report.",
            "Filter students with attendance greater than 75 and marks greater than 50.",
            "Calculate department-wise average marks and average attendance.",
            "Count students by placement status.",
            "Clean the dataset, analyze placement status and generate a report."
        ]

        example = st.selectbox(
            "Choose an example",
            ["Select an example"] + example_prompts,
            key="workflow_example"
        )

        if st.button("Use This Example", key="use_example"):

            if example != "Select an example":

                st.session_state.workflow_request = example
                st.session_state.generated_workflow = None
                st.session_state.execution_result = None

                st.rerun()

        workflow_request = st.text_area(
            "Describe your workflow",
            key="workflow_request",
            height=130,
            placeholder=(
                "Example: Remove duplicate rows, filter students "
                "whose marks are above 70, calculate department-wise "
                "average marks and generate a report."
            )
        )

        if st.button(
            "✨ Generate Workflow",
            use_container_width=True,
            key="generate_workflow_button"
        ):

            if not workflow_request.strip():

                st.warning("Please describe the workflow first.")

            else:

                try:

                    with st.spinner(
                        "FlowCraft AI is generating your workflow..."
                    ):

                        workflow = generate_workflow(
                            workflow_request,
                            df
                        )

                        st.session_state.generated_workflow = (
                            workflow.model_dump()
                        )

                        st.session_state.execution_result = None
                        st.session_state.last_error = None

                    st.success("Workflow generated successfully!")

                except Exception as error:

                    st.session_state.generated_workflow = None

                    st.error(
                        f"Workflow generation failed: {error}"
                    )

        if st.session_state.generated_workflow is not None:

            workflow_data = st.session_state.generated_workflow

            st.markdown("---")
            st.markdown("## 🔍 Review Generated Workflow")

            st.markdown(
                f"### {workflow_data.get('workflow_name', 'Generated Workflow')}"
            )

            st.write(workflow_data.get("description", ""))

            render_workflow_preview(
                workflow_data.get("steps", [])
            )

            st.markdown("---")
            st.markdown("## 🚀 Approve and Execute Workflow")

            st.info(
                "Review the generated workflow before execution. "
                "Execution processes a copy of your uploaded dataset."
            )

            if st.button(
                "✅ Approve and Execute",
                use_container_width=True,
                key="approve_execute_button"
            ):

                try:

                    with st.spinner(
                        "Executing approved workflow..."
                    ):

                        validated_workflow = (
                            WorkflowDefinition.model_validate(
                                workflow_data
                            )
                        )

                        execution_result = execute_workflow(
                            validated_workflow,
                            st.session_state.dataset.copy()
                        )

                        st.session_state.execution_result = (
                            execution_result
                        )

                        st.session_state.last_error = None

                        save_workflow_history(
                            workflow_name=workflow_data.get(
                                "workflow_name",
                                "Untitled Workflow"
                            ),
                            description=workflow_data.get(
                                "description", ""
                            ),
                            user_request=st.session_state.workflow_request,
                            dataset_name=st.session_state.dataset_name,
                            workflow_steps=workflow_data,
                            execution_status="Completed",
                            execution_logs=execution_result.get(
                                "execution_logs", []
                            )
                        )

                    st.success(
                        "Workflow executed and saved successfully!"
                    )

                except Exception as error:

                    st.session_state.execution_result = None
                    st.session_state.last_error = str(error)

                    st.error(f"Execution failed: {error}")

            if st.session_state.execution_result is not None:

                show_execution_results(
                    st.session_state.execution_result
                )

    else:

        st.info(
            "Upload a CSV file or load the sample dataset "
            "to start creating workflows."
        )


# ============================================================
# 9. WORKFLOW HISTORY - VISUAL DISPLAY
# ============================================================

elif selected_page == "Workflow History":

    st.title("🕘 Workflow History")

    st.caption(
        "View and manage your previously completed workflows."
    )

    history = get_workflow_history()

    if not history:

        st.info(
            "No workflow history found. "
            "Execute a workflow to see it here."
        )

    else:

        completed_count = sum(
            1 for item in history
            if item.get("execution_status") == "Completed"
        )

        other_count = len(history) - completed_count

        st.markdown("## 📊 History Overview")

        col1, col2, col3 = st.columns(3)

        col1.metric("Total Executions", len(history))
        col2.metric("Successful Executions", completed_count)
        col3.metric("Other Executions", other_count)

        st.markdown("---")
        st.markdown("## Previous Workflows")

        history_table = pd.DataFrame([
            {
                "Workflow": item.get(
                    "workflow_name", "Untitled Workflow"
                ),
                "Dataset": item.get("dataset_name", "Unknown"),
                "Steps": item.get("total_steps", 0),
                "Status": item.get("execution_status", "Unknown"),
                "Execution Time": item.get("execution_time", "")
            }
            for item in history
        ])

        st.dataframe(
            history_table,
            use_container_width=True,
            hide_index=True
        )

        st.markdown("---")
        st.markdown("## 🔍 Workflow Details")

        workflow_options = {
            (
                f"{item.get('workflow_name', 'Untitled Workflow')} "
                f"(#{item['id']})"
            ): item["id"]
            for item in history
        }

        selected_workflow = st.selectbox(
            "Choose a workflow to view its details",
            list(workflow_options.keys()),
            key="history_workflow_selector"
        )

        selected_id = workflow_options[selected_workflow]

        selected_record = get_workflow_by_id(selected_id)

        if selected_record is not None:

            with st.container(border=True):

                st.markdown(
                    f"### {selected_record.get('workflow_name', 'Untitled Workflow')}"
                )

                st.write(
                    selected_record.get("description")
                    or "No description available."
                )

                info_col1, info_col2 = st.columns(2)

                with info_col1:

                    st.caption("DATASET")

                    st.write(
                        selected_record.get("dataset_name", "Unknown")
                    )

                    st.caption("EXECUTION TIME")

                    st.write(
                        selected_record.get("execution_time", "Unknown")
                    )

                with info_col2:

                    st.caption("STATUS")

                    status = selected_record.get(
                        "execution_status", "Unknown"
                    )

                    if status == "Completed":
                        st.success(status)
                    else:
                        st.warning(status)

                    st.caption("TOTAL STEPS")

                    st.write(
                        selected_record.get("total_steps", 0)
                    )

            st.markdown("### 💬 Original Request")

            st.info(
                selected_record.get("user_request")
                or "No original request is available."
            )

            # Read stored workflow information internally.
            # Never display the raw JSON to the user.

            workflow_data = selected_record.get(
                "workflow_steps", {}
            )

            if isinstance(workflow_data, str):

                try:
                    workflow_data = json.loads(workflow_data)

                except (TypeError, ValueError):
                    workflow_data = {}

            if isinstance(workflow_data, dict):
                steps = workflow_data.get("steps", [])

            elif isinstance(workflow_data, list):
                steps = workflow_data

            else:
                steps = []

            operation_names = {
                "remove_duplicates": "Remove duplicate records",
                "drop_missing": "Remove rows with missing values",
                "filter_rows": "Filter records",
                "validate_range": "Validate value ranges",
                "group_aggregate": "Group and summarize data",
                "sort_rows": "Sort records",
                "generate_report": "Generate a data report"
            }

            st.markdown("### ✨ Workflow Steps")

            if steps:

                for index, step in enumerate(steps, start=1):

                    if not isinstance(step, dict):
                        continue

                    operation = step.get("operation", "")

                    friendly_name = operation_names.get(
                        operation,
                        "Data processing"
                    )

                    description = (
                        step.get("description") or friendly_name
                    )

                    with st.container(border=True):

                        step_col, detail_col = st.columns([1, 5])

                        with step_col:
                            st.markdown(f"### {index:02d}")

                        with detail_col:

                            st.markdown(f"**{description}**")

                            st.caption(friendly_name)

            else:

                st.caption(
                    "Step-by-step information is not available "
                    "for this workflow."
                )

            st.markdown("### 📋 Execution Summary")

            execution_logs = selected_record.get(
                "execution_logs", []
            ) or []

            if isinstance(execution_logs, str):

                try:
                    execution_logs = json.loads(execution_logs)

                except (TypeError, ValueError):
                    execution_logs = []

            if execution_logs:

                for index, log in enumerate(
                    execution_logs,
                    start=1
                ):

                    if not isinstance(log, dict):
                        continue

                    operation = log.get("operation", "")

                    friendly_name = operation_names.get(
                        operation,
                        "Data processing"
                    )

                    message = log.get("message", "")

                    rows_affected = log.get("rows_affected")

                    with st.container(border=True):

                        st.markdown(
                            f"**Step {log.get('step_number', index)}: "
                            f"{friendly_name}**"
                        )

                        if message:
                            st.write(message)

                        if rows_affected is not None:

                            try:

                                st.caption(
                                    f"Records affected: "
                                    f"{int(rows_affected):,}"
                                )

                            except (TypeError, ValueError):

                                st.caption(
                                    f"Records affected: {rows_affected}"
                                )

            else:

                st.caption(
                    "No additional execution details are available."
                )

            st.markdown("---")

            if st.button(
                "🗑️ Delete Selected Workflow",
                key=f"delete_workflow_{selected_id}"
            ):

                deleted = delete_workflow_history(selected_id)

                if deleted:

                    st.success(
                        "Workflow history deleted successfully."
                    )

                    st.rerun()

                else:

                    st.warning(
                        "Workflow could not be deleted."
                    )

        st.markdown("---")

        with st.expander("⚠️ Clear All Workflow History"):

            st.warning(
                "This action permanently deletes all saved workflow history."
            )

            confirm_clear = st.checkbox(
                "I understand that this action cannot be undone.",
                key="confirm_clear_history"
            )

            if st.button(
                "Clear All History",
                disabled=not confirm_clear,
                key="clear_all_history"
            ):

                clear_workflow_history()

                st.success(
                    "All workflow history has been cleared."
                )

                st.rerun()


# ============================================================
# 10. TEMPLATES
# ============================================================

elif selected_page == "Templates":

    st.title("📚 Workflow Templates")

    st.caption(
        "Use ready-made workflow instructions to get started faster."
    )

    templates = {

        "Data Cleaning": (
            "Remove duplicate records and drop rows "
            "containing missing values. Generate a report."
        ),

        "Student Performance Analysis": (
            "Filter students with marks greater than 70. "
            "Calculate department-wise average marks."
        ),

        "Attendance Analysis": (
            "Validate attendance between 0 and 100. "
            "Filter students with attendance greater than 75. "
            "Calculate department-wise average attendance."
        ),

        "Placement Analysis": (
            "Group students by placement_status and "
            "count the number of students in each category."
        ),

        "Complete Student Analysis": (
            "Remove duplicates, drop missing values, "
            "validate attendance and marks between 0 and 100, "
            "filter students with attendance greater than 75 "
            "and marks greater than 50, calculate department-wise "
            "average marks and attendance, count students per "
            "placement status, and generate a report."
        )

    }

    for title, prompt in templates.items():

        with st.container(border=True):

            st.markdown(f"### {title}")

            st.write(prompt)

            if st.button(
                f"Use {title}",
                key=f"template_{title}"
            ):

                st.session_state.workflow_request = prompt

                st.session_state.generated_workflow = None

                st.session_state.execution_result = None

                st.success(
                    "Template selected. Open Dashboard to generate it."
                )


# ============================================================
# 11. ABOUT FLOWCRAFT
# ============================================================

elif selected_page == "About FlowCraft":

    st.title("ℹ️ About FlowCraft AI")

    st.markdown(
        """
        ## What is FlowCraft AI?

        FlowCraft AI is a natural-language-to-executable
        workflow application designed to simplify CSV data
        processing and analysis.

        Users describe their requirements in everyday language.
        The AI converts these instructions into a structured
        workflow that is validated and executed using
        predefined Python operations.

        ## Main Features

        - Natural-language workflow generation
        - CSV dataset processing
        - Data cleaning and validation
        - Numeric and categorical filtering
        - Grouping and aggregation
        - Interactive data visualizations
        - Execution summaries
        - Downloadable reports
        - Permanent workflow history using SQLite

        ## Technology Stack
        """
    )

    technologies = pd.DataFrame({
        "Component": [
            "Frontend",
            "Backend",
            "AI Integration",
            "Data Processing",
            "Data Validation",
            "Visualization",
            "Database"
        ],
        "Technology": [
            "Streamlit",
            "Python",
            "Groq API",
            "Pandas",
            "Pydantic",
            "Plotly",
            "SQLite"
        ]
    })

    st.dataframe(
        technologies,
        use_container_width=True,
        hide_index=True
    )

    st.markdown("## Security")

    st.write(
        """
        FlowCraft AI uses structured workflow definitions
        and predefined operations. AI-generated Python code
        is not directly executed.
        """
    )

    st.markdown("## Version")

    st.caption("FlowCraft AI v1.0.0")


# ============================================================
# 12. FOOTER
# ============================================================

st.divider()

st.markdown(
    """
    <div style='text-align:center; color:#7F8BA6; padding:12px;'>
        ⚡ <strong>FlowCraft AI</strong><br>
        Natural Language to Executable Workflow<br>
        Built with Python, Streamlit, Pandas and AI<br>
        © 2026 FlowCraft AI
    </div>
    """,
    unsafe_allow_html=True
)
