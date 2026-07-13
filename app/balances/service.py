from decimal import Decimal
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from app.expenses.models import Expense, ExpenseShare
from app.expenses.service import ExpenseService
from app.groups.service import GroupService, GroupMemberService
from uuid import UUID
from app.settlements.service import SettlementService
from app.users.models import User

class BalanceService:
    def __init__(
        self,
        db: AsyncSession,
        group_service: GroupService,
        group_member_service: GroupMemberService,
        expense_service: ExpenseService,
        settlement_service: SettlementService,    
    ):
        self.db = db
        self.group_service = group_service
        self.group_member_service = group_member_service
        self.expense_service = expense_service
        self.settlement_service = settlement_service
        
    async def calculate_balance(self, group_id: UUID, user: User) -> dict[UUID, Decimal]:
        group = await self.group_service.get_group_by_id(group_id, user)
        if group is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Group is not found")
        
        group_members = await self.group_member_service.get_group_members(group_id, user)
        member_ids = [m.id for m in group_members]
        
        expenses = await self.expense_service.get_expenses(user, group_id)
        balances = {id: Decimal(0) for id in member_ids}
        
        for expense in expenses:
            balances[expense.paid_by] += expense.amount
        
        expense_shares = (await self.db.scalars(
        select(ExpenseShare)
        .join(Expense, Expense.id == ExpenseShare.expense_id)
        .where(Expense.group_id == group_id)
        )).all()
        
        for share in expense_shares:
            balances[share.member_id] -= share.amount_owed
        
        settlements = await self.settlement_service.get_settlements(group_id, user)
        for settlement in settlements:
            balances[settlement.to_member] += settlement.amount
            balances[settlement.from_member] -= settlement.amount
        
        return balances
    
    
    async def simplify_debts(self, group_id: UUID, user: User):
        balances = await self.calculate_balance(group_id, user)
        result = list()
        creditors = list()
        debtors = list()
        
        for id, balance in balances.items():
            if balance > 0:
                creditors.append([id, balance])
            elif balance < 0:
                debtors.append([id, balance])
        
        
        while creditors and debtors:
            max_creditors = max(creditors, key=lambda x: x[1])
            min_debtors = min(debtors, key=lambda x: x[1])
            
            amount = min(max_creditors[1], -min_debtors[1])
            
            result.append({"from_member": min_debtors[0], "to_member": max_creditors[0], "amount": amount})
            
            max_creditors[1] -= amount
            min_debtors[1] += amount
            
            if max_creditors[1] == 0:
                creditors.remove(max_creditors)
            if min_debtors[1] == 0:
                debtors.remove(min_debtors)
        return result
        
        
        
        
        
        