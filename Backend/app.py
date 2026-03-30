# backend/app.py  (FINAL VERSION)

from flask import Flask, request, jsonify
from flask_cors import CORS
import classifier
import rules
import explainer

app = Flask(__name__)
CORS(app)

# Load ML model once at startup
classifier.load_model()


@app.route('/')
def home():
    return jsonify({"message": "Reality Distortion Engine is running!"})


@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.get_json()

    if not data or 'text' not in data:
        return jsonify({"error": "No text provided"}), 400

    text = data['text'].strip()

    if len(text) < 15:
        return jsonify({"error": "Text too short. Please enter at least one sentence."}), 400

    # Step 1: ML prediction
    ml_result = classifier.predict(text)

    # Step 2: Rule-based analysis
    rule_result = rules.analyze_rules(text)

    # Step 3: Combine scores → final label
    label, final_score = explainer.determine_label(
        ml_fake_prob=ml_result['fake_probability'],
        rule_score=rule_result['rule_score']
    )

    # Step 4: Generate explanation
    explanation_text = explainer.generate_explanation(
        label=label,
        final_score=final_score,
        ml_result=ml_result,
        rule_result=rule_result
    )

    return jsonify({
        "label": label,
        "confidence": round(final_score * 100, 1),  # As percentage
        "ml_score": round(ml_result['fake_probability'] * 100, 1),
        "rule_score": round(rule_result['rule_score'] * 100, 1),
        "rule_flags": rule_result['flags'],
        "explanation": explanation_text
    })


if __name__ == '__main__':
    app.run(debug=True, port=5000)