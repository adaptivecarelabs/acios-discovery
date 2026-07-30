from pydantic import BaseModel

from .context import DiscoveryContext
from .models import RawDiscovery


class DiscoveryRecord(BaseModel):
    """
    Combines the discovered company
    with the metadata describing
    where it came from.
    """

    context: DiscoveryContext

    company: RawDiscovery
