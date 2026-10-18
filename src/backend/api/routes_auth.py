"""
Authentication & User Preferences API Router
"""

import re
from typing import Any, Dict, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, field_validator
from sqlalchemy.orm import Session

from src.backend.database.connection import get_db
from src.backend.database.models import User, UserPreferences
from src.backend.auth.security import (
    hash_password, verify_password, create_access_token, get_current_user
)

router = APIRouter(prefix="/auth", tags=["Authentication & User Profiles"])


class RegisterRequest(BaseModel):
    email: str
    username: str
    password: str
    full_name: Optional[str] = None

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        clean = v.strip().lower()
        if not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", clean):
            raise ValueError("Invalid email format")
        return clean


class LoginRequest(BaseModel):
    email: str
    password: str


class PreferencesUpdateRequest(BaseModel):
    default_routing_profile: Optional[str] = "FASTEST"
    avoid_highways: Optional[bool] = False
    avoid_tolls: Optional[bool] = False
    avoid_unpaved: Optional[bool] = True
    require_accessible: Optional[bool] = False
    avoid_stairs: Optional[bool] = False
    prefer_curb_ramps: Optional[bool] = False
    share_location_consent: Optional[bool] = False


@router.post("/register")
def register_user(req: RegisterRequest, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == req.email).first():
        raise HTTPException(status_code=400, detail="An account with this email already exists")
    if db.query(User).filter(User.username == req.username).first():
        raise HTTPException(status_code=400, detail="Username is already taken")

    user = User(
        email=req.email,
        username=req.username,
        hashed_password=hash_password(req.password),
        full_name=req.full_name,
        role="USER"
    )
    db.add(user)
    db.flush()

    prefs = UserPreferences(user_id=user.id)
    db.add(prefs)
    db.commit()
    db.refresh(user)

    token = create_access_token({"sub": user.id, "email": user.email, "role": user.role})
    return {
        "message": "User registered successfully",
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "username": user.username,
            "role": user.role
        }
    }


@router.post("/login")
def login_user(req: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(
        (User.email == req.email) | (User.username == req.email)
    ).first()
    if not user or not verify_password(req.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email/username or password"
        )
    if not user.is_active:
        raise HTTPException(status_code=403, detail="User account is suspended")

    token = create_access_token({"sub": user.id, "email": user.email, "role": user.role})
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "username": user.username,
            "full_name": user.full_name,
            "role": user.role
        }
    }


@router.get("/me")
def get_current_user_profile(current_user: User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "email": current_user.email,
        "username": current_user.username,
        "full_name": current_user.full_name,
        "role": current_user.role,
        "created_at": current_user.created_at.isoformat(),
        "preferences": {
            "default_routing_profile": current_user.preferences.default_routing_profile if current_user.preferences else "FASTEST",
            "require_accessible": current_user.preferences.require_accessible if current_user.preferences else False,
            "avoid_stairs": current_user.preferences.avoid_stairs if current_user.preferences else False,
            "avoid_tolls": current_user.preferences.avoid_tolls if current_user.preferences else False
        } if current_user.preferences else None
    }


@router.put("/preferences")
def update_preferences(
    req: PreferencesUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    prefs = current_user.preferences
    if not prefs:
        prefs = UserPreferences(user_id=current_user.id)
        db.add(prefs)

    for field, val in req.model_dump(exclude_unset=True).items():
        setattr(prefs, field, val)

    db.commit()
    db.refresh(prefs)
    return {"message": "Preferences updated successfully"}
