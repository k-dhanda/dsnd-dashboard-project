from .query_base import QueryBase
from .sql_execution import query


class Team(QueryBase):
    """
    SQL query class for team entities.

    Inherits shared queries from QueryBase and adds team-specific
    queries for listing teams and retrieving a single team's name.

    Attributes
    ----------
    name : str
        Entity name used in f-string SQL queries.  Always 'team'.
    """

    name = 'team'

    @query
    def names(self):
        """
        Return all teams as (team_name, team_id) tuples.

        QUERY 5 — Selects team_name and team_id for all rows in the
        team table.

        Returns
        -------
        list of tuple
            Each tuple is (team_name: str, team_id: int).
        """
        return """
            SELECT team_name, team_id
            FROM team
            ORDER BY team_name
        """

    @query
    def username(self, id):
        """
        Return the name of a single team.

        QUERY 6 — Selects team_name for the team whose team_id matches *id*.

        Parameters
        ----------
        id : int or str
            The team's primary key.

        Returns
        -------
        list of tuple
            Single-element list containing a one-element tuple with the
            team name.
        """
        return f"""
            SELECT team_name
            FROM team
            WHERE team_id = {id}
        """

    def model_data(self, id):
        """
        Return per-employee aggregated event counts for the ML model.

        Sums total positive and negative events per employee within the
        team and returns a pandas DataFrame with one row per employee.

        Parameters
        ----------
        id : int or str
            The team's primary key.

        Returns
        -------
        pandas.DataFrame
            Columns: positive_events, negative_events
            (one row per team member).
        """
        return self.pandas_query(f"""
            SELECT positive_events, negative_events FROM (
                    SELECT employee_id
                         , SUM(positive_events) positive_events
                         , SUM(negative_events) negative_events
                    FROM {self.name}
                    JOIN employee_events
                        USING({self.name}_id)
                    WHERE {self.name}.{self.name}_id = {id}
                    GROUP BY employee_id
                   )
                """)
