# backend/train_model.py
"""
Trains a Logistic Regression model on the Fake/True news dataset.
Run this script ONCE before starting the Flask server.
Usage: python backend/train_model.py
"""

import os
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, accuracy_score
import joblib

# --- Paths ---
DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')
MODEL_DIR = os.path.join(os.path.dirname(__file__), 'model_files')
os.makedirs(MODEL_DIR, exist_ok=True)

print("Loading dataset...")
fake_df = pd.read_csv(os.path.join(DATA_DIR, 'Fake.csv'))
true_df = pd.read_csv(os.path.join(DATA_DIR, 'True.csv'))

# Label: 1 = Fake, 0 = Real
fake_df['label'] = 1
true_df['label'] = 0

# Combine and shuffle
df = pd.concat([fake_df, true_df], ignore_index=True)
df = df.sample(frac=1, random_state=42).reset_index(drop=True)

print(f"Dataset size: {len(df)} articles")
print(f"Fake: {fake_df.shape[0]} | Real: {true_df.shape[0]}")

# Use title + text combined for better signal
df['content'] = df['title'].fillna('') + ' ' + df['text'].fillna('')

# --- Vectorize ---
print("\nVectorizing text with TF-IDF...")
vectorizer = TfidfVectorizer(
    max_features=10000,   # Top 10k words by frequency
    ngram_range=(1, 2),   # Unigrams and bigrams
    stop_words='english', # Remove "the", "is", etc.
    min_df=5              # Ignore very rare words
)

X = vectorizer.fit_transform(df['content'])
y = df['label']

# --- Train/test split ---
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

print(f"Training on {X_train.shape[0]} samples...")

# --- Train Logistic Regression ---
model = LogisticRegression(
    max_iter=1000,
    C=1.0,        # Regularization strength
    solver='lbfgs'
)
model.fit(X_train, y_train)

# --- Evaluate ---
y_pred = model.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)
print(f"\nModel accuracy: {accuracy:.2%}")
print("\nDetailed report:")
print(classification_report(y_test, y_pred, target_names=['Real', 'Fake']))

# --- Save ---
model_path = os.path.join(MODEL_DIR, 'classifier.pkl')
vec_path = os.path.join(MODEL_DIR, 'vectorizer.pkl')
joblib.dump(model, model_path)
joblib.dump(vectorizer, vec_path)
print(f"\nModel saved to: {model_path}")
print(f"Vectorizer saved to: {vec_path}")
print("\nDone! You can now start the Flask server.")