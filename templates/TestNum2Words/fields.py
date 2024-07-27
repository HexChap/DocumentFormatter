from pydantic import BaseModel, Field

from core.base_bundles import Repeatable, Num2Wordable


class _Bundle(BaseModel):
    words1: str = Field(description="Тест")
    words2: str = Field(description="Тест")
    words3: str = Field(description="Тест")


fields = [
    Num2Wordable(
        model=_Bundle,
        num2words_fields={
            ("words1", "words11"),
            ("words2", "words21"),
            ("words3", "words31")
        }
    )
]
