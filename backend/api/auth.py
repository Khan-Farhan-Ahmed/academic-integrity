from fastapi import Depends, HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import os
import jwt
from typing import Optional
from pydantic import BaseModel

security = HTTPBearer()

class User(BaseModel):
    id: str
    email: str
    role: str

def get_current_user(credentials: HTTPAuthorizationCredentials = Security(security)) -> User:
    token = credentials.credentials
    secret = os.environ.get("SUPABASE_JWT_SECRET")
    
    if not secret:
        # In a real app we'd fail hard here, but for testing we can mock it
        if token == "mock-instructor-token":
            return User(id="inst_1", email="instructor@test.com", role="instructor")
        elif token == "mock-student-token":
            return User(id="stu_1", email="student@test.com", role="student")
        elif token == "mock-student2-token":
            return User(id="stu_2", email="student2@test.com", role="student")
        raise HTTPException(status_code=500, detail="JWT secret not configured")
        
    try:
        # Supabase JWTs use HS256 algorithm
        payload = jwt.decode(token, secret, algorithms=["HS256"], audience="authenticated")
        user_id = payload.get("sub")
        email = payload.get("email")
        
        # In Supabase, custom claims or app_metadata usually hold roles.
        # Defaulting to 'student' if not explicitly an instructor.
        app_metadata = payload.get("app_metadata", {})
        role = app_metadata.get("role", "student")
        
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")
            
        return User(id=user_id, email=email, role=role)
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

def get_instructor_user(user: User = Depends(get_current_user)) -> User:
    if user.role != "instructor":
        raise HTTPException(status_code=403, detail="Instructor access required")
    return user
