"""
Ported 1:1 from the original js/data.js computeScore()/matchLabel() so the
scoring behaviour judges and citizens already saw in the demo stays
identical once this moves server-side.
"""

import re
from datetime import date
from typing import Optional

from app.reference_data import PS_TO_DISTRICT

STOPWORDS = {
    "the", "and", "with", "for", "this", "that", "from", "have", "was", "are",
    "black", "white", "blue", "red", "green", "grey", "gray", "silver", "gold",
    "small", "large", "new", "old",
}

_WORD_RE = re.compile(r"[a-z0-9]+")


def tokenize(text: Optional[str]) -> set:
    if not text:
        return set()
    words = _WORD_RE.findall(text.lower())
    return {w for w in words if len(w) > 2 and w not in STOPWORDS}


def compute_score(found, stolen) -> int:
    """
    `found` and `stolen` are any objects exposing the attributes:
    category, brand, color, location_ps, event_date, item_name, description
    (works with both SQLAlchemy model instances and plain dicts via getattr).
    """
    def g(obj, key):
        return obj.get(key) if isinstance(obj, dict) else getattr(obj, key, None)

    score = 0

    if g(found, "category") and g(found, "category") == g(stolen, "category"):
        score += 30

    f_brand, s_brand = g(found, "brand"), g(stolen, "brand")
    if f_brand and s_brand and f_brand.strip().lower() == s_brand.strip().lower():
        score += 20

    f_color, s_color = g(found, "color"), g(stolen, "color")
    if f_color and s_color and f_color.strip().lower() == s_color.strip().lower():
        score += 15

    f_ps, s_ps = g(found, "location_ps"), g(stolen, "location_ps")
    if f_ps == s_ps:
        score += 15
    elif PS_TO_DISTRICT.get(f_ps) and PS_TO_DISTRICT.get(f_ps) == PS_TO_DISTRICT.get(s_ps):
        score += 7

    lost_date: Optional[date] = g(stolen, "event_date")
    found_date: Optional[date] = g(found, "event_date")
    if lost_date and found_date and found_date >= lost_date:
        diff_days = (found_date - lost_date).days
        if diff_days <= 90:
            score += 10

    kw_found = tokenize(f"{g(found, 'item_name') or ''} {g(found, 'description') or ''}")
    kw_stolen = tokenize(f"{g(stolen, 'item_name') or ''} {g(stolen, 'description') or ''}")
    overlap = kw_found & kw_stolen
    score += min(10, len(overlap) * 3)

    return min(100, score)


def match_label(score: int) -> Optional[str]:
    if score >= 70:
        return "Strong Match"
    if score >= 45:
        return "Possible Match"
    return None
