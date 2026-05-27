from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User
from app.schemas import UserCreate, UserOut, Token
from app.auth import verify_password, get_password_hash, create_access_token, get_current_user

router = APIRouter(prefix="/api/auth", tags=["Autenticación"])


# POST /api/auth/register — registrar nuevo usuario
@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def registrar_usuario(datos: UserCreate, db: Session = Depends(get_db)):
    if db.query(User).filter(User.username == datos.username).first():
        raise HTTPException(status_code=400, detail="El nombre de usuario ya existe.")
    if db.query(User).filter(User.email == datos.email).first():
        raise HTTPException(status_code=400, detail="El email ya está registrado.")

    user = User(
        username=datos.username,
        email=datos.email,
        hashed_password=get_password_hash(datos.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


# POST /api/auth/token — login, devuelve JWT
@router.post("/token", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario o contraseña incorrectos.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.activo:
        raise HTTPException(status_code=400, detail="Usuario desactivado.")

    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}


# GET /api/auth/me — datos del usuario autenticado
@router.get("/me", response_model=UserOut)
def obtener_perfil(current_user: User = Depends(get_current_user)):
    return current_user
