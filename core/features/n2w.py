from types import UnionType
from typing import get_type_hints, Any, get_args, get_origin, Union

from loguru import logger
from num2words import num2words
from pydantic import BaseModel, ValidationError
from pydantic._internal._model_construction import ModelMetaclass
# noinspection PyProtectedMember
from pydantic.fields import FieldInfo, Field
from pydantic_core import PydanticCustomError

from core.common_bundles.base import BaseBundle
from core.tools import Numeric


def get_n2w_from_str(value: str) -> str:
    vals = []
    for val in value.split("."):
        if not val.isdigit():
            raise ValueError(value + " contains symbols beside numbers and periods")
        vals.append(
            num2words(int(val), lang="ru")
        )

    return " точка ".join(vals)


def get_n2w(val: str | Numeric) -> str:
    if isinstance(val, Numeric):
        return num2words(val, lang="ru")
    else:
        return get_n2w_from_str(val)


def validate_n2w_field[T](value: T) -> T:
    """
    Validate n2w source field's type
    Args:
        value: Value to be validated

    Raises:
        ValidationError: if field has unprocessable type

    """
    allowed_types = int | float | str
    if not isinstance(value, allowed_types):
        logger.error(f"unprocessable type {type(value)} for Num2WordsField")
        raise ValueError(f"{type(value)} is not num2wordable, only {allowed_types} are allowed.")

    return value


def Num2WordsField(result_field_name: str, field_info: FieldInfo) -> FieldInfo:
    if not field_info.json_schema_extra:
        field_info.json_schema_extra = {}

    field_info.json_schema_extra.update(
        dict(__n2w_field_name__=result_field_name)
    )

    return field_info


class Num2WordsBundle(BaseBundle, extra="allow"):
    @classmethod
    def validate_n2w_fields(cls):
        allowed_types = int | float | str

        for name, info in cls.model_fields.items():
            err = PydanticCustomError(
                "not_num2wordable",
                "field '{name}' got unprocessable type '{type_}', expected '{allowed}'",
                dict(name=name, type_=info.annotation, allowed=allowed_types)
            )

            if get_origin(info.annotation) in [UnionType, Union]:
                for type_ in get_args(info.annotation):
                    if not issubclass(type_, allowed_types):
                        logger.error(err)
                        raise err
            else:
                if not issubclass(info.annotation, allowed_types):
                    logger.error(err)
                    raise err

    def generate_n2w_fields(self):
        for name, info in self.model_fields.items():
            extra = info.json_schema_extra or {}
            if n2w_name := extra.get("__n2w_field_name__", ""):  # generating num2words if the field is marked
                val = validate_n2w_field(getattr(self, name))
                field = {n2w_name: get_n2w(val)}

                self.__dict__.update(field)
                if not self.__pydantic_root_model__:
                    self.__pydantic_extra__.update(field)

    def model_post_init(self, _):
        self.generate_n2w_fields()

    @classmethod
    def validate_model_schema(cls):
        cls.validate_n2w_fields()


if __name__ == '__main__':
    class Test(Num2WordsBundle):
        test: str = Num2WordsField(
            "test_words",
            Field(default="61056.501.419.3.22")
        )
        test1: list[int] = [123]
        test2: float = 40.23

    Test()
