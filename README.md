# Reality Distortion Engine

An AI-powered fake news detector built with Flask and scikit-learn.

## Features
- ML classifier (Logistic Regression, 99% accuracy)
- Rule-based detection (clickbait, CAPS, punctuation)
- Confidence score + explanation output
- Clean dark-themed web UI

## Tech Stack
- Backend: Python, Flask
- ML: scikit-learn, TF-IDF
- Frontend: HTML, CSS, JavaScript
- Dataset: Fake and Real News Dataset (Kaggle)

## Setup

### 1. Install dependencies
pip install -r requirements.txt

### 2. Add dataset
Download Fake.csv and True.csv from Kaggle and place in /data

### 3. Train the model
python backend/train_model.py

### 4. Run the server
python backend/app.py

### 5. Open the frontend
Open frontend/index.html in your browser
