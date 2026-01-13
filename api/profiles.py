"""
Business Profile API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from database import get_db
from models import BusinessProfile, User
from schemas import (
    BusinessProfileCreate,
    BusinessProfileUpdate,
    BusinessProfileResponse
)
from api.dependencies import get_current_user

router = APIRouter(prefix="/profiles", tags=["Business Profiles"])


@router.post("", response_model=BusinessProfileResponse, status_code=status.HTTP_201_CREATED)
def create_profile(
    profile_data: BusinessProfileCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new business profile"""
    new_profile = BusinessProfile(**profile_data.model_dump())
    db.add(new_profile)
    db.commit()
    db.refresh(new_profile)
    return new_profile


@router.get("", response_model=List[BusinessProfileResponse])
def list_profiles(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all business profiles"""
    profiles = db.query(BusinessProfile).offset(skip).limit(limit).all()
    return profiles


@router.get("/{profile_id}", response_model=BusinessProfileResponse)
def get_profile(
    profile_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific business profile"""
    profile = db.query(BusinessProfile).filter(BusinessProfile.id == profile_id).first()
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Business profile not found"
        )
    return profile


@router.put("/{profile_id}", response_model=BusinessProfileResponse)
def update_profile(
    profile_id: int,
    profile_data: BusinessProfileUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a business profile"""
    profile = db.query(BusinessProfile).filter(BusinessProfile.id == profile_id).first()
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Business profile not found"
        )

    # Update fields
    for field, value in profile_data.model_dump(exclude_unset=True).items():
        setattr(profile, field, value)

    db.commit()
    db.refresh(profile)
    return profile


@router.delete("/{profile_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_profile(
    profile_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a business profile"""
    profile = db.query(BusinessProfile).filter(BusinessProfile.id == profile_id).first()
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Business profile not found"
        )

    db.delete(profile)
    db.commit()
    return None
