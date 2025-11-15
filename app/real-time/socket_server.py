import json
from fastapi import WebSocket
from app.chat.controller import save_message

# very small in-memory connection manager
class ConnectionManager:
    def __init__(self):
        self.active = {}

    async def connect(self, websocket: WebSocket, user_id: str):
        await websocket.accept()
        self.active[user_id] = websocket

    def disconnect(self, user_id: str):
        self.active.pop(user_id, None)

    async def send_personal(self, user_id: str, message: dict):
        ws = self.active.get(user_id)
        if ws:
            await ws.send_json(message)

    async def broadcast(self, message: dict):
        for ws in list(self.active.values()):
            await ws.send_json(message)

manager = ConnectionManager()

async def websocket_endpoint(websocket: WebSocket):
    try:
        # expect header-like query param ?user=devtoken-<deviceid>
        query = websocket.query_params
        token = query.get('token','anonymous')
        user_id = token.split('-')[-1]
        await manager.connect(websocket, user_id)
        await manager.send_personal(user_id, {"system":"connected","user":user_id})
        while True:
            data = await websocket.receive_json()
            # echo back & persist
            text = data.get('text')
            to = data.get('to','server')
            await save_message(user_id, to, text)
            await manager.send_personal(user_id, {"from":user_id, "to":to, "text":text})
    except Exception:
        manager.disconnect(user_id)
