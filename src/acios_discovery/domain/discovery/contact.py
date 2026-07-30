from pydantic import BaseModel, ConfigDict, Field


class BusinessContact(BaseModel):
    model_config = ConfigDict(
        frozen=True,
    )

    phone_numbers: list[str] = Field(
        default_factory=list,
    )

    emails: list[str] = Field(
        default_factory=list,
    )

    websites: list[str] = Field(
        default_factory=list,
    )
