
import pandas as pd
import re


EMAIL_PATTERN = re.compile(
    r"^[A-Za-z0-9.!#$%&'*+/=?^_`{|}~-]+"
    r"@[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)+$"
)


def validate_email(value):
    """
    Check whether an email address has a valid basic format.
    """

    if pd.isna(value):
        return False

    value = str(value).strip()

    if not value or len(value) > 254:
        return False

    return bool(EMAIL_PATTERN.fullmatch(value))


def validate_numeric_range(series, minimum, maximum):
    """
    Identify numeric values outside an allowed range.
    """

    numeric_values = pd.to_numeric(
        series,
        errors="coerce"
    )

    invalid = (
        numeric_values.notna()
        & (
            (numeric_values < minimum)
            | (numeric_values > maximum)
        )
    )

    return int(invalid.sum())


def analyze_data_quality(df):
    """
    Analyze missing, duplicate and invalid values.

    This function does not modify the original dataset.
    """

    issues = []

    # Missing values

    for column in df.columns:

        missing_count = int(
            df[column].isnull().sum()
        )

        if missing_count > 0:

            issues.append({
                "column": column,
                "issue": "Missing values",
                "count": missing_count,
                "severity": "Warning"
            })

    # Duplicate records

    duplicate_count = int(
        df.duplicated().sum()
    )

    if duplicate_count > 0:

        issues.append({
            "column": "All columns",
            "issue": "Duplicate rows",
            "count": duplicate_count,
            "severity": "Warning"
        })

    # Student-specific validations

    if "attendance" in df.columns:

        invalid_count = validate_numeric_range(
            df["attendance"], 0, 100
        )

        if invalid_count:

            issues.append({
                "column": "attendance",
                "issue": "Attendance outside 0-100",
                "count": invalid_count,
                "severity": "Error"
            })

    if "marks" in df.columns:

        invalid_count = validate_numeric_range(
            df["marks"], 0, 100
        )

        if invalid_count:

            issues.append({
                "column": "marks",
                "issue": "Marks outside 0-100",
                "count": invalid_count,
                "severity": "Error"
            })

    if "email" in df.columns:

        invalid_emails = (
            df["email"].notna()
            & ~df["email"].apply(validate_email)
        )

        invalid_count = int(
            invalid_emails.sum()
        )

        if invalid_count:

            issues.append({
                "column": "email",
                "issue": "Invalid email format",
                "count": invalid_count,
                "severity": "Error"
            })

    if "semester" in df.columns:

        semester = pd.to_numeric(
            df["semester"],
            errors="coerce"
        )

        invalid_semesters = (
            semester.notna()
            & ~semester.between(1, 8)
        )

        invalid_count = int(
            invalid_semesters.sum()
        )

        if invalid_count:

            issues.append({
                "column": "semester",
                "issue": "Semester outside 1-8",
                "count": invalid_count,
                "severity": "Error"
            })

    return pd.DataFrame(
        issues,
        columns=[
            "column",
            "issue",
            "count",
            "severity"
        ]
    )
