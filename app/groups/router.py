from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, get_db
from app.groups.schemas import (
    GroupCreate,
    GroupMemberCreate,
    GroupMemberResponse,
    GroupResponse,
    GroupUpdate,
)
from app.groups.service import GroupMemberService, GroupService
from app.users.models import User

router = APIRouter(prefix="/groups", tags=["groups"])


def get_group_service(db: AsyncSession = Depends(get_db)) -> GroupService:
    return GroupService(db)


def get_group_member_service(
    db: AsyncSession = Depends(get_db),
    group_service: GroupService = Depends(get_group_service),
) -> GroupMemberService:
    return GroupMemberService(db, group_service)


@router.post("/", response_model=GroupResponse)
async def create_group(
    data: GroupCreate,
    user: Annotated[User, Depends(get_current_user)],
    service: Annotated[GroupService, Depends(get_group_service)],
):
    return await service.create_group(data, user)


@router.get("/{group_id}", response_model=GroupResponse)
async def get_group(
    group_id: UUID,
    user: Annotated[User, Depends(get_current_user)],
    service: Annotated[GroupService, Depends(get_group_service)],
):
    group = await service.get_group_by_id(group_id, user)
    if group is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Group is not found")
    return group

@router.get("/", response_model=list[GroupResponse])
async def get_groups(user: Annotated[User, Depends(get_current_user)],service: Annotated[GroupService, Depends(get_group_service)]):
    return await service.get_groups(user)


@router.patch("/{group_id}", response_model=GroupResponse)
async def update_group(
    group_id: UUID,
    data: GroupUpdate,
    user: Annotated[User, Depends(get_current_user)],
    service: Annotated[GroupService, Depends(get_group_service)],
):
    return await service.update_group(group_id, data, user)


@router.delete("/{group_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_group(
    group_id: UUID,
    user: Annotated[User, Depends(get_current_user)],
    service: Annotated[GroupService, Depends(get_group_service)],
):
    await service.delete_group(group_id, user)


@router.get("/{group_id}/members", response_model=list[GroupMemberResponse])
async def get_group_members(
    group_id: UUID,
    user: Annotated[User, Depends(get_current_user)],
    service: Annotated[GroupMemberService, Depends(get_group_member_service)],
):
    return await service.get_group_members(group_id, user)


@router.post("/{group_id}/members", response_model=GroupMemberResponse)
async def create_group_member(
    group_id: UUID,
    data: GroupMemberCreate,
    user: Annotated[User, Depends(get_current_user)],
    service: Annotated[GroupMemberService, Depends(get_group_member_service)],
):
    return await service.create_group_member(data, user, group_id)
