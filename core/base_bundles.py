from pydantic import BaseModel, field_validator

from core.tools import Numeric


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
