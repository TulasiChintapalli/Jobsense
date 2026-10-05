import re

def clean_text(t):
    """Light cleaning only: keeps tech terms like c++, c#, node.js."""
    t = re.sub(r"<[^>]+>", " ", str(t).lower())
    t = re.sub(r"[^a-z0-9+#.\s]", " ", t)
    return re.sub(r"\s+", " ", t).strip()

def clean_frame(df, text_col, target_col):
    df = df[[text_col, target_col]].dropna().copy()
    df[text_col] = df[text_col].map(clean_text)
    df[target_col] = df[target_col].astype(str).str.strip()
    df = df[(df[text_col].str.len() > 30) & (df[target_col] != "")]
    return df.drop_duplicates(subset=[text_col])
