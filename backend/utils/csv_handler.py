
import io
import pandas as pd


MAX_FILE_SIZE = 20 * 1024 * 1024  # 20 MB


def load_csv_file(file_bytes, filename):
    """
    Safely load a CSV file into a Pandas DataFrame.
    """

    if not filename.lower().endswith(".csv"):
        raise ValueError("Only CSV files are supported.")

    if not file_bytes:
        raise ValueError("The uploaded file is empty.")

    if len(file_bytes) > MAX_FILE_SIZE:
        raise ValueError("File exceeds the 20 MB limit.")

    encodings = ["utf-8-sig", "utf-8", "cp1252"]

    last_error = None

    for encoding in encodings:

        try:

            df = pd.read_csv(
                io.BytesIO(file_bytes),
                encoding=encoding,
                low_memory=False,
                on_bad_lines="error"
            )

            if df.empty:
                raise ValueError(
                    "The CSV contains no data records."
                )

            if len(df.columns) == 0:
                raise ValueError(
                    "The CSV does not contain any columns."
                )

            if len(df.columns) > 200:
                raise ValueError(
                    "The CSV contains too many columns."
                )

            # Normalize column names
            df.columns = [
                str(column).strip()
                for column in df.columns
            ]

            if any(not column for column in df.columns):
                raise ValueError(
                    "The CSV contains an empty column name."
                )

            if len(set(df.columns)) != len(df.columns):
                raise ValueError(
                    "Duplicate column names detected. "
                    "Please rename duplicate columns."
                )

            return df

        except UnicodeDecodeError as error:
            last_error = error
            continue

        except (pd.errors.ParserError, pd.errors.EmptyDataError) as error:
            raise ValueError(
                f"Unable to parse CSV: {error}"
            ) from error

    raise ValueError(
        f"Unable to decode CSV file: {last_error}"
    )


def get_dataset_overview(df):
    """
    Generate basic information about a dataset.
    """

    return {
        "total_rows": len(df),
        "total_columns": len(df.columns),
        "missing_values": int(
            df.isnull().sum().sum()
        ),
        "duplicate_rows": int(
            df.duplicated().sum()
        ),
        "memory_usage": int(
            df.memory_usage(deep=True).sum()
        ),
        "column_names": df.columns.tolist()
    }


def get_column_information(df):
    """
    Generate information about every column.
    """

    information = []

    for column in df.columns:

        information.append({
            "column": column,
            "data_type": str(df[column].dtype),
            "missing_values": int(
                df[column].isnull().sum()
            ),
            "unique_values": int(
                df[column].nunique()
            ),
            "missing_percentage": round(
                df[column].isnull().mean() * 100,
                2
            )
        })

    return pd.DataFrame(information)
