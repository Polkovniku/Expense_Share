from pydantic import BaseModel, ConfigDict, Field
from uuid import UUID
from datetime import datetime
from decimal import Decimal

class ExpenseResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    group_id: UUID
    paid_by: UUID
    description: str
    amount: Decimal
    created_at: datetime
    
class ExpenseCreate(BaseModel):
    group_id: UUID
    paid_by: UUID
    description: str = Field(min_length=5, max_length=250)
    amount: Decimal = Field(gt=0)

class ExpenseUpdate(BaseModel):
    description: str | None = Field(default=None, min_length=5, max_length=250)
    amount: Decimal | None = Field(default=None, gt=0)


class ExpenseShareResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    expense_id: UUID
    member_id: UUID
    amount_owed: Decimal
    
class ExpenseShareCreate(BaseModel):
    expense_id: UUID
    member_id: UUID
    amount_owed: Decimal = Field(gt=0)