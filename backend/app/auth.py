import asyncio
import logging

import jwt
from datetime import datetime, timedelta, UTC
from google.oauth2 import id_token
from google.auth.transport import requests

from config import settings

logger = logging.getLogger(__name__)


async def verify_google_token(token: str) -> dict | None:
    """
    Verifies the Google ID token and returns the decoded payload.
    Returns None if the token is invalid or the email is not verified.
    Raises on unexpected errors (network issues, Google outages, etc.)
    """
    try:
        loop = asyncio.get_event_loop()
        idinfo: dict = await loop.run_in_executor(
            None,
            lambda: id_token.verify_oauth2_token(
                token,
                requests.Request(),
                settings.GOOGLE_CLIENT_ID,
            ),
        )
    except ValueError as e:
        logger.warning("Invalid Google token: %s", e)
        return None
    except Exception as e:
        logger.error("Google token verification failed unexpectedly: %s", e)
        raise

    if not idinfo.get("email_verified"):
        logger.warning("Google token email not verified for: %s", idinfo.get("email"))
        return None

    return idinfo


def create_access_token(data: dict) -> str:
    """
    Creates a signed JWT to issue to the frontend.
    """
    to_encode = data.copy()
    expire = datetime.now(UTC) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({
        "exp": expire,
        "type": "access",
    })

    return jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )
