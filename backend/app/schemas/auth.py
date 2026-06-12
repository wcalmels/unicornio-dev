from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class RegisterReq(BaseModel):
    email: EmailStr
    name: str = Field(..., min_length=1, max_length=100)
    password: str = Field(..., min_length=8, max_length=128)


class LoginReq(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=1, max_length=128)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    id: int
    email: str
    name: str
    plan: str
    created_at: datetime


class ProjectCreateReq(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    description: str = Field(default="", max_length=10_000)


class ProjectResponse(BaseModel):
    id: int
    name: str
    description: str
    created_at: datetime


class QueryHistoryItem(BaseModel):
    id: int
    module: str
    input_data: dict
    output_text: str
    project_id: int | None
    created_at: datetime
