from datetime import datetime
from decimal import Decimal
from sqlalchemy import DateTime, func, UUID, ForeignKey, String, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base
import uuid

class Expense(Base):
    __tablename__="expenses"
    
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    group_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("groups.id", ondelete="CASCADE"), nullable=False)
    paid_by: Mapped[uuid.UUID] = mapped_column(ForeignKey("group_members.id", ondelete="RESTRICT"), nullable=False)
    description: Mapped[str] = mapped_column(String(250), nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    group: Mapped["Group"] = relationship(back_populates="expenses")
    payer: Mapped["GroupMember"] = relationship(back_populates="expenses_paid")
    expense_shares: Mapped[list["ExpenseShare"]] = relationship(back_populates="expense")
    
class ExpenseShare(Base):
    __tablename__="expense_shares"
    
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    expense_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("expenses.id", ondelete="CASCADE"), nullable=False)
    member_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("group_members.id", ondelete="RESTRICT"), nullable=False)
    amount_owed: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    
    member: Mapped["GroupMember"] = relationship(back_populates="expense_shares")
    expense: Mapped["Expense"] = relationship(back_populates="expense_shares")