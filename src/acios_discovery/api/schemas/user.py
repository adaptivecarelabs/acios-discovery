from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, EmailStr


class CreateUserRequest(BaseModel):
    email: EmailStr
    password: str
    role: str = "member"


class UpdateUserRequest(BaseModel):
    role: str | None = None
    active: bool | None = None


class UserResponse(BaseModel):
    id: str
    email: str
    role: str
    active: bool
    created_at: datetime
