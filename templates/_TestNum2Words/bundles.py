n2w = features.n2w
OBJECT_ID_PATTERN = r"^\d(\.?\d+)+$"


class Bundle(n2w.Num2WordsBundle):
    apart_no: int = n2w.Num2WordsField(
        "apart_no_words",
        Field(description="Номер апартамента", default=12)
    )
    object_id: str = n2w.Num2WordsField(
        "object_id_words",
        Field(
            description="Идентификатор объекта",
            pattern=OBJECT_ID_PATTERN,
            default="11232.12313.123.1.12"
        )
    )
    area: int | float = n2w.Num2WordsField(
        "area_words",
        Field(description="Площадь объекта", default=45.78),
    )


bundles = [
    Bundle
]
