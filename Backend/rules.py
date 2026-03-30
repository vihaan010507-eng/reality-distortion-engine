# backend/rules.py
"""
Rule-based fake news detector.
Scans text for linguistic red flags commonly found in misleading content.
"""

import re
import string

# Words frequently used in clickbait and fake news headlines
CLICKBAIT_WORDS = [
    "shocking", "unbelievable", "you won't believe", "mind-blowing",
    "secret", "they don't want you to know", "miracle", "exposed",
    "breaking", "urgent", "warning", "alert", "banned", "censored",
    "conspiracy", "hoax", "fake", "fraud", "scam", "crisis", "bombshell",
    "explosive", "stunning", "outrageous", "scandalous", "terrifying",
    "must see", "share before deleted", "mainstream media won't show"
]

# Emotionally charged / sensational phrases
EMOTIONAL_PHRASES = [
    "wake up", "sheeple", "deep state", "new world order",
    "they're hiding", "the truth about", "what they don't tell you",
    "100% proven", "doctors hate", "one weird trick"
]


def count_caps_ratio(text: str) -> float:
    """Returns the ratio of uppercase letters to total letters."""
    letters = [c for c in text if c.isalpha()]
    if not letters:
        return 0.0
    caps = [c for c in letters if c.isupper()]
    return len(caps) / len(letters)


def count_exclamations(text: str) -> int:
    """Counts exclamation marks — overuse signals sensationalism."""
    return text.count('!')


def count_question_marks(text: str) -> int:
    """Multiple ?? marks are a red flag."""
    return text.count('?')


def find_clickbait_words(text: str) -> list:
    """Returns list of clickbait words found in the text."""
    text_lower = text.lower()
    found = []
    for word in CLICKBAIT_WORDS:
        if word in text_lower:
            found.append(word)
    return found


def find_emotional_phrases(text: str) -> list:
    """Returns list of emotionally manipulative phrases found."""
    text_lower = text.lower()
    found = []
    for phrase in EMOTIONAL_PHRASES:
        if phrase in text_lower:
            found.append(phrase)
    return found


def has_all_caps_words(text: str) -> list:
    """Returns words written in ALL CAPS (3+ letters). Signals urgency/panic."""
    words = text.split()
    caps_words = [w for w in words if w.isupper() and len(w) >= 3 
                  and w not in ['USA', 'UK', 'FBI', 'CIA', 'CDC', 'WHO', 'UN']]
    return caps_words


def count_numbers_and_stats(text: str) -> int:
    """
    Fake news often uses oddly specific stats to seem credible.
    Counts number-like patterns. (This is a weak signal, used lightly.)
    """
    return len(re.findall(r'\b\d+[\.,]?\d*%?\b', text))


def analyze_rules(text: str) -> dict:
    """
    Master function: runs all rule checks and returns a structured result.
    Returns a score between 0.0 (clean) and 1.0 (very suspicious).
    """
    flags = []
    penalty = 0.0

    # --- Check 1: Excessive caps ---
    caps_ratio = count_caps_ratio(text)
    if caps_ratio > 0.5:
        flags.append(f"Very high uppercase ratio ({caps_ratio:.0%}) — suggests panic or shouting")
        penalty += 0.35
    elif caps_ratio > 0.3:
        flags.append(f"Elevated uppercase usage ({caps_ratio:.0%})")
        penalty += 0.15

    # --- Check 2: ALL CAPS words ---
    caps_words = has_all_caps_words(text)
    if caps_words:
        flags.append(f"ALL CAPS words detected: {', '.join(caps_words[:5])}")
        penalty += min(0.1 * len(caps_words), 0.25)

    # --- Check 3: Clickbait words ---
    clickbait = find_clickbait_words(text)
    if clickbait:
        flags.append(f"Clickbait language: '{', '.join(clickbait[:4])}'")
        penalty += min(0.12 * len(clickbait), 0.35)

    # --- Check 4: Emotional manipulation phrases ---
    emotional = find_emotional_phrases(text)
    if emotional:
        flags.append(f"Manipulative phrasing: '{', '.join(emotional[:3])}'")
        penalty += min(0.15 * len(emotional), 0.3)

    # --- Check 5: Excessive punctuation ---
    exclamations = count_exclamations(text)
    if exclamations >= 3:
        flags.append(f"Excessive exclamation marks ({exclamations})")
        penalty += min(0.08 * exclamations, 0.2)
    elif exclamations == 2:
        flags.append("Multiple exclamation marks")
        penalty += 0.05

    question_marks = count_question_marks(text)
    if question_marks >= 2:
        flags.append(f"Multiple question marks ({question_marks}) — often used to imply doubt")
        penalty += 0.05

    # Clamp score to [0.0, 1.0]
    rule_score = min(penalty, 1.0)

    return {
        "rule_score": round(rule_score, 3),
        "flags": flags,
        "caps_ratio": round(caps_ratio, 3),
        "clickbait_words": clickbait,
        "emotional_phrases": emotional,
        "caps_words": caps_words[:5]
    }