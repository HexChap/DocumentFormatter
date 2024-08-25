from enum import StrEnum

from pydantic import Field, computed_field

from core.common_bundles import NamesBundle, BirthBundle
from core.common_bundles.base import BaseBundle
from core.common_bundles.bg_permit import BgPermitBundle
from core.common_bundles.rus_foreign_passport import RusForeignPassportBundle
from core.features.external import ExternalBundle


class CitizenshipEnum(StrEnum):
    ru = "ru"
    bg = "bg"


citizenship_map = {
    CitizenshipEnum.ru: "Российская Федерация",
    CitizenshipEnum.bg: "Республика Болгария"
}


class BgResidentBundle(
    NamesBundle,
    BirthBundle,
    BgPermitBundle,
):
    citizenship: CitizenshipEnum = Field(description="Гражданство (ru/bg)")
    registration_address: str = Field(description="Постоянны адрес")

    rus: RusForeignPassportBundle

    @computed_field
    @property
    def citizenship_words(self) -> str:
        return citizenship_map[self.citizenship]
