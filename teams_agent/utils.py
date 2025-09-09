import re

# Accepts formatted (99.999.999/9999-99) and unformatted (99999999999999) CNPJ, with optional separators
_CNPJ_FLEX_RE = re.compile(
    r"(\d{2})[\.\s-]?(\d{3})[\.\s-]?(\d{3})[\//\s-]?(\d{4})[-\s]?(\d{2})"
)

def extract_cnpj(text: str | None) -> str | None:
    if not text:
        return None
    m = _CNPJ_FLEX_RE.search(text)
    if not m:
        return None
    g1, g2, g3, g4, g5 = m.groups()
    return f"{g1}.{g2}.{g3}/{g4}-{g5}"
