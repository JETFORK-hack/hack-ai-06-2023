from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql.functions import func
from sqlalchemy.sql.sqltypes import DateTime
from sqlalchemy.sql.schema import ForeignKey

from app.db import Base

if TYPE_CHECKING:
    from app.models.bundle import Bundle  # noqa: F401
    from app.models.remark import Remark  # noqa: F401


class File(Base):
    __tablename__ = "files"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str | None]
    size: Mapped[int | None]
    download_id: Mapped[UUID] = mapped_column(UUID, ForeignKey("bundles.id"))
    download: Mapped["Bundle"] = relationship(back_populates="files")
    path: Mapped[str | None]

    created: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    remarks: Mapped["Remark"] = relationship(
        back_populates="file", cascade="all, delete")
