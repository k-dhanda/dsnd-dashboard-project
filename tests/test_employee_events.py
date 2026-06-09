import pytest
from pathlib import Path

# Absolute path of the project root directory.
# test_employee_events.py lives at <project_root>/tests/test_employee_events.py
project_root = Path(__file__).resolve().parent.parent


@pytest.fixture
def db_path():
    """
    Pytest fixture that returns the Path to employee_events.db.

    Returns
    -------
    pathlib.Path
        Absolute path to the SQLite database file.
    """
    return project_root / 'python-package' / 'employee_events' / 'employee_events.db'


def test_db_exists(db_path):
    """Assert the SQLite database file exists at the expected location."""
    assert db_path.is_file(), f"Database not found at {db_path}"


@pytest.fixture
def db_conn(db_path):
    from sqlite3 import connect
    return connect(db_path)


@pytest.fixture
def table_names(db_conn):
    name_tuples = db_conn.execute("SELECT name FROM sqlite_master WHERE type='table';").fetchall()
    return [x[0] for x in name_tuples]


def test_employee_table_exists(table_names):
    """Assert the 'employee' table exists in the database."""
    assert 'employee' in table_names


def test_team_table_exists(table_names):
    """Assert the 'team' table exists in the database."""
    assert 'team' in table_names


def test_employee_events_table_exists(table_names):
    """Assert the 'employee_events' table exists in the database."""
    assert 'employee_events' in table_names
