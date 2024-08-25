from pydantic import Field

from core.common_bundles.base import BaseBundle
from core.common_fields import DateField


class BgPermitBundle(BaseBundle):
    egn: str = Field(description="ЕГН", pattern=r"^\d+$")
    permit_no: str = Field(description="Разрешение на долгосрочное пребывание")
    permit_until_date: DateField = Field(description="Срок действия до")
    permit_issued_date: DateField = Field(description="Дата выдачи разрешения")
    permit_issued_city: str = Field(description="Название города выдачи")
