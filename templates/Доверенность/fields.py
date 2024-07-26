from random import randint

from pydantic import BaseModel, Field, computed_field

from core.base_fields import RusCitizenInfoFields, Repeated, RepeatableModel


class _Fields(BaseModel):
    pass


fields = [
    _Fields,
    Repeated(
        model=RusCitizenInfoFields,
        repeat_field_name="citizen_info",
        result_field_name="citizen_infos"
    ),
]
