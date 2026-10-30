
import pandas as pd
from pandas.api.types import is_numeric_dtype

from backend.core.workflow_schema import WorkflowDefinition


NUMERIC_AGGREGATIONS = {"mean", "sum", "min", "max"}

NUMERIC_FILTER_CONDITIONS = {
    "greater_than",
    "greater_than_or_equal",
    "less_than",
    "less_than_or_equal",
}


def _is_numeric_column(df: pd.DataFrame, column: str) -> bool:
    """Return True only for numeric, non-boolean columns."""

    series = df[column]

    return (
        is_numeric_dtype(series)
        and not pd.api.types.is_bool_dtype(series)
    )


def validate_workflow_columns(
    workflow: WorkflowDefinition,
    df: pd.DataFrame,
) -> bool:
    """Validate workflow parameters against the original dataset."""

    if df is None or df.empty:
        raise ValueError(
            "Dataset is empty. Please upload a valid dataset."
        )

    if not df.columns.is_unique:
        raise ValueError(
            "The dataset contains duplicate column names."
        )

    available_columns = set(df.columns)

    for index, step in enumerate(workflow.steps, start=1):
        operation = step.operation

        # Validate single-column references.
        if step.column is not None:
            if step.column not in available_columns:
                raise ValueError(
                    f"Step {index}: Column '{step.column}' "
                    "does not exist in the dataset."
                )

        # Validate aggregation column.
        if step.aggregate_column is not None:
            if step.aggregate_column not in available_columns:
                raise ValueError(
                    f"Step {index}: Aggregate column "
                    f"'{step.aggregate_column}' does not exist."
                )

        # Validate grouping columns.
        for column in step.group_by:
            if column not in available_columns:
                raise ValueError(
                    f"Step {index}: Grouping column '{column}' "
                    "does not exist in the dataset."
                )

        # Validate numeric filters.
        if (
            operation == "filter_rows"
            and step.condition in NUMERIC_FILTER_CONDITIONS
        ):
            if not _is_numeric_column(df, step.column):
                raise ValueError(
                    f"Step {index}: Numeric filtering requires "
                    f"a numeric column. '{step.column}' is not numeric."
                )

            try:
                float(step.value)
            except (TypeError, ValueError) as error:
                raise ValueError(
                    f"Step {index}: Filter value must be numeric."
                ) from error

        # Validate numeric range checks.
        if operation == "validate_range":
            if not _is_numeric_column(df, step.column):
                raise ValueError(
                    f"Step {index}: Range validation requires "
                    f"a numeric column. '{step.column}' is not numeric."
                )

        # Validate aggregation data types.
        if operation == "group_aggregate":
            if step.aggregation in NUMERIC_AGGREGATIONS:
                if not _is_numeric_column(
                    df,
                    step.aggregate_column,
                ):
                    raise ValueError(
                        f"Step {index}: Aggregation "
                        f"'{step.aggregation}' requires a numeric "
                        f"column. '{step.aggregate_column}' is not numeric. "
                        "Use 'count' for categorical columns."
                    )

        # Validate sorting parameters.
        if operation == "sort_rows":
            if step.sort_order not in {"ascending", "descending"}:
                raise ValueError(
                    f"Step {index}: Invalid sort order."
                )

    return True
