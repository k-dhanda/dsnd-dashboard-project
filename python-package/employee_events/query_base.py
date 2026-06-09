from .sql_execution import QueryMixin


class QueryBase(QueryMixin):
    """
    Base class for employee_events SQL queries.

    Provides shared queries for both Employee and Team entities.
    Subclasses set the ``name`` class attribute to 'employee' or 'team'
    so that f-string formatted queries target the correct table and
    id column.

    Inherits
    --------
    QueryMixin
        Provides ``pandas_query`` and ``query`` methods for SQL execution.
    """

    # Subclasses override this with their entity name ('employee' or 'team')
    name = ''

    def names(self):
        """Return an empty list (overridden in subclasses)."""
        return []

    def event_counts(self, id):
        """
        Return cumulative positive and negative event counts per date.

        Groups employee_events by event_date for the given entity id
        and sums the positive and negative event columns.

        Parameters
        ----------
        id : int or str
            Entity id (employee_id or team_id).

        Returns
        -------
        pandas.DataFrame
            Columns: event_date, positive_events, negative_events
        """
        # QUERY 1
        # Group by event_date, sum positive and negative events
        # for the entity whose id matches the argument.
        sql = f"""
            SELECT event_date
                 , SUM(positive_events) AS positive_events
                 , SUM(negative_events) AS negative_events
            FROM {self.name}
            JOIN employee_events
                USING({self.name}_id)
            WHERE {self.name}.{self.name}_id = {id}
            GROUP BY event_date
            ORDER BY event_date
        """
        return self.pandas_query(sql)

    def notes(self, id):
        """
        Return manager notes for the given entity.

        Parameters
        ----------
        id : int or str
            Entity id (employee_id or team_id).

        Returns
        -------
        pandas.DataFrame
            Columns: note_date, note
        """
        # QUERY 2
        # Join the notes table to the entity table on the shared id column
        # and filter to the requested entity.
        sql = f"""
            SELECT note_date, note
            FROM notes
            JOIN {self.name}
                USING({self.name}_id)
            WHERE {self.name}.{self.name}_id = {id}
        """
        return self.pandas_query(sql)
