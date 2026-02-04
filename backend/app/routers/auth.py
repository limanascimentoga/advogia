from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import create_access_token, hash_password, verify_password
from app.deps import get_db
from app.models.user import User
from app.schemas.auth import Token, UserCreate, UserOut
from app.deps_auth import get_current_user
from app.models.organization import Organization
from app.models.membership import Membership



router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register(payload: UserCreate, db: Session = Depends(get_db)):
    email = str(payload.email).lower().strip()

    if db.query(User).filter(User.email == email).first():
        raise HTTPException(status_code=409, detail="email_ja_cadastrado")

    try:
        org = Organization(name="Meu escritorio")
        db.add(org)
        db.flush()  # garante org.id

        user = User(email=email, hashed_password=hash_password(payload.password))
        db.add(user)
        db.flush()  # garante user.id

        membership = Membership(user_id=user.id, organization_id=org.id, role="owner")
        db.add(membership)

        db.commit()
        db.refresh(user)
        return user
    except Exception:
        db.rollback()
        raise



@router.post("/login", response_model=Token)
def login(payload: UserCreate, db: Session = Depends(get_db)):
    email = str(payload.email).lower().strip()
    user = db.query(User).filter(User.email == email).first()

    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="credenciais_invalidas")

    token = create_access_token(subject=str(user.id))
    return Token(access_token=token)

@router.get("/me", response_model=UserOut)
def me(user: User = Depends(get_current_user)):
    return user
