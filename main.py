import os
from datetime import datetime
from pathlib import Path
from importlib import import_module
from typing import Any

from docxtpl import DocxTemplate
from pydantic import BaseModel, ValidationError

from config import resources_path, output_path, FIELD_FILENAME


def validate_field(
    model: BaseModel,
    field_name: str,
    value: Any
) -> tuple[str, bool]:
    try:
        model.__pydantic_validator__.validate_assignment(
            model.model_construct(),
            field_name,
            value
        )
    except ValidationError as e:
        return e, False
    else:
        return "", True


def user_select_res() -> str:
    resources = [item for item in os.listdir(resources_path) if not item.startswith("_")]
    error_msg = f"Введеное значение должно быть числом от 0 до {len(resources)}"

    for i, res in enumerate(resources):
        print(f"{i + 1}. {res}\n")

    res_i = -1
    while res_i == -1:
        user_in = input("-> Выберите шаблон: ")
        if not user_in.isdigit():
            print(error_msg)
            continue

        user_in = int(user_in) - 1

        if user_in < 0 or user_in >= len(resources):
            print(error_msg)
            continue

        res_i = user_in

    return resources[res_i]


def fill_resource(res_name: str):
    res_path = Path(resources_path / res_name)
    res_fields_path = str(
        res_path / FIELD_FILENAME.removesuffix(".py")
    ).replace(os.sep, ".")

    doc = DocxTemplate(res_path / (res_name + ".docx"))
    doc_fields: BaseModel = import_module(res_fields_path).Fields

    fields = list(doc_fields.model_fields.items())
    values = {}
    while fields:
        f_name, info = fields.pop(0)
        value = input(f"{info.description}, тип {info.annotation.__name__}: ")

        if not validate_field(doc_fields, f_name, value)[1]:
            print("Введеное значение не подходит под поле, проверьте и попробуйте снова.\n")
            fields.insert(0, (f_name, info))
            continue

        values.update({f_name: value})

    model = doc_fields.model_validate(values)
    doc.render(model.model_dump())

    doc.save(output_path / (res_name + f"_{datetime.now().timestamp()}" + ".docx"))


def main():
    res_name = user_select_res()
    fill_resource(res_name)


if __name__ == '__main__':
    main()
