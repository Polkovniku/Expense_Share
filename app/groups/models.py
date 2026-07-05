from datetime import datetime
import uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import DateTime, ForeignKey, func, String, UUID
from app.core.database import Base

class Group(Base):
    __tablename__="groups"
    
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    created_by: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    creator: Mapped["User"] = relationship(back_populates="created_groups")
    expenses: Mapped[list["Expense"]] = relationship(back_populates="group")
    group_members: Mapped[list["GroupMember"]] = relationship(back_populates="group")
    settlements: Mapped[list["Settlement"]] = relationship(back_populates="group")

class GroupMember(Base):
    __tablename__="group_members"
    
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    group_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("groups.id", ondelete="CASCADE"), nullable=False)
    user_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    display_name: Mapped[str] = mapped_column(String(50))
    joined_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    user: Mapped["User | None"] = relationship(back_populates="group_memberships")
    expenses_paid: Mapped[list["Expense"]] = relationship(back_populates="payer")
    group: Mapped["Group"] = relationship(back_populates="group_members")
    expense_shares: Mapped[list["ExpenseShare"]] = relationship(back_populates="member")
    
    settlements_sent: Mapped[list["Settlement"]] = relationship(
    back_populates="from_group_member",
    foreign_keys="Settlement.from_member",
    )
    settlements_received: Mapped[list["Settlement"]] = relationship(
        back_populates="to_group_member",
        foreign_keys="Settlement.to_member",
    )