from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from acios_discovery.infrastructure.persistence.metadata import Base


class StateORM(Base):

    __tablename__ = "company_states"

    id: Mapped[int] = mapped_column(primary_key=True)

    company_id: Mapped[str] = mapped_column(
        ForeignKey("companies.id"),
        index=True,
    )

    value: Mapped[str] = mapped_column(
        String(120),
        index=True,
    )

    company = relationship(
        "CompanyORM",
        back_populates="states",
    )
