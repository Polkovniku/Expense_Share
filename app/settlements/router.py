from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, get_db
from app.groups.service import GroupMemberService, GroupService
from app.settlements.schemas import SettlementCreate, SettlementResponse
from app.settlements.service import SettlementService
from app.users.models import User

router = APIRouter(prefix="/groups/{group_id}/settlements", tags=["settlements"])


def get_group_service(db: AsyncSession = Depends(get_db)) -> GroupService:
    return GroupService(db)


def get_group_member_service(
    db: AsyncSession = Depends(get_db),
    group_service: GroupService = Depends(get_group_service),
) -> GroupMemberService:
    return GroupMemberService(db, group_service)


def get_settlement_service(
    db: AsyncSession = Depends(get_db),
    group_service: GroupService = Depends(get_group_service),
    group_member_service: GroupMemberService = Depends(get_group_member_service),
) -> SettlementService:
    return SettlementService(db, group_service, group_member_service)


@router.get("/", response_model=list[SettlementResponse])
async def get_settlements(
    group_id: UUID,
    user: Annotated[User, Depends(get_current_user)],
    service: Annotated[SettlementService, Depends(get_settlement_service)],
):
    return await service.get_settlements(group_id, user)


@router.post("/", response_model=SettlementResponse)
async def create_settlement(
    group_id: UUID,
    data: SettlementCreate,
    user: Annotated[User, Depends(get_current_user)],
    service: Annotated[SettlementService, Depends(get_settlement_service)],
):
    return await service.create_settlement(group_id, data, user)
