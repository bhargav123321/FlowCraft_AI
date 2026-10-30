
import pandas as pd

from backend.core.operations import group_aggregate


df = pd.DataFrame({
    "department": ["CSE", "IT", "CSE", "ECE", "IT"],
    "placement_status": [
        "Placed",
        "Not Placed",
        "Placed",
        "Not Eligible",
        "Not Placed"
    ],
    "marks": [85, 70, 90, 60, 75]
})

# Test 1: Count students by placement status
result, log = group_aggregate(
    df,
    group_by=["placement_status"],
    aggregate_column="placement_status",
    aggregation="count"
)

print("Categorical aggregation:")
print(result)
print(log)

# Test 2: Average marks by department
result, log = group_aggregate(
    df,
    group_by=["department"],
    aggregate_column="marks",
    aggregation="mean"
)

print("\nNumeric aggregation:")
print(result)
print(log)

# Test 3: Invalid aggregation should raise an error
try:
    group_aggregate(
        df,
        group_by=["department"],
        aggregate_column="placement_status",
        aggregation="mean"
    )
except ValueError as error:
    print("\nExpected validation error:")
    print(error)
