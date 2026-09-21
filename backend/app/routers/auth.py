from fastapi import APIRouter, Depends, HTTPException, status

from ..repository import find_user
from ..schemas import LoginIn
from ..security import create_token, current_username, verify_password

router = APIRouter(prefix="/api/auth", tags=["auth"])


def _public(user: dict) -> dict:
    return {"username": user["username"], "full_name": user["full_name"], "role": user["role"]}


@router.post("/login")
def login(body: LoginIn):
    user = find_user(body.username)
    if not user or not user.get("active", True) or not verify_password(body.password, user["password_hash"]):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Usuario o contraseña incorrectos.")
    return {"token": create_token(user["username"]), "user": _public(user)}


@router.get("/me")
def me(username: str = Depends(current_username)):
    user = find_user(username)
    if not user or not user.get("active", True):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "La cuenta ya no existe o está desactivada.")
    return _public(user)
