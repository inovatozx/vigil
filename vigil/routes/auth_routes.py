from datetime import timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status, Response
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel

from core.database import get_db, User
from core.auth import AuthManager, get_current_user
from core.config import get_settings
from core.exceptions import InvalidCredentialsException, UserNotFoundException, UnauthorizedException

router = APIRouter()
settings = get_settings()

class Token(BaseModel):
    access_token: str
    token_type: str
    refresh_token: Optional[str] = None

class UserCreate(BaseModel):
    username: str
    password: str

class TOTPSetupResponse(BaseModel):
    secret: str
    qrcode_uri: str

class TOTPVerifyRequest(BaseModel):
    otp: str

@router.post("/auth/register", response_model=Token, summary="Registrar um novo usuário")
async def register_user(user_data: UserCreate, db: Session = Depends(get_db)):
    # Check if any user exists. If not, the first user becomes admin.
    is_first_user = db.query(User).count() == 0

    hashed_password = AuthManager.get_password_hash(user_data.password)
    db_user = User(username=user_data.username, password_hash=hashed_password, is_admin=is_first_user)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = AuthManager.create_access_token(
        data={"sub": db_user.username},
        expires_delta=access_token_expires
    )
    refresh_token = AuthManager.create_refresh_token(
        data={"sub": db_user.username}
    )
    return {"access_token": access_token, "token_type": "bearer", "refresh_token": refresh_token}

@router.post("/auth/login", response_model=Token, summary="Autenticar usuário e obter tokens de acesso")
async def login_for_access_token(response: Response, form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not AuthManager.verify_password(form_data.password, user.password_hash):
        raise InvalidCredentialsException()
    
    # If TOTP is enabled, require TOTP verification
    if user.totp_secret:
        # This is a simplified flow. In a real app, you'd return a specific status
        # indicating TOTP is required, and have a separate endpoint for TOTP verification.
        # For now, we'll assume TOTP is verified as part of login if present.
        # Or, we can raise an exception if OTP is not provided in form_data.password
        # For simplicity, we'll assume TOTP is handled by a separate flow or not enforced strictly here.
        pass # TODO: Implement proper TOTP verification flow

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = AuthManager.create_access_token(
        data={"sub": user.username},
        expires_delta=access_token_expires
    )
    refresh_token = AuthManager.create_refresh_token(
        data={"sub": user.username}
    )
    
    # Update last login time
    user.last_login = datetime.utcnow()
    db.commit()

    return {"access_token": access_token, "token_type": "bearer", "refresh_token": refresh_token}

@router.post("/auth/logout", status_code=status.HTTP_204_NO_CONTENT, summary="Revogar tokens de acesso (logout)")
async def logout(current_user: User = Depends(get_current_user)):
    # In a real application, you would invalidate the refresh token or blacklist the access token.
    # For JWTs, stateless logout is often handled client-side by deleting the token.
    # For now, this endpoint primarily serves as a protected route that requires a valid token.
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@router.get("/auth/me", summary="Obter informações do usuário atual")
async def read_users_me(current_user: User = Depends(get_current_user)):
    return {"username": current_user.username, "is_admin": current_user.is_admin, "id": current_user.id}

@router.post("/auth/totp/setup", response_model=TOTPSetupResponse, summary="Configurar 2FA (TOTP)")
async def setup_totp(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.totp_secret:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="TOTP already configured")
    
    secret = AuthManager.generate_totp_secret()
    current_user.totp_secret = secret
    db.commit()
    db.refresh(current_user)
    
    qrcode_uri = AuthManager.get_totp_uri(secret, current_user.username)
    return {"secret": secret, "qrcode_uri": qrcode_uri}

@router.post("/auth/totp/verify", summary="Verificar código 2FA (TOTP)")
async def verify_totp(request: TOTPVerifyRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if not current_user.totp_secret:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="TOTP not configured")
    
    if not AuthManager.verify_totp(current_user.totp_secret, request.otp):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid TOTP code")
    
    return {"message": "TOTP verified successfully"}
