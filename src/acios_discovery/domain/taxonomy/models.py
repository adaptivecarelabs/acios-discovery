from pydantic import BaseModel


class Taxonomy(BaseModel):
    root: str
    industry: str
    sector: str | None = None
    category: str
    subcategory: str | None = None
