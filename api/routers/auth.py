from fastapi import APIRouter, HTTPException
from api.schemas.auth_schemas import UserCreate, UserLogin, TokenResponse
from api.utils.security import get_password_hash, verify_password, create_access_token
from shared.utils.db_utils import get_db_connection

router = APIRouter(prefix="/api/v1/auth", tags=["Authentication"])

# In production, store this in an environment variable
PROFESSOR_INVITE_CODE = "MAS-PROF-2026"
ADMIN_INVITE_CODE = "MAS-ADMIN-MASTER"

@router.post("/register")
async def register_user(request: UserCreate):
    """Registers a new user. Enforces invite codes for elevated roles."""
    
    # enforce Role-Based Invite Codes
    if request.role == "professor" and request.invite_code != PROFESSOR_INVITE_CODE:
        raise HTTPException(status_code=403, detail="Invalid invite code for professor registration.")
    if request.role == "admin" and request.invite_code != ADMIN_INVITE_CODE:
        raise HTTPException(status_code=403, detail="Invalid invite code for admin registration.")
        
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()    
            cursor.execute("SELECT UserID FROM Users WHERE Email = ?", (request.email,))
            if cursor.fetchone():
                raise HTTPException(status_code=400, detail="Email is already registered.")         
            # hash pw and insert the user
            hashed_pw = get_password_hash(request.password)
            
            query = """INSERT INTO Users (Email, HashedPassword, Role, IsActive)
                VALUES (?, ?, ?, 1)"""
            cursor.execute(query, (request.email, hashed_pw, request.role))
            conn.commit()
            return {"message": f"User {request.email} registered successfully as {request.role}."}           
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@router.post("/login", response_model=TokenResponse)
async def login_user(request: UserLogin):
    """Verifies credentials and returns a JWT access token"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT UserID, HashedPassword, Role, IsActive FROM Users WHERE Email = ?", 
                (request.email,))
            user = cursor.fetchone()
            
        if not user:
            raise HTTPException(status_code=401, detail="Invalid email or password")
        if not user.IsActive:
            raise HTTPException(status_code=403, detail= "Account has been deactivated")
            
        if not verify_password(request.password, user.HashedPassword):
            raise HTTPException(status_code=401, detail="Invalid email or password")
            
        # gen JWT
        token = create_access_token(user_id=user.UserID, role=user.Role)
        return TokenResponse(
            access_token=token,
            token_type="bearer",
            role=user.Role
        )        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")