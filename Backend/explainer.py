# backend/explainer.py
"""
Generates human-readable explanations for classification decisions.
Combines ML model signals with rule-based flags.
"""


def generate_explanation(
    label: str,
    final_score: float,
    ml_result: dict,
    rule_result: dict
) -> str:
    """
    Builds a plain-English explanation of the result.
    
    Args:
        label: Final label ("Real", "Fake", or "Misleading")
        final_score: Combined fake probability (0.0 to 1.0)
        ml_result: Output from model.predict()
        rule_result: Output from rules.analyze_rules()
    
    Returns:
        A readable explanation string.
    """
    lines = []

    # --- Opening verdict ---
    confidence_pct = f"{final_score * 100:.0f}%"
    
    if label == "Fake":
        lines.append(
            f"This content was classified as FAKE with {confidence_pct} confidence."
        )
    elif label == "Misleading":
        lines.append(
            f"This content was classified as MISLEADING with {confidence_pct} confidence. "
            "It may contain some factual elements mixed with distorted framing."
        )
    else:
        lines.append(
            f"This content appears to be REAL with {(1 - final_score) * 100:.0f}% confidence."
        )

    # --- ML signal ---
    fake_pct = ml_result['fake_probability'] * 100
    real_pct = ml_result['real_probability'] * 100
    
    lines.append(
        f"\nML model analysis: The trained classifier assigned a "
        f"{fake_pct:.0f}% fake probability and {real_pct:.0f}% real probability "
        "based on writing patterns and vocabulary learned from thousands of articles."
    )

    # --- Rule-based flags ---
    flags = rule_result.get('flags', [])
    
    if flags:
        lines.append("\nRule-based red flags detected:")
        for flag in flags[:5]:   # Show up to 5 flags
            lines.append(f"  • {flag}")
    else:
        lines.append(
            "\nNo rule-based red flags were detected — "
            "no unusual capitalization, clickbait words, or sensational phrasing found."
        )

    # --- Specific patterns found ---
    clickbait = rule_result.get('clickbait_words', [])
    emotional = rule_result.get('emotional_phrases', [])
    
    if clickbait:
        lines.append(
            f"\nClickbait terms found: {', '.join(clickbait[:5])}. "
            "These words are disproportionately common in fabricated or misleading content."
        )
    
    if emotional:
        lines.append(
            f"\nEmotional manipulation phrases: '{', '.join(emotional[:3])}'. "
            "These are frequently used to bypass critical thinking."
        )

    # --- Confidence caveat ---
    if 0.4 <= final_score <= 0.6:
        lines.append(
            "\nNote: The confidence score is in the uncertain range (40–60%). "
            "Treat this result with caution and verify with trusted sources."
        )

    lines.append(
        "\nRemember: Always cross-check important news with multiple credible sources."
    )

    return "\n".join(lines)


def determine_label(ml_fake_prob: float, rule_score: float) -> tuple:
    """
    Combines ML probability and rule score to determine the final label.
    
    Logic:
    - High ML + High rules  → Fake
    - High ML + Low rules   → Fake (model is confident)
    - Low ML + High rules   → Misleading (passes ML but has suspicious language)
    - Low ML + Low rules    → Real
    
    Returns:
        (label: str, final_score: float)
    """
    # Weighted combination: 70% ML, 30% rules
    combined = (0.70 * ml_fake_prob) + (0.30 * rule_score)
    combined = round(combined, 4)

    if combined >= 0.60:
        label = "Fake"
    elif combined >= 0.35:
        # Edge case: rule engine flags it but ML thinks it's real → "Misleading"
        if rule_score >= 0.4 and ml_fake_prob < 0.5:
            label = "Misleading"
        else:
            label = "Fake"
    else:
        label = "Real"

    return label, combined  