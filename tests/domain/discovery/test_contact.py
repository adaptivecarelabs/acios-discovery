from acios_discovery.domain.discovery.contact import (
    BusinessContact,
)


def test_business_contact_defaults() -> None:
    contact = BusinessContact()

    assert contact.phone_numbers == []
    assert contact.emails == []
    assert contact.websites == []


def test_business_contact_accepts_values() -> None:
    contact = BusinessContact(
        phone_numbers=[
            "08032852530",
            "08149666894",
        ],
        emails=[
            "info@example.com",
            "sales@example.com",
        ],
        websites=[
            "https://example.com",
            "https://shop.example.com",
        ],
    )

    assert contact.phone_numbers == [
        "08032852530",
        "08149666894",
    ]

    assert contact.emails == [
        "info@example.com",
        "sales@example.com",
    ]

    assert contact.websites == [
        "https://example.com",
        "https://shop.example.com",
    ]


def test_business_contact_accepts_empty_lists() -> None:
    contact = BusinessContact(
        phone_numbers=[],
        emails=[],
        websites=[],
    )

    assert contact.phone_numbers == []
    assert contact.emails == []
    assert contact.websites == []
