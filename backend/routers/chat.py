from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
import json

from database import get_db, SessionLocal
from models import ChatMessage, SenderType, Property

router = APIRouter(prefix="/chat", tags=["chat"])

# property_id -> list of active WebSocket connections
_connections: dict[int, list[WebSocket]] = {}


class MessageIn(BaseModel):
    property_id: int
    session_token: str
    sender: SenderType
    sender_name: str
    content: str


class MessageOut(BaseModel):
    id: int
    property_id: int
    session_token: str
    sender: SenderType
    sender_name: str
    content: str
    created_at: str

    model_config = {"from_attributes": True}


@router.get("/{property_id}/{session_token}", response_model=list[MessageOut])
def get_messages(property_id: int, session_token: str, db: Session = Depends(get_db)):
    msgs = (
        db.query(ChatMessage)
        .filter(
            ChatMessage.property_id == property_id,
            ChatMessage.session_token == session_token,
        )
        .order_by(ChatMessage.created_at)
        .all()
    )
    return [_to_out(m) for m in msgs]


@router.post("/", response_model=MessageOut, status_code=201)
def post_message(payload: MessageIn, db: Session = Depends(get_db)):
    prop = db.query(Property).filter(Property.id == payload.property_id).first()
    if not prop:
        raise HTTPException(status_code=404, detail="Property not found")

    msg = ChatMessage(**payload.model_dump())
    db.add(msg)
    db.commit()
    db.refresh(msg)
    return _to_out(msg)


@router.websocket("/ws/{property_id}/{session_token}")
async def websocket_chat(websocket: WebSocket, property_id: int, session_token: str):
    await websocket.accept()
    _connections.setdefault(property_id, []).append(websocket)

    try:
        while True:
            raw = await websocket.receive_text()
            data = json.loads(raw)

            db = SessionLocal()
            try:
                prop = db.query(Property).filter(Property.id == property_id).first()
                if not prop:
                    await websocket.send_text(json.dumps({"error": "Property not found"}))
                    continue

                msg = ChatMessage(
                    property_id=property_id,
                    session_token=session_token,
                    sender=data.get("sender", "renter"),
                    sender_name=data.get("sender_name", "Anonymous"),
                    content=data["content"],
                )
                db.add(msg)
                db.commit()
                db.refresh(msg)
                out = json.dumps(_to_out(msg))
            finally:
                db.close()

            for ws in list(_connections.get(property_id, [])):
                try:
                    await ws.send_text(out)
                except Exception:
                    _connections[property_id].remove(ws)

    except WebSocketDisconnect:
        conns = _connections.get(property_id, [])
        if websocket in conns:
            conns.remove(websocket)


def _to_out(msg: ChatMessage) -> dict:
    return {
        "id": msg.id,
        "property_id": msg.property_id,
        "session_token": msg.session_token,
        "sender": msg.sender,
        "sender_name": msg.sender_name,
        "content": msg.content,
        "created_at": msg.created_at.isoformat() if msg.created_at else "",
    }
