from pydantic import BaseModel


class Taxonomy(BaseModel):
    industry: str
    sector: str | None = None
    category: str
    subcategory: str | None = None
