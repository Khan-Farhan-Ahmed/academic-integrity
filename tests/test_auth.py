from fastapi.testclient import TestClient
from fastapi import APIRouter, Depends
from backend.main import app
from backend.api.auth import get_current_user, get_instructor_user, User
import os

# Create a temporary router for testing auth dependencies
auth_test_router = APIRouter()

@auth_test_router.get("/api-auth-any")
def api_auth_any(user: User = Depends(get_current_user)):
    return {"user": user.model_dump()}

@auth_test_router.get("/api-auth-instructor")
def api_auth_instructor(user: User = Depends(get_instructor_user)):
    return {"user": user.model_dump()}

app.include_router(auth_test_router)

client = TestClient(app)

def test_unauthenticated_request():
    response = client.get("/api-auth-any")
    assert response.status_code == 403 or response.status_code == 401
    assert "Not authenticated" in response.json()["detail"]

def test_instructor_access():
    headers = {"Authorization": "Bearer mock-instructor-token"}
    response = client.get("/api-auth-instructor", headers=headers)
    assert response.status_code == 200
    assert response.json()["user"]["role"] == "instructor"

def test_student_access_any():
    headers = {"Authorization": "Bearer mock-student-token"}
    response = client.get("/api-auth-any", headers=headers)
    assert response.status_code == 200
    assert response.json()["user"]["role"] == "student"

def test_student_access_instructor_route_fails():
    headers = {"Authorization": "Bearer mock-student-token"}
    response = client.get("/api-auth-instructor", headers=headers)
    assert response.status_code == 403
    assert "Instructor access required" in response.json()["detail"]

def test_unauthorized_student_access_to_another_students_data():
    # Simulate a route that expects a specific student ID
    @app.get("/test-student-data/{student_id}")
    def get_student_data(student_id: str, user: User = Depends(get_current_user)):
        if user.role != "instructor" and user.id != student_id:
            from fastapi import HTTPException
            raise HTTPException(status_code=403, detail="Cannot access another student's data")
        return {"data": "secret"}
        
    # Test with stu_1 trying to access stu_2
    headers = {"Authorization": "Bearer mock-student-token"} # stu_1
    response = client.get("/test-student-data/stu_2", headers=headers)
    assert response.status_code == 403
    assert "Cannot access another student's data" in response.json()["detail"]
    
    # Test with stu_1 trying to access stu_1 (success)
    response = client.get("/test-student-data/stu_1", headers=headers)
    assert response.status_code == 200
    
    # Test with instructor trying to access stu_2 (success)
    headers = {"Authorization": "Bearer mock-instructor-token"}
    response = client.get("/test-student-data/stu_2", headers=headers)
    assert response.status_code == 200
