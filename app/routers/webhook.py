from __future__ import annotations

import hashlib
import hmac
import os

from fastapi import APIRouter, HTTPException, Request

router = APIRouter()


@router.post("/webhook")
async def webhook(request: Request) -> dict:
    body = await request.body()
    signature = request.headers.get("X-Line-Signature", "")
    secret = os.getenv("LINE_CHANNEL_SECRET", "").encode()
    digest = hmac.new(secret, body, hashlib.sha256).digest()
    import base64
    expected = base64.b64encode(digest).decode()
    if not hmac.compare_digest(expected, signature):
        raise HTTPException(status_code=400, detail="Invalid signature")
    return {"status": "ok"}
