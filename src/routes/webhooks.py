from fastapi import APIRouter, Request, HTTPException, Depends
from sqlalchemy.orm import Session

from ..database.db import create_challenge_quota
from ..database.models import get_db
from svix.webhooks import Webhook
import os
import json

router = APIRouter()

@router.post('/clerk')
async def handle_user_creation(request: Request, db:Session = Depends(get_db)):
    webhook_secret = os.getenv('CLERK_WEBHOOK_SECRET')
    if not webhook_secret:
        raise HTTPException(status_code=500, detail="Webhook secret not configured")

    body = await request.body()
    payload = body.decode('utf-8')
    headers = dict(request.headers)

    try:
        wh = Webhook(webhook_secret)
        wh.verify(payload, headers)

        data = json.loads(payload)

        if data.get('type') == 'user.created':
            user_data = data.get('data', {})
            user_id = user_data.get('id')

            if user_id:
                create_challenge_quota(db, user_id)
                return {'status': 'success', 'message': 'User quota created'}
            else:
                raise HTTPException(status_code=400, detail="User ID not found in webhook data")

        return {'status': 'ignored', 'message': 'Event type not handled'}

    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))