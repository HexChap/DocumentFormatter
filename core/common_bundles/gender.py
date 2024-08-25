from enum import StrEnum

from pydantic import Field, computed_field

from core.common_bundles.base import BaseBundle


class GenderEnum(StrEnum):
    male = "М"
    female = "Ж"


class GenderDependantBundle(BaseBundle):
    gender: GenderEnum = Field(
        description="Пол в формате М/Ж (только буква)",
        exclude=True
    )

    @computed_field
    @property
    def citizen(self) -> str:
        return "гражданин" if self.gender == GenderEnum.male else "гражданка"
