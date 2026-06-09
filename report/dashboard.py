from fasthtml.common import *
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import numpy as np

# Import QueryBase, Employee, Team from the installed employee_events package
from employee_events import QueryBase, Employee, Team

# Import load_model from utils.py in this same directory
from utils import load_model

# Pre-built parent classes from report/base_components and report/combined_components
from base_components import (
    Dropdown,
    BaseComponent,
    Radio,
    MatplotlibViz,
    DataTable,
)

from combined_components import FormGroup, CombinedComponent


# ---------------------------------------------------------------------------
# ReportDropdown
# ---------------------------------------------------------------------------

class ReportDropdown(Dropdown):
    """
    Dropdown that lists all employees or teams from the database.

    Overrides ``build_component`` to set the label dynamically from the
    model's ``name`` attribute, and overrides ``component_data`` to
    fetch (display_text, id) pairs via the model's ``names`` method.
    """

    def build_component(self, entity_id, model):
        """Set the label to the current model name then delegate to parent."""
        self.label = model.name.title()
        return super().build_component(entity_id, model)

    def component_data(self, entity_id, model):
        """Return list of (name, id) tuples from the model."""
        return model.names()


# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------

class Header(BaseComponent):
    """
    Page heading that reflects whether we are viewing an employee or a team.

    Implements the 'stand-out' requirement: title reads
    "Employee Performance" or "Team Performance" rather than just the
    raw model name.
    """

    def build_component(self, entity_id, model):
        """Return an H1 element containing '<Entity> Performance'."""
        return H1(f"{model.name.title()} Performance")


# ---------------------------------------------------------------------------
# LineChart  –  cumulative event counts over time
# ---------------------------------------------------------------------------

class LineChart(MatplotlibViz):
    """
    Line chart showing cumulative positive and negative events over time.

    Fetches event_counts data from the model, fills missing dates with 0,
    computes a running cumulative sum, then plots two lines (Positive /
    Negative) with accessible styling.
    """

    def visualization(self, entity_id, model):
        """
        Build the cumulative events line chart.

        Parameters
        ----------
        entity_id : str or int
            The selected employee or team id.
        model : Employee | Team
            Active SQL model instance.
        """
        # Fetch grouped event counts from the database
        data = model.event_counts(entity_id)

        # Fill any missing values with 0
        data = data.fillna(0)

        # Use event_date as the DataFrame index and sort chronologically
        data = data.set_index('event_date')
        data = data.sort_index()

        # Convert to cumulative counts so the chart shows running totals
        data = data.cumsum()

        # Human-readable column labels
        data.columns = ['Positive', 'Negative']

        # Create matplotlib figure and axis
        fig, ax = plt.subplots(figsize=(8, 4))

        # Plot the two cumulative series
        data.plot(ax=ax, color=['#2ecc71', '#e74c3c'])

        # Apply consistent styling (black borders and labels for legibility)
        self.set_axis_styling(ax, bordercolor='black', fontcolor='black')

        # Titles and axis labels
        ax.set_title('Cumulative Performance Events', fontsize=14)
        ax.set_xlabel('Date', fontsize=11)
        ax.set_ylabel('Cumulative Count', fontsize=11)
        ax.legend(fontsize=10)


# ---------------------------------------------------------------------------
# BarChart  –  ML recruitment-risk prediction
# ---------------------------------------------------------------------------

class BarChart(MatplotlibViz):
    """
    Horizontal bar chart showing the model's predicted recruitment risk.

    For an individual employee the bar shows that employee's probability.
    For a team the bar shows the mean probability across all team members.

    Includes a colour scale (green → amber → red) as the 'stand-out'
    feature: the bar colour reflects risk severity.
    """

    # Load the pickled scikit-learn model once at class definition time
    predictor = load_model()

    def visualization(self, entity_id, model):
        """
        Build the recruitment-risk bar chart.

        Parameters
        ----------
        entity_id : str or int
            The selected employee or team id.
        model : Employee | Team
            Active SQL model instance.
        """
        # Retrieve the feature data required by the ML model
        data = model.model_data(entity_id)

        # Predict class probabilities; shape = (n_samples, n_classes)
        proba = self.predictor.predict_proba(data)

        # Keep only the second column (P(recruited=1)); shape = (n_samples, 1)
        proba = proba[:, 1:]

        # Aggregate to a single scalar for display
        if model.name == 'team':
            # Team view: show the average risk across all team members
            pred = float(proba.mean())
        else:
            # Employee view: show the individual's risk probability
            pred = float(proba[0][0])

        # --- Colour scale: green (low risk) → red (high risk) ---
        # Use the RdYlGn_r colourmap so red = high risk, green = low risk
        colour = cm.RdYlGn_r(pred)   # returns (R, G, B, A)

        # Create figure and axis
        fig, ax = plt.subplots(figsize=(6, 2))

        # Unchanged code from the spec
        ax.barh([''], [pred], color=[colour])
        ax.set_xlim(0, 1)
        ax.set_title('Predicted Recruitment Risk', fontsize=20)

        # Style the axis to match the rest of the dashboard
        self.set_axis_styling(ax, bordercolor='black', fontcolor='black')

        # Add a text annotation showing the exact probability
        ax.text(
            pred + 0.02, 0,
            f'{pred:.0%}',
            va='center',
            fontsize=14,
            color='black',
        )


# ---------------------------------------------------------------------------
# Visualizations  –  grid of LineChart + BarChart
# ---------------------------------------------------------------------------

class Visualizations(CombinedComponent):
    """
    Renders LineChart and BarChart side-by-side inside a CSS grid div.
    """

    children = [LineChart(), BarChart()]

    # Override the outer div to use the 'grid' CSS class
    outer_div_type = Div(cls='grid')


# ---------------------------------------------------------------------------
# NotesTable  –  manager notes for the selected entity
# ---------------------------------------------------------------------------

class NotesTable(DataTable):
    """
    DataTable subclass that displays manager notes from the database.
    """

    def component_data(self, entity_id, model):
        """
        Fetch notes for the current entity.

        Parameters
        ----------
        entity_id : str or int
        model : Employee | Team

        Returns
        -------
        pandas.DataFrame
            Columns: note_date, note
        """
        return model.notes(entity_id)


# ---------------------------------------------------------------------------
# DashboardFilters  –  radio buttons + dropdown form (provided, unchanged)
# ---------------------------------------------------------------------------

class DashboardFilters(FormGroup):

    id = "top-filters"
    action = "/update_data"
    method = "POST"

    children = [
        Radio(
            values=["Employee", "Team"],
            name='profile_type',
            hx_get='/update_dropdown',
            hx_target='#selector',
        ),
        ReportDropdown(
            id="selector",
            name="user-selection",
        ),
    ]


# ---------------------------------------------------------------------------
# Report  –  full-page combined component
# ---------------------------------------------------------------------------

class Report(CombinedComponent):
    """
    Top-level page component.

    Composes Header, DashboardFilters, Visualizations, and NotesTable
    into a single HTML page returned by each route.
    """

    children = [
        Header(),
        DashboardFilters(),
        Visualizations(),
        NotesTable(),
    ]


# ---------------------------------------------------------------------------
# FastHTML application + routes
# ---------------------------------------------------------------------------

# Initialise the FastHTML app, loading the project CSS
app = FastHTML(
    hdrs=[
        Link(rel='stylesheet', href='/assets/report.css', type='text/css'),
    ]
)

# Serve the assets directory so report.css is accessible
@app.get('/assets/{fname:path}')
def serve_asset(fname: str):
    from pathlib import Path
    asset_path = Path(__file__).resolve().parent.parent / 'assets' / fname
    return FileResponse(asset_path)

# Initialise a single Report instance (stateless; reused across requests)
report = Report()


@app.get('/')
def index():
    """Root route: defaults to employee id=1."""
    return report('1', Employee())


@app.get('/employee/{id}')
def employee(id: str):
    """Route for a single employee dashboard, e.g. /employee/2."""
    return report(id, Employee())


@app.get('/team/{id}')
def team(id: str):
    """Route for a team dashboard, e.g. /team/3."""
    return report(id, Team())


# ---------------------------------------------------------------------------
# Dynamic routes provided by the project skeleton – leave unchanged
# ---------------------------------------------------------------------------

@app.get('/update_dropdown{r}')
def update_dropdown(r):
    dropdown = DashboardFilters.children[1]
    print('PARAM', r.query_params['profile_type'])
    if r.query_params['profile_type'] == 'Team':
        return dropdown(None, Team())
    elif r.query_params['profile_type'] == 'Employee':
        return dropdown(None, Employee())


@app.post('/update_data')
async def update_data(r):
    from fasthtml.common import RedirectResponse
    data = await r.form()
    profile_type = data._dict['profile_type']
    id = data._dict['user-selection']
    if profile_type == 'Employee':
        return RedirectResponse(f"/employee/{id}", status_code=303)
    elif profile_type == 'Team':
        return RedirectResponse(f"/team/{id}", status_code=303)


serve()
