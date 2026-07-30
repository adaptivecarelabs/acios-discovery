from bs4 import Tag


def extract_text(
    parent: Tag,
    selector: str,
    *,
    required: bool = True,
) -> str | None:
    """
    Extract stripped text from the first matching element.
    """

    element = parent.select_one(selector)

    if element is None:
        if required:
            raise ValueError(
                f"Selector not found: {selector}"
            )

        return None

    return element.get_text(" ", strip=True)


def extract_link(
    parent: Tag,
    selector: str,
    *,
    required: bool = True,
) -> str | None:
    """
    Extract href from the first matching anchor.
    """

    element = parent.select_one(selector)

    if element is None:
        if required:
            raise ValueError(
                f"Selector not found: {selector}"
            )

        return None

    href = element.get("href")

    if not href:
        if required:
            raise ValueError(
                f"Empty href for selector: {selector}"
            )

        return None

    return href


def extract_phone_list(
    phone_text: str,
) -> list[str]:
    """
    Split a raw phone string into individual numbers.

    Example:

    "0803 111 1111, 0805 222 2222"

    becomes

    [
        "0803 111 1111",
        "0805 222 2222",
    ]
    """

    return [
        phone.strip()
        for phone in phone_text.split(",")
        if phone.strip()
    ]
