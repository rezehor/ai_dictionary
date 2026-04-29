from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import verify_google_token, create_access_token
from app.db.session import get_db
from app.models import User
from app.schemas import GoogleAuthRequest, TokenResponse


router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/google", response_model=TokenResponse)
async def google_login(request: GoogleAuthRequest, db: AsyncSession = Depends(get_db)):

    idinfo = await verify_google_token(request.credential)
    if not idinfo:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Google credentials",
        )

    email: str = idinfo["email"]
    google_id: str = idinfo["sub"]
    name: str | None = idinfo.get("name")

    result = await db.execute(select(User).where(User.google_id == google_id))
    user = result.scalar_one_or_none()

    if not user:
        user = User(email=email, google_id=google_id, full_name=name)
        db.add(user)
        await db.commit()
        await db.refresh(user)

    access_token = create_access_token(data={"sub": str(user.id)})

    return TokenResponse(access_token=access_token, token_type="bearer")
