from datetime import datetime
from typing import TYPE_CHECKING
from uuid import uuid4

from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql.functions import func
from sqlalchemy.sql.sqltypes import DateTime

from app.db import Base

if TYPE_CHECKING:
    from app.models.files import File  # noqa: F401


class Bundle(Base):
    __tablename__ = "bundles"

    id: Mapped[UUID] = mapped_column(UUID(
        as_uuid=True), primary_key=True, default=uuid4)

    path: Mapped[str | None]
    entity: Mapped[str | None]
    status: Mapped[str | None]
    message: Mapped[str | None]

    created: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    files: Mapped["File"] = relationship(
        back_populates="download", cascade="all, delete")
