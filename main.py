import os
from pathlib import Path
from importlib import import_module
from typing import Any

from docxtpl import DocxTemplate
from pydantic import BaseModel, ValidationError

FIELD_FILENAME = "fields.py"


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


output_path = Path("output")
resources_path = Path("resources")
resources = [item for item in os.listdir(resources_path) if not item.startswith("_")]

for i, res in enumerate(resources):
    print(f"{i+1}. {res}\n")

res_i = int(input("-> Выберите шаблон: ")) - 1
res_name = resources[res_i]
res_path = Path(resources_path / res_name)
res_fields_path = str(res_path / FIELD_FILENAME.removesuffix(".py")).replace(
    os.sep, ".")

doc = DocxTemplate(res_path / (res_name + ".docx"))
DocFields: BaseModel = import_module(res_fields_path).Fields

fields = list(DocFields.model_fields.items())
values = {}
while fields:
    name, info = fields.pop(0)
    value = input(f"{info.description}, тип {info.annotation.__name__}: ")

    if not validate_field(DocFields, name, value)[1]:
        print("Введеное значение не подходит под поле, проверьте и попробуйте снова.\n")
        fields.insert(0, (name, info))
        continue

    values.update({name: value})

doc.render(values)

doc.save(output_path / (res_name + ".docx"))
