from pydantic import Field, computed_field

from core.features import n2w
from core.tools import Numeric

OBJECT_ID_PATTERN = r"^\d(\.?\d+)+$"


class ObjectInfoBundle(n2w.Num2WordsBundle):
    apart_no: int = n2w.Num2WordsField(
        "apart_no_words",
        Field(description="Номер апартамента")
    )
    object_id: str = n2w.Num2WordsField(
        "object_id_words",
        Field(description="Идентификатор объекта", pattern=OBJECT_ID_PATTERN)
    )
    object_address: str = Field(description="Адресс объекта")
    area: Numeric = Field(description="Площадь объекта")
    area_adjacent: Numeric | None = Field(description="Прилежащие части")

    @computed_field
    @property
    def area_total(self) -> Numeric:
        return round(self.area + self.area_adjacent, 2) if self.area_adjacent else None
