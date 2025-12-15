# backend/app/utils/text_normalizer.py
import re
import pandas as pd

def norm_text(s):
    if pd.isna(s):
        return ""

    s = str(s).strip().replace('\\N', ' ')
    s = s.lower()

    # Insert space when letters+numbers stick together
    s = re.sub(r'([a-z]+)([0-9]+)', r'\1 \2', s)
    s = re.sub(r'([0-9]+)([a-z]+)', r'\1 \2', s)

    # Common stuck-word splitting dictionary
    dictionary = ["gold","chain","bangle","haram","ring","women","ladies","mens","unisex","silver"]
    for word in dictionary:
        s = s.replace(word, f" {word} ")

    # Remove unwanted characters
    s = re.sub(r'[^a-z0-9\.\-\s]', ' ', s)
    s = re.sub(r'\s+', ' ', s).strip()

    return s
