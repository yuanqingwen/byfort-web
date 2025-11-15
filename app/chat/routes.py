from fastapi import APIRouter, Header, HTTPException
from app.chat.controller import save_message

router = APIRouter()

@router.post('/send')
async def send_chat(payload: dict, authorization: str = Header(None)):
    # payload: {"to": "user_id", "text": "..."}
    if not authorization:
        raise HTTPException(401, "Missing Authorization header")
    sender = authorization.split('-')[-1]
    await save_message(sender, payload.get('to'), payload.get('text'))
    return {"ok": True}
