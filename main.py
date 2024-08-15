import asyncio
import os
from datetime import datetime
from pathlib import Path
from typing import Any

from aiohttp import ClientConnectionError
from docx.document import Document
from docxtpl import DocxTemplate
from gh_auto_updater import update
from loguru import logger
from pydantic import BaseModel
from pydantic import ValidationError

from core.base_bundles import Repeatable, Num2Wordable, BaseMarker
from core.config import TEMPLATES_PATH, OUTPUT_PATH, FIELD_FILENAME, FROZEN
from core.tools import generate_num2words

# logger.configure(handlers=[{"sink": sys.stdout, "level": "ERROR"}])

LAST_UPDATE_DATE_PATH = ".ghlastupdate"
if FROZEN:
    LAST_UPDATE_DATE_PATH = Path.cwd() / "_internal" / LAST_UPDATE_DATE_PATH

__version__ = "v1.0.1"


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
    templates = [item for item in os.listdir(TEMPLATES_PATH) if not FROZEN or not item.startswith("_")]
    error_msg = f"Введеное значение должно быть числом от 1 до {len(templates)}"

    for i, tmpl in enumerate(templates):
        print(f"{i + 1}. {tmpl}")

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


# noinspection PyUnresolvedReferences
def get_tmpl_bundles(tmpl_path: Path) -> list[type[BaseModel] | type[BaseMarker]]:
    from core import base_bundles
    from pydantic import BaseModel, Field

    with open(tmpl_path / FIELD_FILENAME, "r", encoding="utf-8") as fp:
        code = fp.read()

    variables = globals()
    variables.update(locals())

    exec(code, variables)

    fields: Any | None = variables.get("fields", None)
    if not fields:
        raise ValueError("Template does not have fields list variable.")

    return fields


def user_select_repeat_count(marker: type[Repeatable]) -> int:
    count = -1
    while count == -1:
        user_in = input(f"Сколько раз ввести {marker.result_field_desc}, минимум {marker.min_count}: ")
        if not user_in.isdigit():
            print("Введите число.\n")
            continue
        user_in = int(user_in)
        if user_in < 0:
            print("Число должно быть положительным.\n")
            continue
        if user_in < marker.min_count:
            print(f"Минимальное число это {marker.min_count}")
            continue
        if user_in > 100:
            choice = input("Вы уверенны? да/нет: ")
            if choice == "нет":
                print("\n")
                continue
            print("Удачи...")
        count = user_in

    return count


def _clean_docx(docx: Document):
    for p in docx.paragraphs:
        tab_stops = p.paragraph_format.tab_stops

        for i in range(len(tab_stops)):
            del tab_stops[i]


def _fill_bundle(bundle: type[BaseModel]) -> dict[str, str]:
    result = {}

    fields = list(bundle.model_fields.items())
    while fields:
        f_name, info = fields.pop(0)
        desc = info.description if info.description else f_name
        exmpl = f" (напр. {info.examples[0]})" if info.examples else ""

        value = input(f"{desc}{exmpl}: ")
        if not validate_field(bundle, f_name, value)[1]:
            print("Введеное значение не подходит под поле, проверьте и попробуйте снова.\n")
            fields.insert(0, (f_name, info))
            continue

        result.update({f_name: value})

    return result


def fill_repeated_bundle(marker: type[Repeatable], repeat_count: int) -> dict[str, list[str]]:
    result = []
    for i in range(repeat_count):
        values = _fill_bundle(marker.model)
        fields = marker.model.model_validate(values).model_dump()

        result.append(
            fields.get(marker.repeat_field_name)
        )

    return {marker.result_field_name: result}


def fill_num2word_bundle(marker: type[Num2Wordable]) -> dict[str, str]:
    result = _fill_bundle(marker.model)
    result.update(
        generate_num2words(payload=result, fields=marker.num2words_fields)
    )

    return result


# noinspection PyTypeChecker
def fill_bundle(bundle: type[BaseModel] | type[BaseMarker]) -> dict[str, str | list[str]]:
    match bundle:
        case Repeatable():
            count = user_select_repeat_count(bundle)
            return fill_repeated_bundle(bundle, count)

        case Num2Wordable():
            return fill_num2word_bundle(bundle)

        case _:
            return _fill_bundle(bundle)


def process_template(tmpl_name: str) -> Path:
    result: dict[str, str | list[str]] = {}
    tmpl_path = Path(TEMPLATES_PATH / tmpl_name)
    tmpl_name = tmpl_name.removeprefix("_")

    doc = DocxTemplate(tmpl_path / (tmpl_name + ".docx"))
    tmpl_bundles = get_tmpl_bundles(tmpl_path)

    for bundle in tmpl_bundles:
        result.update(fill_bundle(bundle))

    OUTPUT_PATH.mkdir(exist_ok=True, parents=True)

    result_path = OUTPUT_PATH / (tmpl_name + f"_{datetime.now().timestamp()}" + ".docx")
    doc.render(result)

    # _clean_docx(doc.docx)
    doc.save(result_path)

    return result_path


async def main():
    try:
        await update(
            repository_name="HexChap/DocumentFormatter",
            current_version=__version__,
            install_dir=Path.cwd(),
            updates_rate_limit_secs=60 * 60,
            last_update_date_path=LAST_UPDATE_DATE_PATH,
            allow_plain=True
        )
    except ClientConnectionError:
        logger.info("No internet connection. Abort update")

    tmpl_name = user_select_tmpl()
    process_template(tmpl_name)


if __name__ == '__main__':
    # print(get_tmpl_bundles(Path(r"D:\.Development\.Projects\HA.Estate\DocumentFormatter\templates\Доверенность")))
    asyncio.run(main())
