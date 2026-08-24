from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from api.utils.security import decode_access_token

security = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    token = credentials.credentials
    payload = decode_access_token(token)
    user_id = payload.get("sub")
    role = payload.get("role")
    if user_id is None or role is None:
        raise HTTPException(status_code=401, detail="Invalid token payload.")
    return {"user_id": int(user_id), "role": role}

def get_current_student(user: dict = Depends(get_current_user)) -> dict:
    """Dependency to enforce that the user is a student."""
    if user.get("role") != "student":
        raise HTTPException(status_code=403, detail="Access denied. Student privileges required.")
    return user

def get_current_professor(user: dict = Depends(get_current_user)) -> dict:
    """Dependency to enforce that the user is a professor (or admin)."""
    role = user.get("role")
    if role not in ["professor", "admin"]:
        raise HTTPException(status_code=403, detail="Access denied. Professor privileges required.")
    return user