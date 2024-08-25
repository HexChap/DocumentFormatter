from pydantic import Field

from core.common_bundles.base import BaseBundle
from core.common_fields import DateField


class RusForeignPassportBundle(BaseBundle):
    f_passport_type: str = Field(description="Тип загранпас.")
    f_passport_no: str = Field(description="Номер загранпас.")
    f_passport_issued_date: DateField = Field(description="Дата выдачи загранпас.")
    f_passport_issued_by: str = Field(description="Название отделения выдачи загранпас.")
    f_passport_until_date: DateField = Field(description="Срок действия загранпас. до")
