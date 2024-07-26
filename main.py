import os
from datetime import datetime
from pathlib import Path
from importlib import import_module
from types import GenericAlias
from typing import Any, TypeAlias, get_args

from docxtpl import DocxTemplate
from pydantic import BaseModel, ValidationError

from core.base_fields import Repeated
from core.config import templates_path, output_path, FIELD_FILENAME

TemplateFieldsList: TypeAlias = list[type[BaseModel] | Repeated]


def validate_field(
    model: type[BaseModel],
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


def user_select_tmpl() -> str:
    templates = [item for item in os.listdir(templates_path) if not item.startswith("_")]
    error_msg = f"Введеное значение должно быть числом от 0 до {len(templates)}"

    for i, tmpl in enumerate(templates):
        print(f"{i + 1}. {tmpl}\n")

    tmpl_i = -1
    while tmpl_i == -1:
        user_in = input("-> Выберите шаблон: ")
        if not user_in.isdigit():
            print(error_msg)
            continue

        user_in = int(user_in) - 1

        if user_in < 0 or user_in >= len(templates):
            print(error_msg)
            continue

        tmpl_i = user_in

    return templates[tmpl_i]


def user_select_count_for(model: type[BaseModel], min_count: int = 0) -> int:
    description = model.description() if hasattr(model, "description") else model.__name__

    count = -1
    while count == -1:
        user_in = input(f"Сколько раз ввести {description}, минимум {min_count}: ")
        if not user_in.isdigit():
            print("Введите число.\n")
            continue
        user_in = int(user_in)
        if user_in < 0:
            print("Число должно быть положительным.\n")
            continue
        if user_in < min_count:
            print(f"Минимальное число это {min_count}")
            continue
        if user_in > 100:
            choice = input("Вы уверенны? да/нет: ")
            if choice == "нет":
                print("\n")
                continue
            print("Удачи...")
        count = user_in

    return count


def user_fill_fields(model: type[BaseModel]) -> dict[str, str]:
    result = {}

    fields = list(model.model_fields.items())
    while fields:
        f_name, info = fields.pop(0)
        desc = info.description if info.description else f_name
        value = input(f"{desc}: ")

        if not validate_field(model, f_name, value)[1]:
            print("Введеное значение не подходит под поле, проверьте и попробуйте снова.\n")
            fields.insert(0, (f_name, info))
            continue

        result.update({f_name: value})

    return result


def get_tmpl_fields(tmpl_path: Path) -> TemplateFieldsList:
    tmpl_fields_path = str(
        tmpl_path / FIELD_FILENAME.removesuffix(".py")
    ).replace(os.sep, ".")

    return import_module(tmpl_fields_path).fields


def process_tmpl_fields(
    fields_to_process: list[type[BaseModel]],
    repeated_fields: list[tuple[Repeated, int]]
):
    result: dict[str, str | list[str]] = {}
    for fields_model in fields_to_process:
        result.update(user_fill_fields(fields_model))

    for repeated, count in repeated_fields:
        fields_model = repeated.model
        filled = []
        for i in range(count):
            values = user_fill_fields(fields_model)
            validated = fields_model.model_validate(values)
            filled.append(validated.model_dump().get(repeated.repeat_field_name))

        result.update({repeated.result_field_name: filled})

    return result


def fill_template(tmpl_name: str):
    tmpl_path = Path(templates_path / tmpl_name)

    doc = DocxTemplate(tmpl_path / (tmpl_name + ".docx"))
    tmpl_fields = get_tmpl_fields(tmpl_path)

    expected_field_names = []
    fields_to_process: list[type[BaseModel]] = []
    repeated_fields: list[tuple[Repeated, int]] = []
    for fields in tmpl_fields:
        if isinstance(fields, Repeated):  # check if Repeated
            fields_model = fields.model
            count = user_select_count_for(fields_model, min_count=fields.min_count)
            repeated_fields.append((fields, count))
            expected_field_names.append(fields.result_field_name)
        else:
            fields_to_process.append(fields)
            expected_field_names.extend(fields.model_fields.keys())

    result = process_tmpl_fields(fields_to_process, repeated_fields)
    result = {k: v for k, v in result.items() if k in expected_field_names}  # omit

    doc.render(result)
    doc.save(output_path / (tmpl_name + f"_{datetime.now().timestamp()}" + ".docx"))


def main():
    tmpl_name = user_select_tmpl()
    fill_template(tmpl_name)


if __name__ == '__main__':
    main()
