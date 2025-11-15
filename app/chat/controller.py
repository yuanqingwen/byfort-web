from app.database.config import get_session
from app.database.models import ChatMessage
import datetime

async def save_message(sender, receiver, text):
    now = datetime.datetime.utcnow().isoformat()
    async with get_session() as s:
        await s.execute(ChatMessage.insert().values(sender=sender, receiver=receiver, message=text, timestamp=now))
        await s.commit()
