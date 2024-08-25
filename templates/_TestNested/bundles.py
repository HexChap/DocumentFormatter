n2w = features.n2w


class Bundle(features.repeatable.RepeatableBundle, n2w.Num2WordsBundle):
    result_var_name = "test_data"
    bundle_desc = "Проверка"

    test: int | float | str = n2w.Num2WordsField(
        "test_words",
        Field(description="Целое, дробное или идентификатор", default=45.78),
    )


bundles = [
    Bundle
]
