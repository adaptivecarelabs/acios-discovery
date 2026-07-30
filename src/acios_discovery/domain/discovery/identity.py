from pydantic import BaseModel, ConfigDict


class BusinessIdentity(BaseModel):
    model_config = ConfigDict( frozen=True )

    business_name: str

    normalized_name: str | None = None
