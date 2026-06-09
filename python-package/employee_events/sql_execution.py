from sqlite3 import connect
from pathlib import Path
from functools import wraps
import pandas as pd

# Absolute path to the employee_events.db file
# (packaged alongside this module)
db_path = Path(__file__).resolve().parent / 'employee_events.db'


# OPTION 1: MIXIN
class QueryMixin:
    """
    Mixin that provides SQL execution helpers.

    Methods
    -------
    pandas_query(sql_query)
        Execute a SQL query and return results as a pandas DataFrame.
    query(sql_query)
        Execute a SQL query and return results as a list of tuples.
    """

    def pandas_query(self, sql_query):
        """
        Execute *sql_query* against employee_events.db.

        Opens a connection, runs the query via pandas.read_sql,
        closes the connection, and returns the resulting DataFrame.
        """
        connection = connect(db_path)
        df = pd.read_sql(sql_query, connection)
        connection.close()
        return df

    def query(self, sql_query):
        """
        Execute *sql_query* against employee_events.db.

        Opens a connection, runs the query via a cursor, closes the
        connection, and returns results as a list of tuples.
        """
        connection = connect(db_path)
        cursor = connection.cursor()
        result = cursor.execute(sql_query).fetchall()
        connection.close()
        return result


# Leave this code unchanged
def query(func):
    """
    Decorator that runs a standard sql execution
    and returns a list of tuples
    """

    @wraps(func)
    def run_query(*args, **kwargs):
        query_string = func(*args, **kwargs)
        connection = connect(db_path)
        cursor = connection.cursor()
        result = cursor.execute(query_string).fetchall()
        connection.close()
        return result

    return run_query
