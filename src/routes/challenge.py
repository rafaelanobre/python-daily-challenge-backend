from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from sqlalchemy.orm import Session
import json
from datetime import datetime

from ..ai_generator import generate_challenge_with_ai
from ..database.db import (
    get_challenge_quota,
    create_challenge,
    create_challenge_quota,
    reset_quota_if_needed,
    get_user_challenges
)
from ..utils import authenticate_and_get_user_details
from ..database.models import get_db
from ..logger import get_logger

router = APIRouter()
logger = get_logger()

class ChallengeRequest(BaseModel):
    difficulty: str

    class Config:
        json_schema_extra = {'example': {'difficulty': 'easy'}}

@router.post('/generate-challenge')
async def generate_challenge(
        request: ChallengeRequest,
        request_obj: Request,
        db: Session = Depends(get_db)
):
    user_id = None
    try:
        user_details = authenticate_and_get_user_details(request_obj)
        user_id = user_details.get('user_id')

        logger.info(f"User {user_id} requested a {request.difficulty} challenge")

        quota = get_challenge_quota(db, user_id)
        if not quota:
            logger.info(f"Creating new challenge quota for user {user_id}")
            quota = create_challenge_quota(db, user_id)

        quota = reset_quota_if_needed(db, quota)

        if quota.quota_remaining <= 0:
            logger.warning(f"User {user_id} quota exhausted")
            raise HTTPException(status_code=429, detail='Quota exhausted')

        challenge_data = generate_challenge_with_ai(request.difficulty)

        challenge_data['options'] = json.dumps(challenge_data['options']) if not isinstance(challenge_data['options'], str) else challenge_data['options']

        new_challenge = create_challenge(
            db,
            request.difficulty,
            user_id,
            challenge_data['title'],
            challenge_data['options'],
            challenge_data['correct_answer_id'],
            challenge_data['explanation'],
        )

        quota.quota_remaining -=1
        db.commit()

        logger.info(f"Successfully created challenge {new_challenge.id} for user {user_id}")

        options = new_challenge.options
        if isinstance(options, str):
            options = json.loads(options)

        return {
            'id': new_challenge.id,
            'difficulty': request.difficulty,
            'title': new_challenge.title,
            'options': options,
            'correct_answer_id': new_challenge.correct_answer_id,
            'explanation': new_challenge.explanation,
            'timestamp': new_challenge.date_created.isoformat(),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating challenge for user {user_id if user_id else 'unknown'}: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get('/my-history')
async def my_history(request: Request, db: Session = Depends(get_db)):
    user_id = None
    try:
        user_details = authenticate_and_get_user_details(request)
        user_id = user_details.get('user_id')

        logger.info(f"User {user_id} requested challenge history")

        challenges = get_user_challenges(db, user_id)
        logger.debug(f"Found {len(challenges) if challenges else 0} challenges for user {user_id}")
        return {'challenges': challenges}
    except Exception as e:
        logger.error(f"Error getting challenge history for user {user_id if user_id else 'unknown'}: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@router.get('/quota')
async def get_quota(request: Request, db: Session = Depends(get_db)):
    user_id = None
    try:
        user_details = authenticate_and_get_user_details(request)
        user_id = user_details.get('user_id')

        logger.info(f"User {user_id} requested quota information")

        quota = get_challenge_quota(db, user_id)
        if not quota:
            logger.debug(f"No quota found for user {user_id}, returning default")
            return {
                'user_id': user_id,
                'quota_remaining': 0,
                'last_reset_date': datetime.now()
            }
        quota = reset_quota_if_needed(db, quota)
        logger.debug(f"User {user_id} quota: {quota.quota_remaining} remaining")
        return quota
    except Exception as e:
        logger.error(f"Error getting quota information for user {user_id if user_id else 'unknown'}: {e}")
        raise HTTPException(status_code=400, detail=str(e))
