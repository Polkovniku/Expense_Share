from decimal import Decimal
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.balances.schemas import SimplifiedDebtResponse
from app.balances.service import BalanceService
from app.core.dependencies import get_current_user, get_db
from app.expenses.service import ExpenseService
from app.groups.service import GroupMemberService, GroupService
from app.settlements.service import SettlementService
from app.users.models import User

router = APIRouter(prefix="/groups/{group_id}/balances", tags=["balances"])


def get_group_service(db: AsyncSession = Depends(get_db)) -> GroupService:
    return GroupService(db)


def get_group_member_service(
    db: AsyncSession = Depends(get_db),
    group_service: GroupService = Depends(get_group_service),
) -> GroupMemberService:
    return GroupMemberService(db, group_service)


def get_expense_service(
    db: AsyncSession = Depends(get_db),
    group_service: GroupService = Depends(get_group_service),
    group_member_service: GroupMemberService = Depends(get_group_member_service),
) -> ExpenseService:
    return ExpenseService(db, group_service, group_member_service)


def get_settlement_service(
    db: AsyncSession = Depends(get_db),
    group_service: GroupService = Depends(get_group_service),
    group_member_service: GroupMemberService = Depends(get_group_member_service),
) -> SettlementService:
    return SettlementService(db, group_service, group_member_service)


def get_balance_service(
    db: AsyncSession = Depends(get_db),
    group_service: GroupService = Depends(get_group_service),
    group_member_service: GroupMemberService = Depends(get_group_member_service),
    expense_service: ExpenseService = Depends(get_expense_service),
    settlement_service: SettlementService = Depends(get_settlement_service),
) -> BalanceService:
    return BalanceService(db, group_service, group_member_service, expense_service, settlement_service)


@router.get("/", response_model=dict[str, Decimal])
async def get_balance(
    group_id: UUID,
    user: Annotated[User, Depends(get_current_user)],
    service: Annotated[BalanceService, Depends(get_balance_service)],
):
    return await service.calculate_balance(group_id, user)


@router.get("/simplified", response_model=list[SimplifiedDebtResponse])
async def simplify_debts(
    group_id: UUID,
    user: Annotated[User, Depends(get_current_user)],
    service: Annotated[BalanceService, Depends(get_balance_service)],
):
    return await service.simplify_debts(group_id, user)
