from typing import ClassVar

from pydantic import Field, computed_field

from .rus_passport import PassportBundle
from .gender import GenderDependantBundle
from .names import NamesBundle
from .birth import BirthBundle
from .. import features
from ..features.repeatable import RepeatableBundle


class RusCitizenInfoBundle(
    RepeatableBundle,
    PassportBundle,
    BirthBundle,
    NamesBundle,
    GenderDependantBundle,
):
    result_var_name = "citizen_datas"
    bundle_desc = "Пасспортные данные гражданина/нки РФ"

    current_registration_address: str = Field(description="Место текущей прописки")
