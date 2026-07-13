from decimal import Decimal
from pydantic import BaseModel, ConfigDict
from uuid import UUID


class SimplifiedDebtResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    from_member: UUID
    to_member: UUID
    amount: Decimal


