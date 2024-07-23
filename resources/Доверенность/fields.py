from pydantic import BaseModel, Field


class Fields(BaseModel):
    f_name: str = Field(description="Имя доверяющего")
    s_name: str = Field(description="Фамилия доверяющего")
    patronymic: str = Field(description="Отчество доверяющего")
    birth_date: str = Field(
        description="Дата рождения доверяющего в формате xx.xx.xxxx",
        pattern=r"^([0-9]{1,2})\.([0-9]{1,2})\.([1-2][0-9]{3})$",
    )
