from datetime import date

from pydantic import BaseModel, ConfigDict


class BusinessRegistration(BaseModel):
    """
    Represents legal registration information obtained
    from the Corporate Affairs Commission (CAC).

    This model is NEVER populated by directory connectors
    such as Finelib, BusinessList, or ConnectNigeria.
    """

    model_config = ConfigDict( frozen=True )

    registration_number: str | None = None

    entity_type: str | None = None

    incorporation_date: date | None = None

    status: str | None = None
