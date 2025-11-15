from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from app.account.routes import router as account_router
from app.chat.routes import router as chat_router
from app.realtime.socket_server import websocket_endpoint
from app.database import config as db_config
import os

app = FastAPI(title="BYFORT AI - Starter")

# Mount static frontend
app.mount("/static", StaticFiles(directory="static"), name="static")

# include routers
app.include_router(account_router, prefix="/api/auth", tags=["auth"])
app.include_router(chat_router, prefix="/api/chat", tags=["chat"])

@app.get("/", response_class=HTMLResponse)
def index():
    return FileResponse(os.path.join("static","index.html"))

# lightweight health
@app.get('/health')
def health():
    return {"status":"ok"}

# WebSocket endpoint for realtime chat
@app.websocket('/ws')
async def ws_endpoint(websocket: WebSocket):
    await websocket.accept()
    await websocket_endpoint(websocket)
