from pydantic import Field

from core.common_bundles.base import BaseBundle
from core.common_fields import DateField


class BirthBundle(BaseBundle):
    birth_date: DateField = Field(description="Дата рождения")
    birth_location: str = Field(description="Место рождения")
