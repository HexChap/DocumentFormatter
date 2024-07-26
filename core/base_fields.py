from abc import ABC, abstractmethod
from copy import deepcopy
from enum import StrEnum
from typing import Annotated, TypedDict, Any, TypeVar

from pydantic import BaseModel, Field, computed_field, create_model
from pydantic.fields import FieldInfo
from pydantic.v1.main import ModelMetaclass

from core.parts import rus_citizen_info_part

DATE_PATTERN = r"^([0-9]{1,2})\.([0-9]{1,2})\.([1-2][0-9]{3})$"
ISSUED_BY_CODE_PATTERN = r"^[0-9]{3}-[0-9]{3}$"

DateField = Annotated[str, Field(pattern=DATE_PATTERN)]


class GenderEnum(StrEnum):
    male = "М"
    female = "Ж"


class Repeated(BaseModel):
    model: type[BaseModel]
    repeat_field_name: str
    result_field_name: str
    min_count: int = 1


def exclude_field(field: FieldInfo, default: Any = None) -> tuple[Any, FieldInfo]:
    new = deepcopy(field)
    new.default = default
    new.exclude = True  # type: ignore
    return new.annotation, new


BaseModelT = TypeVar('BaseModelT', bound=BaseModel)


def make_only_computed_model(model: type[BaseModelT]) -> type[BaseModelT]:
    return create_model(  # type: ignore
        f'OnlyComputed{model.__name__}',
        __base__=model,
        __module__=model.__module__,
        **{
            field_name: exclude_field(field_info)
            for field_name, field_info in model.model_fields.items()
        }
    )


class RepeatableModel(BaseModel, ABC):
    @staticmethod
    @abstractmethod
    def description() -> str:
        pass


class GenderDependantFields(BaseModel):
    gender: GenderEnum = Field(
        description="Пол в формате М/Ж (только буква)",
        exclude=True
    )

    @computed_field
    @property
    def citizen(self) -> str:
        return "гражданин" if self.gender == GenderEnum.male else "гражданка"


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


class RusCitizenInfoFields(
    RepeatableModel,
    PassportFields,
    BirthFields,
    FullnameFields,
    GenderDependantFields,
):
    current_registration_address: str = Field(description="Место текущей прописки")

    @computed_field()
    @property
    def citizen_info(self) -> str:
        return rus_citizen_info_part.format(**self.model_dump(exclude={"citizen_info"}))

    @staticmethod
    def description():
        return "Паспортные данные гражданина РФ"
