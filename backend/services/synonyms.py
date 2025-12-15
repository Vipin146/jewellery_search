# backend/app/services/synonyms.py
from app.utils.text_normalizer import norm_text

# Gender synonyms
GENDER_SYNONYMS = {
    'male': ['male','man','men','boy','boys','his','he','gent','gentleman','mens'],
    'female': ['female','woman','women','girl','girls','her','she','ladies','lady'],
    'unisex': ['unisex','both','universal','neutral','for all','gender neutral','mens/womens','unisexs']
}

# Domain synonyms
DOMAIN_SYNONYMS = {
    'haram': ['haram','necklace','neckpieces'],
    'bangle': ['bangle','bangles','bracelet','bracelets'],
    'chain': ['chain','chains'],
    'ring': ['ring','rings'],
}

# Reverse lookup dictionary
SYNONYM_TO_CANONICAL = {}

for canon, words in GENDER_SYNONYMS.items():
    for w in words:
        SYNONYM_TO_CANONICAL[norm_text(w)] = canon

for canon, words in DOMAIN_SYNONYMS.items():
    for w in words:
        SYNONYM_TO_CANONICAL[norm_text(w)] = canon

# Allow dynamic synonym addition
def add_domain_synonyms(canonical: str, synonyms: list):
    canon_norm = norm_text(canonical)
    if canon_norm not in DOMAIN_SYNONYMS:
        DOMAIN_SYNONYMS[canon_norm] = []

    for s in synonyms:
        s_norm = norm_text(s)
        DOMAIN_SYNONYMS[canon_norm].append(s_norm)
        SYNONYM_TO_CANONICAL[s_norm] = canon_norm
