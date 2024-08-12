from typing import Annotated

from pydantic import BaseModel, Field, computed_field, field_validator

from core.parts import rus_citizen_info_part
from core.tools import GenderEnum, Numeric

DATE_PATTERN = r"^([0-9]{1,2})\.([0-9]{1,2})\.([1-2][0-9]{3})$"
ISSUED_BY_CODE_PATTERN = r"^[0-9]{3}-[0-9]{3}$"

DATE_EXAMPLE = "12.08.2024"

DateField = Annotated[str, Field(pattern=DATE_PATTERN, examples=[DATE_EXAMPLE])]


class BaseMarker(BaseModel):
    """ A base class for creating processing-time markers

    Attributes:
        model: model to mark
    """
    model: type[BaseModel]


class Repeatable(BaseMarker):
    """ Mark bundle as repeatable.

    Attributes:
        repeat_field_name: the name of field that will be repeated
        result_field_name: the name under which the repeated data will be stored
        result_field_desc: description of the result field for user
        min_count: minimal repeat count
    """
    repeat_field_name: str
    result_field_name: str
    result_field_desc: str
    min_count: int = 1


class Num2Wordable(BaseMarker):
    """ Mark bundle for num2words processing

    Attributes:
        num2words_fields: a set of tuples, each containing the name of a field and
            the result name after being converted by num2words
    """
    num2words_fields: set[tuple[str, str]]

    @classmethod
    @field_validator("num2words_fields")
    def fields_numeric_or_str(cls, v: set[tuple[str, str]]):
        for f_name, res_f_name in v:
            f_info = cls.model_fields.get(f_name)

            if not isinstance(f_info.annotation, (Numeric, str)):
                raise ValueError("Must be int, float or str")

        return v


class GenderDependantBundle(BaseModel):
    gender: GenderEnum = Field(
        description="Пол в формате М/Ж (только буква)",
        exclude=True
    )

    @computed_field
    @property
    def citizen(self) -> str:
        return "гражданин" if self.gender == GenderEnum.male else "гражданка"


class NamesBundle(BaseModel):
    f_name: str = Field(description="Имя")
    s_name: str = Field(description="Фамилия")
    patronymic: str = Field(description="Отчество")


class BirthBundle(BaseModel):
    birth_date: DateField = Field(description="Дата рождения")
    birth_location: str = Field(description="Место рождения")


class PassportBundle(BaseModel):
    passport_no: str = Field(description="Номер (№) пасспорта")
    passport_issued_date: DateField = Field(description="Дата выдачи пасспорта")
    passport_issued_by_name: str = Field(description="Полное название отделения, без кода")
    passport_issued_by_code: str = Field(
        pattern=ISSUED_BY_CODE_PATTERN,
        description="Код подразделения",
        examples=["500-127"]
    )


class RusCitizenInfoBundle(
    PassportBundle,
    BirthBundle,
    NamesBundle,
    GenderDependantBundle,
):
    current_registration_address: str = Field(description="Место текущей прописки")

    @computed_field()
    @property
    def citizen_info(self) -> str:
        return rus_citizen_info_part.format(**self.model_dump(exclude={"citizen_info"}))


class ObjectInfoBundle(BaseModel):
    apart_no: int = Field(description="Номер апартамента")
    object_id: str = Field(description="Идентификатор объекта")
    object_address: str = Field(description="Адресс объекта")
    area: Numeric = Field(description="Площадь объекта")
    area_adjacent: Numeric = Field(description="Прилежащие части")


RepeatableRusCitizenInfoBundle = Repeatable(
    model=RusCitizenInfoBundle,
    repeat_field_name="citizen_info",
    result_field_name="citizen_infos",
    result_field_desc="Паспортные данные гражданина РФ"
)

Num2WordedObjectInfoBundle = Num2Wordable(
    model=ObjectInfoBundle,
    num2words_fields={
        ("apart_no", "apart_no_words"),
        ("object_id", "object_id_words")
    }
)
