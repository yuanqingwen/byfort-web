# placeholder for input validation

def ensure_text(s: str) -> str:
    return (s or "").strip()[:2000]
