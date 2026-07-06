from datetime import datetime
from decimal import Decimal
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field, model_validator

class SettlementResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    group_id: UUID
    from_member: UUID
    to_member: UUID
    amount: Decimal
    created_at: datetime
    
class SettlementCreate(BaseModel):
    from_member: UUID
    to_member: UUID
    amount: Decimal = Field(gt=0)
    
    @model_validator(mode="after")
    def check_different_members(self):
        if self.from_member == self.to_member:
            raise ValueError("from_member and to_member can't match")
        return self 
    