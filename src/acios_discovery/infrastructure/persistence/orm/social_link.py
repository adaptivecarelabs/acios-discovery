from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from acios_discovery.infrastructure.persistence.metadata import Base


class SocialLinkORM(Base):

    __tablename__ = "company_social_links"

    id: Mapped[int] = mapped_column(primary_key=True)

    company_id: Mapped[str] = mapped_column(
        ForeignKey("companies.id"),
        index=True,
    )

    value: Mapped[str]

    company = relationship(
        "CompanyORM",
        back_populates="social_links",
    )
