# backend/classifier.py
"""
Loads the saved ML model and exposes prediction functions.
This is a SEPARATE file from train_model.py.
train_model.py  → trains and saves the model to disk (run once)
classifier.py   → loads the saved model and predicts (used by app.py)
"""

import os
import joblib

MODEL_DIR = os.path.join(os.path.dirname(__file__), 'model_files')

# Module-level variables — loaded once when Flask starts
_model = None
_vectorizer = None


def load_model():
    """Load model and vectorizer from disk. Called once at startup."""
    global _model, _vectorizer

    model_path = os.path.join(MODEL_DIR, 'classifier.pkl')
    vec_path   = os.path.join(MODEL_DIR, 'vectorizer.pkl')

    if not os.path.exists(model_path):
        raise FileNotFoundError(
            "Model not found! Please run: python train_model.py"
        )

    _model      = joblib.load(model_path)
    _vectorizer = joblib.load(vec_path)
    print("ML model loaded successfully.")


def predict(text: str) -> dict:
    """
    Predicts whether text is fake or real.

    Returns:
        {
          "ml_label": "Fake" | "Real",
          "fake_probability": float (0.0 to 1.0),
          "real_probability": float (0.0 to 1.0)
        }
    """
    if _model is None or _vectorizer is None:
        raise RuntimeError("Model not loaded. Call load_model() first.")

    # Transform input text using the same vectorizer from training
    X = _vectorizer.transform([text])

    # predict_proba returns [[real_prob, fake_prob]]
    probabilities = _model.predict_proba(X)[0]

    real_prob = float(probabilities[0])
    fake_prob = float(probabilities[1])

    ml_label = "Fake" if fake_prob >= 0.5 else "Real"

    return {
        "ml_label":         ml_label,
        "fake_probability": round(fake_prob, 4),
        "real_probability": round(real_prob, 4)
    }   