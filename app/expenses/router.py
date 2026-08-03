from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, get_db
from app.expenses.schemas import ExpenseCreate, ExpenseResponse, ExpenseShareResponse
from app.expenses.service import ExpenseService
from app.groups.service import GroupMemberService, GroupService
from app.users.models import User

router = APIRouter(prefix="/groups/{group_id}/expenses", tags=["expenses"])


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


@router.get("/", response_model=list[ExpenseResponse])
async def get_expenses(
    group_id: UUID,
    user: Annotated[User, Depends(get_current_user)],
    service: Annotated[ExpenseService, Depends(get_expense_service)],
):
    return await service.get_expenses(user, group_id)


@router.post("/", response_model=ExpenseResponse)
async def create_expense(
    group_id: UUID,
    data: ExpenseCreate,
    user: Annotated[User, Depends(get_current_user)],
    service: Annotated[ExpenseService, Depends(get_expense_service)],
):
    return await service.create_expense(user, group_id, data)


@router.get("/{expense_id}", response_model=ExpenseResponse)
async def get_expense(
    group_id: UUID,
    expense_id: UUID,
    user: Annotated[User, Depends(get_current_user)],
    service: Annotated[ExpenseService, Depends(get_expense_service)],
):
    expense = await service.get_expense_by_id(expense_id, user)
    if expense is None or expense.group_id != group_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Expense is not found")
    return expense


@router.get("/{expense_id}/shares", response_model=list[ExpenseShareResponse])
async def get_expense_shares(
    group_id: UUID,
    expense_id: UUID,
    user: Annotated[User, Depends(get_current_user)],
    service: Annotated[ExpenseService, Depends(get_expense_service)],
):
    expense = await service.get_expense_by_id(expense_id, user)
    if expense is None or expense.group_id != group_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Expense is not found")
    return await service.get_expense_shares(expense_id, user)
