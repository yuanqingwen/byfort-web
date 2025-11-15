from app.database.models import DeviceUser
from app.database.config import get_session
from app.utils.device_id import normalize_device_id
import uuid
import asyncio

async def create_or_get_device(device_id: str):
    device_id = normalize_device_id(device_id)
    async with get_session() as s:
        q = await s.exec(DeviceUser.select().where(DeviceUser.c.device_id==device_id))
        res = q.first()
        if res:
            return res
        # create
        uid = f"u{str(uuid.uuid4())[:8]}"
        rec = {"user_id": uid, "device_id": device_id, "created_at": None, "display_name": uid}
        await s.execute(DeviceUser.insert().values(**rec))
        await s.commit()
        return rec
