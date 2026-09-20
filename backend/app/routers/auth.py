from fastapi import APIRouter, Depends, HTTPException, status

from ..config import settings
from ..schemas import LoginIn
from ..security import create_token, current_username, hash_password, verify_password

# El acceso NO depende de Spark: así puedes entrar aunque Java o Spark fallen,
# y ver el motivo en Configuración. Cuando tengas MongoDB, los usuarios pasarán allí.
_ADMIN = {
    "username": settings.admin_username,
    "password_hash": hash_password(settings.admin_password),
    "full_name": settings.admin_name,
    "role": "Administrador",
}

router = APIRouter(prefix="/api/auth", tags=["auth"])


def _find_user(username: str) -> dict | None:
    return _ADMIN if username.strip().lower() == _ADMIN["username"].lower() else None


def _public(user: dict) -> dict:
    return {"username": user["username"], "full_name": user["full_name"], "role": user["role"]}


@router.post("/login")
def login(body: LoginIn):
    user = _find_user(body.username)
    if not user or not verify_password(body.password, user["password_hash"]):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Usuario o contraseña incorrectos.")
    return {"token": create_token(user["username"]), "user": _public(user)}


@router.get("/me")
def me(username: str = Depends(current_username)):
    user = _find_user(username)
    if not user:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "La cuenta ya no existe.")
    return _public(user)
