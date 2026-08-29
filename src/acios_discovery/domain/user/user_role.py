from enum import StrEnum


class UserRole(StrEnum):
    """
    Access level for a User.

    Deliberately minimal for now: two roles only. ADMIN can
    manage users and view/trigger everything; MEMBER can trigger
    and monitor crawls but not manage other users. A more
    granular permission model (e.g. separate operator/viewer
    roles) can be introduced later without changing this enum's
    existing values.
    """

    ADMIN = "admin"
    MEMBER = "member"
