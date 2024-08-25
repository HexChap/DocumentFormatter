from pydantic import Field

from core.common_bundles.base import BaseBundle


class NamesBundle(BaseBundle):
    f_name: str = Field(description="Имя")
    s_name: str = Field(description="Фамилия")
    patronymic: str = Field(description="Отчество")
