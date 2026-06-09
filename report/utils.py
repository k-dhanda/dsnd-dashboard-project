import pickle
from pathlib import Path

# Absolute path of the project root directory.
# utils.py lives at <project_root>/report/utils.py
# so parent.parent resolves to <project_root>.
project_root = Path(__file__).resolve().parent.parent

# Path to the pre-trained scikit-learn model artifact
model_path = project_root / 'assets' / 'model.pkl'


def load_model():
    """
    Unpickle and return the recruitment-risk ML model.

    Returns
    -------
    sklearn estimator
        Fitted classifier with a ``predict_proba`` method.
    """
    with model_path.open('rb') as file:
        model = pickle.load(file)

    return model
