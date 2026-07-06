from pydantic import BaseModel, ConfigDict, Field
from uuid import UUID
from datetime import datetime

class GroupResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    name: str
    created_by: UUID
    created_at: datetime
    
class GroupCreate(BaseModel):
    name: str = Field(min_length=2, max_length=100)

class GroupUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=100)
    

class GroupMemberResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    group_id: UUID
    user_id: UUID | None
    display_name: str
    joined_at: datetime
    
class GroupMemberCreate(BaseModel):
    display_name: str = Field(min_length=1, max_length=50)