from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql.functions import func
from sqlalchemy.sql.sqltypes import DateTime
from sqlalchemy.sql.schema import ForeignKey

from app.db import Base

if TYPE_CHECKING:
    from app.models.files import File  # noqa: F401


class Remark(Base):
    __tablename__ = "remarks"

    id: Mapped[int] = mapped_column(primary_key=True)
    file_id: Mapped[int] = mapped_column(ForeignKey("files.id"))
    file: Mapped["File"] = relationship(back_populates="remarks")

    page_num: Mapped[int | None]
    golden_name: Mapped[str | None]
    targets: Mapped[str | None]
    candidate: Mapped[str | None]
    probability: Mapped[float | None]
    similarity: Mapped[float | None]

    created: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
