
import pandas as pd
from pandas.api.types import is_numeric_dtype


# ============================================================
# HELPER FUNCTION
# ============================================================

def is_numeric_column(series):
    """Check whether a Pandas Series contains numeric, non-boolean data."""

    return (
        is_numeric_dtype(series)
        and not pd.api.types.is_bool_dtype(series)
    )


# ============================================================
# 1. REMOVE DUPLICATES
# ============================================================

def remove_duplicates(df):
    """Remove duplicate records."""

    result = df.drop_duplicates().copy()

    removed = len(df) - len(result)

    return result, {
        "operation": "Remove Duplicates",
        "rows_affected": removed,
        "input_rows": len(df),
        "output_rows": len(result),
        "message": f"Removed {removed} duplicate records."
    }


# ============================================================
# 2. DROP MISSING VALUES
# ============================================================

def drop_missing(df):
    """Remove rows containing missing values."""

    result = df.dropna().copy()

    removed = len(df) - len(result)

    return result, {
        "operation": "Drop Missing Values",
        "rows_affected": removed,
        "input_rows": len(df),
        "output_rows": len(result),
        "message": (
            f"Removed {removed} rows containing missing values. "
            f"{len(result)} rows remain."
        )
    }


# ============================================================
# 3. FILTER ROWS
# ============================================================

def filter_rows(df, column, condition, value):
    """Filter records using an approved comparison."""

    if column not in df.columns:
        raise ValueError(f"Column not found: {column}")

    series = df[column]

    numeric_conditions = {
        "greater_than",
        "greater_than_or_equal",
        "less_than",
        "less_than_or_equal"
    }

    if condition in numeric_conditions:

        if not is_numeric_column(series):
            raise ValueError(
                f"Numeric filtering cannot be applied to "
                f"categorical column '{column}'."
            )

        try:
            comparison_value = float(value)

        except (TypeError, ValueError) as error:
            raise ValueError(
                "Numeric filtering requires a numeric value."
            ) from error

        if condition == "greater_than":
            mask = series > comparison_value

        elif condition == "greater_than_or_equal":
            mask = series >= comparison_value

        elif condition == "less_than":
            mask = series < comparison_value

        else:
            mask = series <= comparison_value

    elif condition == "equal":

        mask = series.astype(str) == str(value)

    elif condition == "not_equal":

        mask = series.astype(str) != str(value)

    else:

        raise ValueError(
            f"Unsupported filter condition: {condition}"
        )

    result = df.loc[mask.fillna(False)].copy()

    removed = len(df) - len(result)

    return result, {
        "operation": "Filter Rows",
        "rows_affected": removed,
        "input_rows": len(df),
        "output_rows": len(result),
        "message": (
            f"Filtered dataset using {column} {condition} {value}. "
            f"{len(result)} rows remain."
        )
    }


# ============================================================
# 4. VALIDATE NUMERIC RANGE
# ============================================================

def validate_range(df, column, min_value, max_value):
    """
    Identify values outside an allowed numeric range.

    This operation does not remove or modify records.
    """

    if column not in df.columns:
        raise ValueError(f"Column not found: {column}")

    if not is_numeric_column(df[column]):
        raise ValueError(
            f"Range validation requires a numeric column. "
            f"'{column}' is categorical."
        )

    if min_value is None or max_value is None:
        raise ValueError(
            "Both minimum and maximum values are required."
        )

    if min_value > max_value:
        raise ValueError(
            "Minimum value cannot be greater than maximum value."
        )

    numeric = pd.to_numeric(
        df[column],
        errors="coerce"
    )

    invalid_mask = (
        numeric.notna()
        & (
            (numeric < min_value)
            | (numeric > max_value)
        )
    )

    invalid_count = int(invalid_mask.sum())

    return df.copy(), {
        "operation": "Validate Numeric Range",
        "rows_affected": invalid_count,
        "input_rows": len(df),
        "output_rows": len(df),
        "message": (
            f"Found {invalid_count} values outside "
            f"the range {min_value} to {max_value} "
            f"in column '{column}'."
        )
    }


# ============================================================
# 5. GROUP AND AGGREGATE
# ============================================================

def group_aggregate(
    df,
    group_by,
    aggregate_column,
    aggregation
):
    """
    Group records and calculate an aggregation.

    Supported methods:
        mean, sum, min, max, count

    Numeric aggregation results are rounded to 2 decimal places.
    """

    if df is None or df.empty:
        raise ValueError(
            "Cannot aggregate an empty dataset."
        )

    if not group_by:
        raise ValueError(
            "At least one grouping column is required."
        )

    if isinstance(group_by, str):
        group_by = [group_by]

    if not isinstance(group_by, list):
        raise ValueError(
            "group_by must be a list of column names."
        )

    if len(group_by) != len(set(group_by)):
        raise ValueError(
            "Duplicate grouping columns are not allowed."
        )

    for column in group_by:

        if column not in df.columns:
            raise ValueError(
                f"Grouping column not found: {column}"
            )

    if aggregate_column not in df.columns:
        raise ValueError(
            f"Aggregate column not found: {aggregate_column}"
        )

    allowed_aggregations = {
        "mean",
        "sum",
        "min",
        "max",
        "count"
    }

    if aggregation not in allowed_aggregations:
        raise ValueError(
            f"Unsupported aggregation method: {aggregation}"
        )

    numeric_aggregations = {
        "mean",
        "sum",
        "min",
        "max"
    }

    if aggregation in numeric_aggregations:

        if not is_numeric_column(df[aggregate_column]):
            raise ValueError(
                f"Aggregation '{aggregation}' requires a numeric "
                f"column. '{aggregate_column}' is not numeric."
            )

    # Perform grouping and aggregation.
    result = (
        df.groupby(
            group_by,
            dropna=False,
            observed=True
        )
        .agg(
            **{
                f"{aggregate_column}_{aggregation}": (
                    aggregate_column,
                    aggregation
                )
            }
        )
        .reset_index()
    )

    result_column = f"{aggregate_column}_{aggregation}"

    # Round numeric aggregation results to 2 decimal places.
    if aggregation in numeric_aggregations:

        result[result_column] = (
            result[result_column].round(2)
        )

    return result, {
        "operation": "Group and Aggregate",
        "rows_affected": len(result),
        "input_rows": len(df),
        "output_rows": len(result),
        "group_by": group_by,
        "aggregate_column": aggregate_column,
        "aggregation": aggregation,
        "message": (
            f"Grouped by {', '.join(group_by)} and calculated "
            f"{aggregation} of {aggregate_column}. "
            f"Generated {len(result)} groups."
        )
    }


# ============================================================
# 6. SORT ROWS
# ============================================================

def sort_rows(df, column, sort_order):
    """Sort dataset records."""

    if column not in df.columns:
        raise ValueError(
            f"Sorting column not found: {column}"
        )

    if sort_order not in {"ascending", "descending"}:
        raise ValueError(
            "Sort order must be ascending or descending."
        )

    result = df.sort_values(
        by=column,
        ascending=(sort_order == "ascending"),
        na_position="last"
    ).copy()

    return result, {
        "operation": "Sort Rows",
        "rows_affected": len(result),
        "input_rows": len(df),
        "output_rows": len(result),
        "message": (
            f"Sorted records by '{column}' in "
            f"{sort_order} order."
        )
    }


# ============================================================
# 7. GENERATE DATASET REPORT
# ============================================================

def generate_report(df):
    """Generate a basic descriptive dataset report."""

    if df is None:
        raise ValueError(
            "Dataset is not available."
        )

    report = {
        "total_rows": int(len(df)),

        "total_columns": int(len(df.columns)),

        "missing_values": int(
            df.isnull().sum().sum()
        ),

        "duplicate_rows": int(
            df.duplicated().sum()
        ),

        "columns": df.columns.tolist(),

        "column_data_types": {
            column: str(dtype)
            for column, dtype in df.dtypes.items()
        },

        "missing_values_by_column": {
            column: int(count)
            for column, count in df.isnull().sum().items()
            if count > 0
        }
    }

    return df.copy(), {
        "operation": "Generate Report",
        "rows_affected": len(df),
        "input_rows": len(df),
        "output_rows": len(df),
        "message": "Dataset summary report generated.",
        "report": report
    }
