from datetime import datetime
from decimal import Decimal
from sqlalchemy import DateTime, func, UUID, ForeignKey, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base
import uuid

class Settlement(Base):
    __tablename__="settlements"
    
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    group_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("groups.id", ondelete="CASCADE"), nullable=False)
    from_member: Mapped[uuid.UUID] = mapped_column(ForeignKey("group_members.id", ondelete="RESTRICT"), nullable=False)
    to_member: Mapped[uuid.UUID] = mapped_column(ForeignKey("group_members.id", ondelete="RESTRICT"), nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    group: Mapped["Group"] = relationship(back_populates="settlements")
    
    from_group_member: Mapped["GroupMember"] = relationship(
        back_populates="settlements_sent",
        foreign_keys=[from_member],
    )
    to_group_member: Mapped["GroupMember"] = relationship(
        back_populates="settlements_received",
        foreign_keys=[to_member],
    )
    
    