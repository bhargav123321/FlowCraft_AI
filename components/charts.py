import streamlit as st
import pandas as pd
import plotly.express as px


def render_aggregation_chart(
    df: pd.DataFrame,
    group_by: list,
    aggregate_column: str,
    aggregation: str,
    title: str = "Aggregation Chart"
):
    """
    Automatically generate and display an interactive visual chart for an aggregation result.
    """
    if df is None or df.empty:
        st.info("No data available to plot.")
        return

    try:
        # Determine group column and value column
        group_col = group_by[0] if (group_by and group_by[0] in df.columns) else df.columns[0]
        val_cols = [c for c in df.columns if c not in group_by]
        val_col = val_cols[0] if val_cols else df.columns[-1]

        # Choose chart format based on cardinality
        num_categories = df[group_col].nunique()

        if aggregation == "count" and num_categories <= 6:
            fig = px.pie(
                df,
                names=group_col,
                values=val_col,
                title=title,
                hole=0.4,
                template="plotly_dark",
                color_discrete_sequence=px.colors.qualitative.Prism
            )
        else:
            fig = px.bar(
                df,
                x=group_col,
                y=val_col,
                title=title,
                text=val_col,
                template="plotly_dark",
                color=group_col,
                color_discrete_sequence=px.colors.qualitative.Pastel
            )
            fig.update_traces(textposition="outside")

        fig.update_layout(
            height=380,
            showlegend=(num_categories <= 8),
            margin=dict(l=20, r=20, t=50, b=30),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)"
        )

        st.plotly_chart(fig, use_container_width=True)

    except Exception as error:
        st.caption(f"Chart display note: {error}")


def render_report_charts(report: dict):
    """
    Render visual infographic charts for a generated dataset report.
    """
    if not isinstance(report, dict):
        return

    col1, col2 = st.columns(2)

    # 1. Column Data Types breakdown
    dtype_map = report.get("column_data_types", {})
    if dtype_map:
        with col1:
            st.markdown("##### 🧩 Column Data Types Distribution")
            dtype_counts = pd.Series(list(dtype_map.values())).value_counts().reset_index()
            dtype_counts.columns = ["Data Type", "Count"]

            fig_dtype = px.pie(
                dtype_counts,
                names="Data Type",
                values="Count",
                hole=0.4,
                template="plotly_dark",
                color_discrete_sequence=px.colors.qualitative.Bold
            )
            fig_dtype.update_layout(
                height=320,
                margin=dict(l=10, r=10, t=30, b=10),
                paper_bgcolor="rgba(0,0,0,0)"
            )
            st.plotly_chart(fig_dtype, use_container_width=True)

    # 2. Missing values breakdown
    missing_map = report.get("missing_values_by_column", {})
    with col2:
        if missing_map:
            st.markdown("##### ⚠️ Missing Values by Column")
            missing_df = pd.DataFrame(
                [{"Column": col, "Missing Count": count} for col, count in missing_map.items()]
            ).sort_values("Missing Count", ascending=True)

            fig_missing = px.bar(
                missing_df,
                x="Missing Count",
                y="Column",
                orientation="h",
                text="Missing Count",
                template="plotly_dark",
                color="Missing Count",
                color_continuous_scale="Reds"
            )
            fig_missing.update_layout(
                height=320,
                margin=dict(l=10, r=10, t=30, b=10),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)"
            )
            st.plotly_chart(fig_missing, use_container_width=True)
        else:
            st.markdown("##### 🟢 Data Completeness")
            st.success("100% complete data — zero missing values detected across all columns.")


def render_data_visualizations(df):
    """
    Display interactive visualizations for a DataFrame.
    """
    if df is None or df.empty:
        st.info("No data available for visualization.")
        return

    st.markdown("## 📊 Data Visualization")

    numeric_columns = df.select_dtypes(
        include=["number"]
    ).columns.tolist()

    categorical_columns = df.select_dtypes(
        include=["object", "category", "bool"]
    ).columns.tolist()

    all_columns = df.columns.tolist()

    if not all_columns:
        st.warning("No columns available.")
        return

    # -----------------------------------------
    # CHART CONTROLS
    # -----------------------------------------

    chart_type = st.selectbox(
        "Choose Chart Type",
        [
            "Bar Chart",
            "Pie Chart",
            "Histogram",
            "Scatter Plot",
            "Box Plot"
        ],
        key="visualization_chart_type"
    )

    # -----------------------------------------
    # BAR CHART
    # -----------------------------------------

    if chart_type == "Bar Chart":
        col1, col2 = st.columns(2)

        with col1:
            x_column = st.selectbox(
                "Select Category Column",
                all_columns,
                key="bar_x_column"
            )

        with col2:
            y_options = numeric_columns or all_columns
            y_column = st.selectbox(
                "Select Value Column",
                y_options,
                key="bar_y_column"
            )

        try:
            if y_column in numeric_columns and x_column != y_column:
                chart_data = (
                    df.groupby(x_column, dropna=False)[y_column]
                    .mean()
                    .reset_index()
                )
                chart_data.columns = [x_column, f"Average {y_column}"]

                fig = px.bar(
                    chart_data,
                    x=x_column,
                    y=f"Average {y_column}",
                    title=f"Average {y_column} by {x_column}",
                    color=x_column,
                    template="plotly_dark"
                )
            else:
                chart_data = (
                    df[x_column]
                    .fillna("Missing")
                    .value_counts()
                    .reset_index()
                )
                chart_data.columns = [x_column, "Count"]

                fig = px.bar(
                    chart_data,
                    x=x_column,
                    y="Count",
                    title=f"Distribution of {x_column}",
                    color=x_column,
                    template="plotly_dark"
                )

            fig.update_layout(
                height=450,
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)"
            )
            st.plotly_chart(fig, use_container_width=True)

        except Exception as error:
            st.error(f"Unable to create bar chart: {error}")

    # -----------------------------------------
    # PIE CHART
    # -----------------------------------------

    elif chart_type == "Pie Chart":
        category_column = st.selectbox(
            "Select Category Column",
            all_columns,
            key="pie_column"
        )

        try:
            chart_data = (
                df[category_column]
                .fillna("Missing")
                .value_counts()
                .reset_index()
            )
            chart_data.columns = [category_column, "Count"]

            fig = px.pie(
                chart_data,
                names=category_column,
                values="Count",
                title=f"Distribution of {category_column}",
                hole=0.35,
                template="plotly_dark"
            )
            fig.update_layout(
                height=450,
                paper_bgcolor="rgba(0,0,0,0)"
            )
            st.plotly_chart(fig, use_container_width=True)

        except Exception as error:
            st.error(f"Unable to create pie chart: {error}")

    # -----------------------------------------
    # HISTOGRAM
    # -----------------------------------------

    elif chart_type == "Histogram":
        if not numeric_columns:
            st.warning("No numeric columns available.")
            return

        selected_column = st.selectbox(
            "Select Numeric Column",
            numeric_columns,
            key="histogram_column"
        )

        try:
            fig = px.histogram(
                df,
                x=selected_column,
                nbins=30,
                title=f"Distribution of {selected_column}",
                template="plotly_dark",
                color_discrete_sequence=["#8B5CF6"]
            )
            fig.update_layout(
                height=450,
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)"
            )
            st.plotly_chart(fig, use_container_width=True)

        except Exception as error:
            st.error(f"Unable to create histogram: {error}")

    # -----------------------------------------
    # SCATTER PLOT
    # -----------------------------------------

    elif chart_type == "Scatter Plot":
        if len(numeric_columns) < 2:
            st.warning("At least two numeric columns are required.")
            return

        col1, col2 = st.columns(2)

        with col1:
            x_column = st.selectbox(
                "X-axis",
                numeric_columns,
                index=0,
                key="scatter_x"
            )

        with col2:
            y_options = [c for c in numeric_columns if c != x_column] or numeric_columns
            y_column = st.selectbox(
                "Y-axis",
                y_options,
                index=0,
                key="scatter_y"
            )

        try:
            color_opt = categorical_columns[0] if categorical_columns else None
            fig = px.scatter(
                df,
                x=x_column,
                y=y_column,
                color=color_opt,
                title=f"{y_column} vs {x_column}",
                template="plotly_dark"
            )
            fig.update_layout(
                height=450,
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)"
            )
            st.plotly_chart(fig, use_container_width=True)

        except Exception as error:
            st.error(f"Unable to create scatter plot: {error}")

    # -----------------------------------------
    # BOX PLOT
    # -----------------------------------------

    elif chart_type == "Box Plot":
        if not numeric_columns:
            st.warning("No numeric columns available.")
            return

        col1, col2 = st.columns(2)

        with col1:
            numeric_column = st.selectbox(
                "Select Numeric Column",
                numeric_columns,
                key="box_numeric"
            )

        with col2:
            category_column = st.selectbox(
                "Group By",
                ["None"] + all_columns,
                key="box_category"
            )

        try:
            if category_column == "None":
                fig = px.box(
                    df,
                    y=numeric_column,
                    title=f"Distribution of {numeric_column}",
                    template="plotly_dark",
                    color_discrete_sequence=["#6366F1"]
                )
            else:
                fig = px.box(
                    df,
                    x=category_column,
                    y=numeric_column,
                    title=f"{numeric_column} by {category_column}",
                    template="plotly_dark",
                    color=category_column
                )

            fig.update_layout(
                height=450,
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)"
            )
            st.plotly_chart(fig, use_container_width=True)

        except Exception as error:
            st.error(f"Unable to create box plot: {error}")
