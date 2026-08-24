from pydantic import BaseModel, EmailStr, Field
from typing import Optional

# new user registers
class UserCreate(BaseModel):
    email: EmailStr = Field(..., description="The user's email address.")
    password: str = Field(..., min_length=8, description="Plain text password (will be hashed).")
    role: str = Field(..., description="Must be 'student', 'professor', or 'admin'.")
    invite_code: Optional[str] = Field(None, description="Required security code for creating professor or admin accounts.")
    user_identifier: str = Field(..., description= "User's full name")

# user attempts to log in
class UserLogin(BaseModel):
    email: EmailStr
    password: str

# response sent back upon successful login
class TokenResponse(BaseModel):
    access_token: str = Field(..., description="The JWT string.")
    token_type: str = Field("bearer", description="The type of token.")
    role: str = Field(..., description="The user's role for frontend routing.")
    user_identifier: str = Field(..., description="The student's full name")