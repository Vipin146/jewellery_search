# backend/app/services/search_engine.py
from typing import List, Dict, Any, Optional
import re, math
from collections import defaultdict, Counter
import pandas as pd
from rapidfuzz import fuzz, process
from app.services.synonyms import SYNONYM_TO_CANONICAL
from app.utils.text_normalizer import norm_text

class SearchEngine:
    def __init__(self, df: pd.DataFrame):
        self.df = df.copy().reset_index(drop=True)
        self._build_index()

    def _tokens_of(self, text: str):
        return re.findall(r'\w+', text or "")

    def _build_index(self):
        self.token_to_products = defaultdict(list)
        self.token_counts = Counter()

        for idx, row in self.df.iterrows():
            tokens = set(self._tokens_of(row['search_text']))
            for t in tokens:
                self.token_to_products[t].append(idx)
                self.token_counts[t] += 1

        # Thumbnail per token
        self.token_thumbnail = {}
        for t, ids in self.token_to_products.items():
            thumb = ""
            for i in ids:
                img = self.df.at[i, 'image']
                if pd.notna(img) and str(img).strip():
                    thumb = img
                    break
            self.token_thumbnail[t] = thumb

    def _token_overlap(self, q_tokens, t_tokens):
        if not q_tokens or not t_tokens:
            return 0.0
        return len(set(q_tokens) & set(t_tokens)) / max(1, len(q_tokens))

    def _fuzzy(self, a, b):
        if not a or not b:
            return 0.0
        return max(
            fuzz.token_sort_ratio(a, b) / 100.0,
            fuzz.partial_ratio(a, b) / 100.0
        )

    def _weight_score(self, product_weight, desired):
        try:
            if math.isnan(product_weight) or math.isnan(desired):
                return 0.0
        except:
            return 0.0
        diff = abs(product_weight - desired)
        return max(0.0, 1.0 - (diff / (desired + 1)))

    def search_products(self, query, top_n=10, weight_pref=None):
        q = norm_text(query)
        q_tokens = self._tokens_of(q)

        # expand synonyms
        expanded = {SYNONYM_TO_CANONICAL[t] for t in q_tokens if t in SYNONYM_TO_CANONICAL}

        scores = []
        for idx, row in self.df.iterrows():
            text = row['search_text']
            tokens = self._tokens_of(text)
            score = 0

            score += self._token_overlap(q_tokens, tokens) * 5
            score += self._fuzzy(q, text) * 3
            if any(t in text for t in q_tokens):
                score += 0.5

            if row['gender_norm'] in expanded:
                score += 2

            # weight match
            w = row['weight_num']
            nums = [float(t) for t in q_tokens if re.fullmatch(r'\d+(\.\d+)?', t)]
            if nums:
                score += self._weight_score(w, nums[0]) * 2
            elif weight_pref:
                score += self._weight_score(w, weight_pref) * 1.5

            scores.append((idx, score))

        scores.sort(key=lambda x: x[1], reverse=True)

        # fallback
        if not scores or scores[0][1] < 0.4:
            fallback = []
            for idx, row in self.df.iterrows():
                fr = fuzz.partial_ratio(q, row['category_norm']) / 100.0
                fallback.append((idx, fr))
            fallback.sort(key=lambda x: x[1], reverse=True)
            ids = [i for i, _ in fallback[:top_n]]
            res = self.df.loc[ids]
            res.attrs['reason'] = 'fallback'
            return res

        ids = [i for i, _ in scores[:top_n]]
        res = self.df.loc[ids]
        res.attrs['reason'] = 'direct match'
        return res

    def autocomplete(self, prefix, top_n=8):
        p = norm_text(prefix)
        candidates = [(t, self.token_counts[t]) for t in self.token_to_products if t.startswith(p)]
        if not candidates:
            matches = process.extract(p, list(self.token_to_products.keys()), limit=top_n, scorer=fuzz.partial_ratio)
            candidates = [(m[0], self.token_counts[m[0]]) for m in matches if m[1] > 30]

        candidates.sort(key=lambda x: x[1], reverse=True)

        return [
            {"suggestion": t, "thumbnail": self.token_thumbnail[t], "count": c}
            for t, c in candidates[:top_n]
        ]

    def explain(self, query, index):
        q = norm_text(query)
        row = self.df.loc[index]
        return {
            "product_id": row['jbo_own_products_id'],
            "search_text": row['search_text'],
            "explanation": "Breakdown",
        }
