"""
Utility functions for AI incident data normalization and intersectional validation.
Centralizing this logic ensures consistency between terminal reports and graphs.
"""

# Semantic overlaps that should be ignored for intersectional analysis
REDUNDANT_PAIRS = {
    ("race", "people of color", "skin_tone", "dark"),
    ("race", "black", "skin_tone", "dark"),
    ("age", "adolescent", "education", "student"),
    ("age", "child", "education", "student"),
    ("age", "young adult", "education", "student"),
    ("ability", "disabled", "health_status", "physically disabled"),
    ("ability", "disabled", "health_status", "disabled"),
}

def normalize_marker(cat, marker):
    """Standardizes identity markers to fix LLM inconsistencies and group synonyms."""
    marker = marker.lower().strip()
    cat = cat.lower().replace(" ", "_")
    
    # Class Normalization
    if cat == "class":
        lower_synonyms = ["working class", "low-income", "low income", "lower class", "poor", "poverty"]
        upper_synonyms = ["upper class", "wealthy", "affluent", "elite"]
        if marker in lower_synonyms: return "lower class"
        if marker in upper_synonyms: return "upper class"
    
    # Gender Normalization
    if cat == "gender":
        if marker in ["female", "woman", "women"]: return "female"
        if marker in ["male", "man", "men"]: return "male"

    # Race Normalization
    if cat == "race":
        if marker in ["black", "african american"]: return "black"
        if marker in ["poc", "people of color", "person of color"]: return "people of color"
            
    return marker

def is_valid_intersection(v1, v2):
    """
    Determines if a pair of markers represents a valid intersectional interaction.
    Filters out intra-category pairs and predefined semantic redundancies.
    """
    cat1, val1 = v1
    cat2, val2 = v2
    
    # Rule 1: No same-category intersections
    if cat1 == cat2:
        return False
    
    # Rule 2: Check against redundancy dictionary
    if (cat1, val1, cat2, val2) in REDUNDANT_PAIRS or \
       (cat2, val2, cat1, val1) in REDUNDANT_PAIRS:
        return False
        
    return True

def get_causal_markers(subject, exclude=["geography", "species"]):
    """Extracts standardized markers passing the CQ1=Yes, CQ2=No filter."""
    ids = subject.get("identity_markers", {})
    valid_markers = {}
    for c, v in ids.items():
        cat = c.lower().replace(" ", "_")
        if cat in exclude: continue
        if not isinstance(v, dict): continue
        
        # Apply Causal Gate: CQ1 (Necessity) and CQ2 (Inherent Harm)
        if str(v.get("DirectScore", "")).strip().lower() == "yes" and \
           str(v.get("AlternateScore", "")).strip().lower() == "no":
            norm_val = normalize_marker(cat, str(v.get("marker", "")))
            valid_markers[cat] = norm_val
    return valid_markers