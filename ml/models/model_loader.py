import json
import os
import pickle

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
REGISTRY_PATH = os.path.join(BASE_DIR, "model_registry.json")


def load_registry() -> dict:
    with open(REGISTRY_PATH, "r") as f:
        return json.load(f)


def load_model(model_id: int) -> tuple:
    """
    Load a registered model by its model_id.

    Returns:
        model         : trained sklearn/xgboost model
        explainer     : SHAP explainer
        feature_names : list of feature names
        metadata      : dict from model_registry.json
    """
    registry = load_registry()

    entry = next((m for m in registry["models"] if m["model_id"] == model_id), None)
    if entry is None:
        raise ValueError(f"model_id {model_id} not found in registry.")

    model_dir = os.path.join(BASE_DIR, str(model_id))
    model_file = "lr_model.pkl" if entry["algorithm"] == "LogisticRegression" else "xgb_model.pkl"

    with open(os.path.join(model_dir, model_file), "rb") as f:
        model = pickle.load(f)

    with open(os.path.join(model_dir, "explainer.pkl"), "rb") as f:
        explainer = pickle.load(f)

    with open(os.path.join(model_dir, "feature_names.pkl"), "rb") as f:
        feature_names = pickle.load(f)

    return model, explainer, feature_names, entry