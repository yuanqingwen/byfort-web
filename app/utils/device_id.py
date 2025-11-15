import hashlib

def normalize_device_id(raw: str) -> str:
    # simple normalization + hashing to avoid storing raw device ids
    if not raw:
        raw = "unknown"
    return hashlib.sha256(raw.encode()).hexdigest()[:32]
