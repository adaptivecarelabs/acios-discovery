from dataclasses import dataclass, field


@dataclass(slots=True)
class Discovery:

    business_name: str

    detail_url: str

    address: str | None = None

    description: str | None = None

    phone_numbers: list[str] = field(default_factory=list)

    email: str | None = None

    website: str | None = None

    social_links: dict[str, str] = field(default_factory=dict)

    year_founded: int | None = None

    employee_count: str | None = None

    business_locations: int | None = None

    product_types: list[str] = field(default_factory=list)

    payment_methods: list[str] = field(default_factory=list)
