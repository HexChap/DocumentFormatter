from enum import StrEnum
from typing import Annotated

from pydantic import BaseModel, Field, computed_field

DATE_PATTERN = r"^([0-9]{1,2})\.([0-9]{1,2})\.([1-2][0-9]{3})$"
ISSUED_BY_CODE_PATTERN = r"^[0-9]{3}-[0-9]{3}$"

DateField = Annotated[str, Field(pattern=DATE_PATTERN)]


class GenderEnum(StrEnum):
    male = "М"
    female = "Ж"


class GenderDependantFields(BaseModel):
    gender: GenderEnum = Field(
        description="Пол в формате М/Ж (только буква)",
        exclude=True
    )

    @computed_field
    @property
    def citizen(self) -> str:
        return "гражданин" if self._gender == GenderEnum.male else "гражданка"


class FullnameFields(BaseModel):
    f_name: str = Field(description="Имя")
    s_name: str = Field(description="Фамилия")
    patronymic: str = Field(description="Отчество")


class BirthFields(BaseModel):
    birth_date: DateField = Field(description="Дата рождения в в формате xx.xx.xxxx")
    birth_location: str = Field(description="Место рождения")


class PassportFields(BaseModel):
    passport_no: str = Field(description="Номер (№) пасспорта")
    passport_issued_date: DateField = Field(description="Дата выдачи пасспорта в формате xx.xx.xxxx")
    passport_issued_by_name: str = Field(description="Полное название отделения, без кода")
    passport_issued_by_code: str = Field(
        pattern=ISSUED_BY_CODE_PATTERN,
        description="Код подразделения, в формате xxx-xxx"
    )


class RusCitizenFields(
    FullnameFields, GenderDependantFields,
    BirthFields, PassportFields
):
    current_registration_address: str = Field(description="Место текущей прописки")
