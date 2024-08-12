from pydantic import BaseModel, Field

from core.base_bundles import Repeatable


class _Bundle(BaseModel):
    testing: str = Field(description="Тест")


fields = [
    Repeatable(
        model=_Bundle,
        repeat_field_name="testing",
        result_field_name="test",
        result_field_desc="Потенциально множественный ввод",
        min_count=2
    )
]
