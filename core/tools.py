from collections import defaultdict
from enum import StrEnum
from typing import TypeAlias

from num2words import num2words
from pydantic import BaseModel

Numeric: TypeAlias = int | float


class GenderEnum(StrEnum):
    male = "М"
    female = "Ж"


def _check_num_to_wordable(dump: dict, fields) -> dict[str, Numeric | list[int]]:
    result = dict()
    for f_name, res_name in fields:
        value: str | Numeric = dump.get(f_name)

        if isinstance(value, Numeric):
            result.update({res_name: value})
            continue

        value = value.strip()

        if value.isdigit():
            result.update({res_name: int(value)})
            continue

        try:
            value = float(value)
        except ValueError:
            pass
        else:
            result.update({res_name: value})
            continue

        vals = []
        for val in value.split("."):
            if not val.isdigit():
                raise ValueError(value + " contains symbols beside numbers and periods")
            vals.append(int(val))
        result.update({res_name: vals})

    return result


def generate_num2words(payload: dict[str, str], fields: set[tuple[str, str]]) -> dict[str, str]:
    """
    Generate num to words for the specified fields

    :param payload: instance of pydantic.BaseModel
    :param fields: list of tuple of field_name and result_name
    """
    result = defaultdict()
    to_process = _check_num_to_wordable(payload, fields)

    for f_name, value in to_process.items():
        if isinstance(value, list):
            result[f_name] = num2words(value[0], lang="ru") + " точка "
            for num in value[1:]:
                result[f_name] += num2words(num, lang="ru") + " точка "
            result[f_name] = result[f_name].removesuffix(" точка ")
        else:
            result[f_name] = num2words(value, lang="ru")

    return result


class Test(BaseModel):
    test: str = "61056.501.419.3.22"
    test1: int = 123
    test2: float = 40.23
