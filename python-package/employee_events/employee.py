from .query_base import QueryBase
from .sql_execution import query


class Employee(QueryBase):
    """
    SQL query class for individual employee entities.

    Inherits shared queries from QueryBase and adds employee-specific
    queries for listing employees and retrieving a single employee's name.

    Attributes
    ----------
    name : str
        Entity name used in f-string SQL queries.  Always 'employee'.
    """

    name = 'employee'

    @query
    def names(self):
        """
        Return all employees as (full_name, employee_id) tuples.

        QUERY 3 — Selects the employee full name (first + last) and id
        for every row in the employee table.

        Returns
        -------
        list of tuple
            Each tuple is (full_name: str, employee_id: int).
        """
        return """
            SELECT first_name || ' ' || last_name AS full_name
                 , employee_id
            FROM employee
            ORDER BY last_name, first_name
        """

    @query
    def username(self, id):
        """
        Return the full name of a single employee.

        QUERY 4 — Selects first_name || last_name for the employee
        whose employee_id matches *id*.

        Parameters
        ----------
        id : int or str
            The employee's primary key.

        Returns
        -------
        list of tuple
            Single-element list containing a one-element tuple with the
            employee's full name.
        """
        return f"""
            SELECT first_name || ' ' || last_name AS full_name
            FROM employee
            WHERE employee_id = {id}
        """

    def model_data(self, id):
        """
        Return aggregated event counts needed by the ML model.

        Sums total positive and negative events for the employee across
        all dates and returns a single-row pandas DataFrame.

        Parameters
        ----------
        id : int or str
            The employee's primary key.

        Returns
        -------
        pandas.DataFrame
            Columns: positive_events, negative_events (one row).
        """
        return self.pandas_query(f"""
                    SELECT SUM(positive_events) positive_events
                         , SUM(negative_events) negative_events
                    FROM {self.name}
                    JOIN employee_events
                        USING({self.name}_id)
                    WHERE {self.name}.{self.name}_id = {id}
                """)
