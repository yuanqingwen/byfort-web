from fastapi import APIRouter, Request, Header, HTTPException
from app.account.controller import create_or_get_device

router = APIRouter()

@router.post('/device-login')
async def device_login(request: Request, x_device_id: str = Header(None)):
    if not x_device_id:
        raise HTTPException(400, "Missing X-Device-ID header")
    user = await create_or_get_device(x_device_id)
    # return simple token (here using device id echo — for demo only)
    return {"user_id": user.get('user_id'), "device_id": x_device_id, "token": f"devtoken-{x_device_id}"}
