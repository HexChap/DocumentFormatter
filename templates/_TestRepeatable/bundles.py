class Bundle(features.repeatable.RepeatableBundle):
    result_var_name = "tests"
    bundle_desc = "Проверка"

    testing: str = Field(description="Тест", default="Тестировка")


bundles = [
    Bundle
]
