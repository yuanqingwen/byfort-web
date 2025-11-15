# lightweight token helpers — production should use jose / HS256 properly
from jose import jwt
from datetime import datetime, timedelta

SECRET = "change-this-secret"

def create_token(sub: str, minutes: int = 60*24*365):
    exp = datetime.utcnow() + timedelta(minutes=minutes)
    return jwt.encode({"sub": sub, "exp": exp.isoformat()}, SECRET, algorithm="HS256")
