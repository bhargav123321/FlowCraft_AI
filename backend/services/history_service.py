import json
import sqlite3

from contextlib import contextmanager
from datetime import datetime
from pathlib import Path


# ============================================================
# DATABASE CONFIGURATION
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATABASE_DIRECTORY = PROJECT_ROOT / "data"

DATABASE_PATH = DATABASE_DIRECTORY / "flowcraft.db"


# ============================================================
# DATABASE CONNECTION
# ============================================================

@contextmanager
def get_connection():
    """
    Create and safely close a SQLite database connection.
    """

    DATABASE_DIRECTORY.mkdir(
        parents=True,
        exist_ok=True
    )

    connection = sqlite3.connect(
        DATABASE_PATH,
        timeout=30
    )

    connection.row_factory = sqlite3.Row

    try:
        yield connection
        connection.commit()

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


# ============================================================
# INITIALIZE DATABASE
# ============================================================

def initialize_database():
    """
    Create the workflow history table if it does not exist.
    """

    with get_connection() as connection:

        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS workflow_history (

                id INTEGER PRIMARY KEY AUTOINCREMENT,

                workflow_name TEXT NOT NULL,

                description TEXT,

                user_request TEXT,

                dataset_name TEXT,

                total_steps INTEGER DEFAULT 0,

                execution_status TEXT NOT NULL,

                execution_time TEXT NOT NULL,

                workflow_json TEXT,

                execution_logs TEXT

            )
            """
        )


# ============================================================
# SAVE WORKFLOW HISTORY
# ============================================================

def save_workflow_history(
    workflow_name,
    description,
    user_request,
    dataset_name,
    workflow_steps,
    execution_status,
    execution_logs=None
):
    """
    Save an executed workflow permanently in SQLite.
    """

    initialize_database()

    execution_time = datetime.now().astimezone().isoformat(
        timespec="seconds"
    )

    if hasattr(workflow_steps, "model_dump"):
        workflow_dict = workflow_steps.model_dump()
    elif isinstance(workflow_steps, dict):
        workflow_dict = workflow_steps
    else:
        workflow_dict = {}

    workflow_json = json.dumps(
        workflow_dict,
        indent=2,
        default=str
    )

    logs_json = json.dumps(
        execution_logs or [],
        indent=2,
        default=str
    )

    total_steps = len(workflow_dict.get("steps") or [])

    with get_connection() as connection:

        cursor = connection.execute(
            """
            INSERT INTO workflow_history (

                workflow_name,
                description,
                user_request,
                dataset_name,
                total_steps,
                execution_status,
                execution_time,
                workflow_json,
                execution_logs

            )

            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                workflow_name,
                description,
                user_request,
                dataset_name,
                total_steps,
                execution_status,
                execution_time,
                workflow_json,
                logs_json
            )
        )

        return cursor.lastrowid


# ============================================================
# FETCH ALL WORKFLOW HISTORY
# ============================================================

def get_workflow_history():
    """
    Retrieve all workflow history records.
    """

    initialize_database()

    with get_connection() as connection:

        records = connection.execute(
            """
            SELECT *
            FROM workflow_history
            ORDER BY id DESC
            """
        ).fetchall()

    history = []

    for record in records:

        item = dict(record)

        try:

            item["workflow_steps"] = json.loads(
                item["workflow_json"] or "{}"
            )

            item["execution_logs"] = json.loads(
                item["execution_logs"] or "[]"
            )

        except json.JSONDecodeError:

            item["workflow_steps"] = {}
            item["execution_logs"] = []

        history.append(item)

    return history


# ============================================================
# FETCH WORKFLOW BY ID
# ============================================================

def get_workflow_by_id(workflow_id):
    """
    Retrieve one workflow using its database ID.
    """

    initialize_database()

    with get_connection() as connection:

        record = connection.execute(
            """
            SELECT *
            FROM workflow_history
            WHERE id = ?
            """,
            (workflow_id,)
        ).fetchone()

    if record is None:
        return None

    item = dict(record)

    try:

        item["workflow_steps"] = json.loads(
            item["workflow_json"] or "{}"
        )

        item["execution_logs"] = json.loads(
            item["execution_logs"] or "[]"
        )

    except json.JSONDecodeError:

        item["workflow_steps"] = {}
        item["execution_logs"] = []

    return item


# ============================================================
# DELETE ONE WORKFLOW
# ============================================================

def delete_workflow_history(workflow_id):
    """
    Delete a specific workflow history record.
    """

    initialize_database()

    with get_connection() as connection:

        cursor = connection.execute(
            """
            DELETE FROM workflow_history
            WHERE id = ?
            """,
            (workflow_id,)
        )

        return cursor.rowcount > 0


# ============================================================
# CLEAR ALL WORKFLOW HISTORY
# ============================================================

def clear_workflow_history():
    """
    Delete all stored workflow history records.
    """

    initialize_database()

    with get_connection() as connection:

        connection.execute(
            "DELETE FROM workflow_history"
        )
