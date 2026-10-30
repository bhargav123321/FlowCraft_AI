
from typing import Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    model_validator,
)


Operation = Literal[
    "remove_duplicates",
    "drop_missing",
    "filter_rows",
    "validate_range",
    "group_aggregate",
    "sort_rows",
    "generate_report",
]

FilterCondition = Literal[
    "greater_than",
    "greater_than_or_equal",
    "less_than",
    "less_than_or_equal",
    "equal",
    "not_equal",
]

AggregationMethod = Literal[
    "mean",
    "sum",
    "min",
    "max",
    "count",
]

SortOrder = Literal["ascending", "descending"]


class WorkflowStep(BaseModel):
    """Schema for one safe, approved workflow operation."""

    model_config = ConfigDict(extra="forbid")

    operation: Operation

    description: str = Field(
        min_length=3,
        max_length=300,
    )

    column: str | None = None

    condition: FilterCondition | None = None

    value: str | float | int | None = None

    min_value: float | None = None
    max_value: float | None = None

    group_by: list[str] = Field(default_factory=list)

    aggregate_column: str | None = None

    aggregation: AggregationMethod | None = None

    sort_order: SortOrder | None = None

    @model_validator(mode="after")
    def validate_required_fields(self):
        """Check that each operation has its required parameters."""

        if self.operation == "filter_rows":
            if self.column is None or self.condition is None:
                raise ValueError(
                    "filter_rows requires column and condition."
                )

            if self.value is None:
                raise ValueError(
                    "filter_rows requires a comparison value."
                )

        elif self.operation == "validate_range":
            if self.column is None:
                raise ValueError(
                    "validate_range requires column."
                )

            if self.min_value is None or self.max_value is None:
                raise ValueError(
                    "validate_range requires min_value and max_value."
                )

            if self.min_value > self.max_value:
                raise ValueError(
                    "min_value cannot be greater than max_value."
                )

        elif self.operation == "group_aggregate":
            if not self.group_by:
                raise ValueError(
                    "group_aggregate requires a non-empty group_by list."
                )

            if any(not column.strip() for column in self.group_by):
                raise ValueError(
                    "group_by cannot contain empty column names."
                )

            if self.aggregate_column is None:
                raise ValueError(
                    "group_aggregate requires aggregate_column."
                )

            if not self.aggregate_column.strip():
                raise ValueError(
                    "aggregate_column cannot be empty."
                )

            if self.aggregation is None:
                raise ValueError(
                    "group_aggregate requires aggregation."
                )

        elif self.operation == "sort_rows":
            if self.column is None or self.sort_order is None:
                raise ValueError(
                    "sort_rows requires column and sort_order."
                )

        return self


class WorkflowDefinition(BaseModel):
    """Schema for a complete generated workflow."""

    model_config = ConfigDict(extra="forbid")

    workflow_name: str = Field(
        min_length=3,
        max_length=100,
    )

    description: str = Field(
        min_length=3,
        max_length=500,
    )

    steps: list[WorkflowStep] = Field(
        min_length=1,
        max_length=20,
    )
