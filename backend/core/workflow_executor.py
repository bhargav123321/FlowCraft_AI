
from backend.core import operations

from backend.core.workflow_validator import (
    validate_workflow_columns
)


def execute_workflow(workflow, dataframe):
    """
    Execute an approved workflow using predefined operations.

    Row-level operations modify the working dataset.

    Aggregation operations calculate separate result tables
    without replacing the working dataset.

    All aggregation operations use the current processed
    dataset at the point where they appear in the workflow.
    """

    # ========================================================
    # 1. VALIDATE WORKFLOW
    # ========================================================

    if dataframe is None or dataframe.empty:
        raise ValueError(
            "Please upload a valid dataset before execution."
        )

    validate_workflow_columns(
        workflow,
        dataframe
    )

    # Keep original dataset unchanged.
    result_df = dataframe.copy()

    execution_logs = []
    generated_reports = []
    aggregation_results = []

    # ========================================================
    # 2. EXECUTE WORKFLOW STEPS
    # ========================================================

    for index, step in enumerate(workflow.steps, start=1):

        operation_name = step.operation

        try:

            # ------------------------------------------------
            # REMOVE DUPLICATES
            # ------------------------------------------------

            if operation_name == "remove_duplicates":

                result_df, log = operations.remove_duplicates(
                    result_df
                )

            # ------------------------------------------------
            # DROP MISSING VALUES
            # ------------------------------------------------

            elif operation_name == "drop_missing":

                result_df, log = operations.drop_missing(
                    result_df
                )

            # ------------------------------------------------
            # FILTER ROWS
            # ------------------------------------------------

            elif operation_name == "filter_rows":

                result_df, log = operations.filter_rows(
                    result_df,
                    step.column,
                    step.condition,
                    step.value
                )

            # ------------------------------------------------
            # VALIDATE NUMERIC RANGE
            # ------------------------------------------------

            elif operation_name == "validate_range":

                result_df, log = operations.validate_range(
                    result_df,
                    step.column,
                    step.min_value,
                    step.max_value
                )

            # ------------------------------------------------
            # GROUP AND AGGREGATE
            # ------------------------------------------------

            elif operation_name == "group_aggregate":

                # Calculate aggregation separately.
                # Do not overwrite result_df.

                aggregated_df, log = operations.group_aggregate(
                    result_df,
                    step.group_by,
                    step.aggregate_column,
                    step.aggregation
                )

                # Store each aggregation result independently.

                aggregation_results.append({
                    "step_number": index,

                    "description": step.description,

                    "operation": operation_name,

                    "group_by": list(step.group_by),

                    "aggregate_column": step.aggregate_column,

                    "aggregation": step.aggregation,

                    "result_df": aggregated_df.copy(),

                    "total_groups": len(aggregated_df),

                    "log": log.copy()
                })

            # ------------------------------------------------
            # SORT ROWS
            # ------------------------------------------------

            elif operation_name == "sort_rows":

                result_df, log = operations.sort_rows(
                    result_df,
                    step.column,
                    step.sort_order
                )

            # ------------------------------------------------
            # GENERATE REPORT
            # ------------------------------------------------

            elif operation_name == "generate_report":

                result_df, log = operations.generate_report(
                    result_df
                )

                generated_reports.append(
                    log["report"]
                )

            # ------------------------------------------------
            # UNSUPPORTED OPERATION
            # ------------------------------------------------

            else:

                raise ValueError(
                    f"Unsupported operation: {operation_name}"
                )

            # =================================================
            # 3. RECORD EXECUTION LOG
            # =================================================

            log["step_number"] = index

            log["step_description"] = step.description

            log["status"] = "success"

            execution_logs.append(log)

        except Exception as error:

            # Identify exactly which workflow step failed.

            execution_logs.append({
                "step_number": index,
                "step_description": step.description,
                "operation": operation_name,
                "status": "failed",
                "rows_affected": 0,
                "message": str(error)
            })

            raise RuntimeError(
                f"Workflow execution failed at Step {index} "
                f"({operation_name}): {error}"
            ) from error

    # ========================================================
    # 4. RETURN COMPLETE EXECUTION RESULTS
    # ========================================================

    return {
        "result_df": result_df,

        "execution_logs": execution_logs,

        "generated_reports": generated_reports,

        "aggregation_results": aggregation_results,

        "total_steps": len(workflow.steps),

        "successful_steps": sum(
            1 for log in execution_logs
            if log["status"] == "success"
        ),

        "failed_steps": sum(
            1 for log in execution_logs
            if log["status"] == "failed"
        ),

        "total_aggregation_results": len(
            aggregation_results
        )
    }
