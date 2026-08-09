from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from acios_discovery.infrastructure.persistence.metadata import Base


class WebsiteORM(Base):

    __tablename__ = "company_websites"

    id: Mapped[int] = mapped_column(
        primary_key=True,
    )

    company_id: Mapped[str] = mapped_column(
        ForeignKey("companies.id"),
    )

    value: Mapped[str] = mapped_column(
        String(500),
        index=True,
    )

    normalized_value: Mapped[str] = mapped_column(
        String(255),
        index=True,
        nullable=False,
    )

    company = relationship(
        "CompanyORM",
        back_populates="websites",
    )
