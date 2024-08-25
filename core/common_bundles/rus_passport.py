from pydantic import Field

from core.common_bundles.base import BaseBundle
from core.common_fields import DateField

ISSUED_BY_CODE_PATTERN = r"^\d{3}-\d{3}$"


class PassportBundle(BaseBundle):
    passport_no: str = Field(description="Номер (№) пасспорта")
    passport_issued_date: DateField = Field(description="Дата выдачи пасспорта")
    passport_issued_by_name: str = Field(description="Полное название отделения, без кода")
    passport_issued_by_code: str = Field(
        pattern=ISSUED_BY_CODE_PATTERN,
        description="Код подразделения",
        examples=["500-127"]
    )
