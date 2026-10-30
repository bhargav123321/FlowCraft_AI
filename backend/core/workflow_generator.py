
import json
import re

import pandas as pd
from pandas.api.types import is_numeric_dtype
from pydantic import ValidationError

from backend.services.llm_service import generate_ai_response
from backend.core.workflow_schema import WorkflowDefinition
from backend.core.workflow_validator import validate_workflow_columns


MAX_GENERATION_ATTEMPTS = 2


def is_numeric_column(series):
    """Check whether a column contains numeric, non-boolean data."""

    return (
        is_numeric_dtype(series)
        and not pd.api.types.is_bool_dtype(series)
    )


# ============================================================
# SYSTEM PROMPT
# ============================================================

SYSTEM_PROMPT = """
You are FlowCraft AI, an intelligent and safe data workflow generator.

Your task is to convert natural-language instructions into
structured JSON workflows for processing CSV datasets.

IMPORTANT SECURITY RULES:

1. Return valid JSON only.
2. Do not return Markdown or explanations outside JSON.
3. Never generate Python code, SQL, shell commands or scripts.
4. Use only approved operations.
5. Use only columns supplied in DATASET INFORMATION.
6. Never invent column names or data values.
7. Follow the requested operation order.
8. Generate between 1 and 20 workflow steps.
9. Do not add extra JSON properties.

APPROVED OPERATIONS:

- remove_duplicates
- drop_missing
- filter_rows
- validate_range
- group_aggregate
- sort_rows
- generate_report

APPROVED FILTER CONDITIONS:

- greater_than
- greater_than_or_equal
- less_than
- less_than_or_equal
- equal
- not_equal

APPROVED AGGREGATION METHODS:

- mean
- sum
- min
- max
- count

APPROVED SORT ORDERS:

- ascending
- descending

DATA TYPE RULES:

1. Read the data type of every column from DATASET INFORMATION.

2. Numeric columns can be used for:
   - Numeric filtering
   - Range validation
   - mean, sum, min and max aggregations
   - count aggregation

3. Categorical or text columns can be used for:
   - Equal and not_equal filtering
   - Grouping
   - Count aggregation
   - Sorting

4. Never use mean, sum, min or max on text columns.

5. Never use numeric filtering or range validation on text columns.

6. A column such as placement_status is categorical.

7. A column such as department or city is categorical.

MANDATORY GROUP AGGREGATION RULES:

Every group_aggregate operation MUST contain:

1. group_by: A non-empty list of valid dataset columns.
2. aggregate_column: A valid dataset column.
3. aggregation: One approved aggregation method.

Never return an incomplete group_aggregate operation.

Never use null or an empty list for group_by in a group_aggregate step.

For counting students, use student_id as aggregate_column.

EXAMPLE 1: COUNT BY PLACEMENT STATUS

{
  "operation": "group_aggregate",
  "description": "Count students by placement status",
  "column": null,
  "condition": null,
  "value": null,
  "min_value": null,
  "max_value": null,
  "group_by": ["placement_status"],
  "aggregate_column": "student_id",
  "aggregation": "count",
  "sort_order": null
}

EXAMPLE 2: DEPARTMENT-WISE STUDENT COUNT

{
  "operation": "group_aggregate",
  "description": "Count students by department",
  "column": null,
  "condition": null,
  "value": null,
  "min_value": null,
  "max_value": null,
  "group_by": ["department"],
  "aggregate_column": "student_id",
  "aggregation": "count",
  "sort_order": null
}

EXAMPLE 3: COMPANY-WISE AVERAGE PACKAGE

{
  "operation": "group_aggregate",
  "description": "Calculate average package by company",
  "column": null,
  "condition": null,
  "value": null,
  "min_value": null,
  "max_value": null,
  "group_by": ["company"],
  "aggregate_column": "package_lpa",
  "aggregation": "mean",
  "sort_order": null
}

EXAMPLE 4: COMPANY-WISE HIGHEST PACKAGE

{
  "operation": "group_aggregate",
  "description": "Find highest package by company",
  "column": null,
  "condition": null,
  "value": null,
  "min_value": null,
  "max_value": null,
  "group_by": ["company"],
  "aggregate_column": "package_lpa",
  "aggregation": "max",
  "sort_order": null
}

OPERATION REQUIREMENTS:

remove_duplicates:
Remove duplicate records.

drop_missing:
Remove rows containing missing values.

filter_rows:
Requires column, condition and value.

validate_range:
Requires column, min_value and max_value.

group_aggregate:
Requires group_by, aggregate_column and aggregation.

sort_rows:
Requires column and sort_order.

generate_report:
Generate a basic report from the processed dataset.

IMPORTANT OPTIONAL FIELD RULE:

For operations that do not require grouping, use:

"group_by": []

For operations that require grouping, use a non-empty list.

For fields not needed by an operation, use null.

REQUIRED JSON STRUCTURE:

{
  "workflow_name": "Placement Analysis",
  "description": "Analyze student placement data",
  "steps": [
    {
      "operation": "group_aggregate",
      "description": "Count students by placement status",
      "column": null,
      "condition": null,
      "value": null,
      "min_value": null,
      "max_value": null,
      "group_by": ["placement_status"],
      "aggregate_column": "student_id",
      "aggregation": "count",
      "sort_order": null
    }
  ]
}

Return only the complete JSON object.
"""


# ============================================================
# DATASET INFORMATION
# ============================================================

def get_dataset_information(dataframe):
    """Collect dataset information for the AI model."""

    columns = []

    for column in dataframe.columns:

        series = dataframe[column]

        numeric = is_numeric_column(series)

        sample_values = (
            series.dropna()
            .astype(str)
            .drop_duplicates()
            .head(5)
            .tolist()
        )

        columns.append({
            "name": str(column),

            "data_type": str(series.dtype),

            "column_category": (
                "numeric"
                if numeric
                else "categorical_or_text"
            ),

            "missing_values": int(series.isnull().sum()),

            "unique_values": int(series.nunique()),

            "sample_values": sample_values
        })

    dataset_information = {
        "total_rows": int(len(dataframe)),

        "total_columns": int(len(dataframe.columns)),

        "columns": columns
    }

    return dataset_information


# ============================================================
# JSON PARSING AND NORMALIZATION
# ============================================================

def parse_ai_json(ai_response):
    """Parse and normalize JSON returned by the AI."""

    if not isinstance(ai_response, str) or not ai_response.strip():

        raise ValueError(
            "The AI returned an empty response."
        )

    cleaned = ai_response.strip()

    # Remove Markdown JSON code fences if present.

    cleaned = re.sub(
        r"^\s*```(?:json)?\s*",
        "",
        cleaned,
        flags=re.IGNORECASE
    )

    cleaned = re.sub(
        r"\s*```\s*$",
        "",
        cleaned
    )

    try:

        parsed = json.loads(cleaned)

    except json.JSONDecodeError as error:

        raise ValueError(
            "The AI returned invalid JSON. Please try again."
        ) from error

    if not isinstance(parsed, dict):

        raise ValueError(
            "The AI response must be a JSON object."
        )

    steps = parsed.get("steps")

    if not isinstance(steps, list):

        raise ValueError(
            "The AI workflow must contain a list of steps."
        )

    # Normalize optional fields.
    # Null group_by is acceptable for non-grouping operations.
    # An empty list in group_aggregate will still be rejected
    # by the Pydantic schema.

    for index, step in enumerate(steps, start=1):

        if not isinstance(step, dict):

            raise ValueError(
                f"Step {index} must be a JSON object."
            )

        if step.get("group_by") is None:
            step["group_by"] = []
        elif isinstance(step.get("group_by"), str):
            step["group_by"] = [step["group_by"]]

    return parsed


# ============================================================
# WORKFLOW VALIDATION
# ============================================================

def validate_generated_workflow(workflow_json, dataframe):
    """Validate workflow structure and dataset references."""

    workflow = WorkflowDefinition.model_validate(
        workflow_json
    )

    validate_workflow_columns(
        workflow,
        dataframe
    )

    return workflow


# ============================================================
# MAIN WORKFLOW GENERATOR
# ============================================================

def generate_workflow(user_request, dataframe):
    """
    Generate a structured workflow using the configured AI service.

    Validates the generated JSON using Pydantic and checks
    dataset columns before returning the workflow.
    """

    # --------------------------------------------------------
    # 1. Validate user input
    # --------------------------------------------------------

    if (
        not isinstance(user_request, str)
        or not user_request.strip()
    ):

        raise ValueError(
            "Please enter a workflow description."
        )

    if dataframe is None or dataframe.empty:

        raise ValueError(
            "Please upload a valid dataset first."
        )

    if not dataframe.columns.is_unique:

        raise ValueError(
            "The dataset contains duplicate column names."
        )

    # --------------------------------------------------------
    # 2. Collect dataset information
    # --------------------------------------------------------

    dataset_information = get_dataset_information(
        dataframe
    )

    # --------------------------------------------------------
    # 3. Prepare user prompt
    # --------------------------------------------------------

    base_prompt = f"""
USER REQUEST:

{user_request}

DATASET INFORMATION:

{json.dumps(dataset_information, indent=2)}

IMPORTANT INSTRUCTIONS:

1. Use only the available dataset columns.
2. Respect the data type of every column.
3. Every group_aggregate operation MUST have:
   - group_by
   - aggregate_column
   - aggregation

4. For non-grouping operations, use group_by: [].

5. For counting students, use student_id.

6. Use mean, sum, min and max only on numeric columns.

7. Do not invent unsupported calculations.

8. Return valid JSON only.
"""

    correction = ""

    last_error = None

    # --------------------------------------------------------
    # 4. Generate and validate workflow
    # --------------------------------------------------------

    for attempt in range(1, MAX_GENERATION_ATTEMPTS + 1):

        user_prompt = base_prompt

        if correction:

            user_prompt += f"""

YOUR PREVIOUS RESPONSE WAS INVALID.

FIX THE FOLLOWING ERROR:

{correction}

Return the complete corrected workflow JSON.
Do not return a partial response.
"""

        try:

            # Call configured AI service.

            ai_response = generate_ai_response(
                SYSTEM_PROMPT,
                user_prompt
            )

            # Parse and normalize JSON.

            workflow_json = parse_ai_json(
                ai_response
            )

            # Validate Pydantic schema and dataset columns.

            workflow = validate_generated_workflow(
                workflow_json,
                dataframe
            )

            # Successful workflow generation.

            return workflow

        except (ValueError, ValidationError) as error:

            last_error = error

            correction = str(error)

            # Retry once with validation feedback.

            if attempt < MAX_GENERATION_ATTEMPTS:
                continue

        except Exception as error:

            raise RuntimeError(
                "The AI service could not generate a workflow. "
                "Check your API configuration and service logs."
            ) from error

    # --------------------------------------------------------
    # 5. Raise error after failed attempts
    # --------------------------------------------------------

    raise ValueError(
        "Workflow generation failed after "
        f"{MAX_GENERATION_ATTEMPTS} attempts. "
        f"Validation details: {last_error}"
    ) from last_error
