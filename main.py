import asyncio
import os
from datetime import datetime
from pathlib import Path
from types import NoneType, new_class, UnionType
from typing import get_args, get_origin

from aiohttp import ClientConnectionError
from docx.document import Document
from docxtpl import DocxTemplate
from gh_auto_updater import update
from loguru import logger
from polyfactory.factories.pydantic_factory import ModelFactory
from pydantic import BaseModel, ValidationError, Field
from pydantic_core import PydanticUndefined, SchemaValidator

from core import common_bundles, features, common_fields
from core.common_bundles import BgResidentBundle
from core.common_bundles.base import BaseBundle
from core.config import TEMPLATES_PATH, OUTPUT_PATH, BUNDLES_FILENAME, FROZEN, AUTO_FILL


LAST_CHECK_DATE_PATH = ".ghlastupdate"
if FROZEN:
    LAST_CHECK_DATE_PATH = Path.cwd() / "_internal" / LAST_CHECK_DATE_PATH

__version__ = "2.0.0"


def validate_field[T](
    model: type[BaseModel],
    field_name: str,
    value: T
) -> tuple[T | str, bool]:
    try:
        # noinspection PyTypeChecker
        field_validator = SchemaValidator(model.__pydantic_core_schema__["schema"]["fields"][field_name]["schema"])
        value = field_validator.validate_python(value)
    except ValidationError as e:
        return e, False
    else:
        return value, True


def get_template_path(template_dir_path) -> Path:
    tmpl_path = TEMPLATES_PATH / template_dir_path
    templates = [
        filename
        for filename in os.listdir(tmpl_path)
        if filename.endswith(".docx") and not filename.startswith("~$")
    ]

    error_msg = None
    if len(templates) > 1:
        error_msg = "Multiple templates in one directory are not allowed"
    elif len(templates) < 1:
        error_msg = "No template was found in the chosen directory."

    if error_msg:
        logger.critical(error_msg)
        raise ValueError(error_msg)

    return tmpl_path / templates[0]


def user_select_tmpl() -> Path:
    """

    Returns:
        str: A pathlib.Path to the template chosen by user
    """
    template_dirs = [item for item in os.listdir(TEMPLATES_PATH) if not FROZEN or not item.startswith("_")]
    error_msg = f"Введеное значение должно быть числом от 1 до {len(template_dirs)}"

    for i, tmpl in enumerate(template_dirs):
        print(f"{i + 1}. {tmpl}")

    tmpl_i = -1
    while tmpl_i == -1:
        user_in = input("-> Выберите шаблон: ")
        if not user_in.isdigit():
            print(error_msg)
            continue

        user_in = int(user_in) - 1

        if user_in < 0 or user_in >= len(template_dirs):
            print(error_msg)
            continue

        tmpl_i = user_in

    return get_template_path(template_dirs[tmpl_i])


def get_tmpl_bundles(tmpl_path: Path) -> list[type[BaseModel]]:
    env = {
        "features": features,
        "common_bundles": common_bundles,
        "common_fields": common_fields,
        "BaseBundle": BaseBundle,
        "Field": Field,
        **locals()
    }

    with open(tmpl_path / BUNDLES_FILENAME, "r", encoding="utf-8") as fp:
        code = fp.read()

    try:
        exec(code, env)  # it will execute the code and put all the new variables in the env dict
    except Exception as e:
        logger.critical(f"Unprocessable bundles file for template {tmpl_path}")
        raise ValueError(f"Something went wrong in the bundles.py for template in {tmpl_path}") from e

    bundles: list[type[BaseModel]] | None = env.get("bundles", None)
    if not bundles:
        raise ValueError("Template does not have bundles list variable.")

    return bundles


def user_select_repeat_count(desc: str) -> int:
    count = -1
    while count == -1:
        user_in = input(f"Сколько раз ввести {desc}?: ")
        if not user_in.isdigit():
            print("Введите число.\n")
            continue
        user_in = int(user_in)
        if user_in < 0:
            print("Число должно быть положительным.\n")
            continue
        # if user_in < bundle.min_count:
        #     print(f"Минимальное число это {bundle.min_count}")
        #     continue
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


def _fill_bundle[T: BaseModel](bundle: type[T]) -> T:
    result = {}

    if AUTO_FILL:
        factory = new_class(
            bundle.__name__ + "Factory",
            (ModelFactory[bundle],),
            {}
        )
        # noinspection PyUnresolvedReferences
        return factory.build()

    fields = list(bundle.model_fields.items())
    while fields:
        f_name, info = fields.pop(0)
        annotation = info.annotation

        if get_origin(annotation) != UnionType and issubclass(annotation, BaseBundle):
            result.update({f_name: _fill_bundle(info.annotation)})
            continue

        desc = info.description if info.description else f_name
        exmpl = f" (напр. {info.examples[0]})" if info.examples else ""
        default = f" (по умол. {info.default})" if info.default != PydanticUndefined else ""
        is_req = "*" if NoneType not in get_args(annotation) else ""

        value = input(f"{is_req}{desc}{exmpl}{default}: ")

        if value == "":
            value = info.default if default else None

        value, success = validate_field(bundle, f_name, value)
        if not success:
            print("Введеное значение не подходит под поле, проверьте и попробуйте снова.\n")
            fields.insert(0, (f_name, info))
            continue

        result.update({f_name: value})

    return bundle.model_construct(**result)


def fill_repeatable(bundle: type[BaseModel], repeat_count: int) -> dict[str, list[BaseModel]]:
    result = []
    for i in range(repeat_count):
        result.append(_fill_bundle(bundle))

    return {bundle.result_var_name: result}


# noinspection PyTypeChecker
def fill_bundle[T: BaseModel](bundle: type[T]) -> T | dict[str, T]:
    result = None

    if issubclass(bundle, features.repeatable.RepeatableBundle):
        count = user_select_repeat_count(bundle.bundle_desc)
        result = fill_repeatable(bundle, count)

    return result or _fill_bundle(bundle).model_dump()


def process_template(tmpl_path: Path) -> Path:
    result: dict[str, str | list[str]] = {}
    tmpl_path = tmpl_path.parent
    tmpl_name = tmpl_path.name.removeprefix("_")
    result_path = OUTPUT_PATH / (tmpl_name + f"_{datetime.now().timestamp()}" + ".docx")

    doc = DocxTemplate(tmpl_path / (tmpl_name + ".docx"))
    tmpl_bundles = get_tmpl_bundles(tmpl_path)

    print("[!] Поля, помеченные звездочкой, обязательны к заполнению.")
    for bundle in tmpl_bundles:
        result.update(fill_bundle(bundle))

    OUTPUT_PATH.mkdir(exist_ok=True, parents=True)

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
            checks_rate_limit_secs=60 * 60,
            last_check_date_path=LAST_CHECK_DATE_PATH,
            allow_plain=True
        )
    except ClientConnectionError:
        logger.info("No internet connection. Abort update")

    tmpl_name = user_select_tmpl()
    process_template(tmpl_name)


if __name__ == '__main__':
    # print(get_tmpl_bundles(Path(r"D:\.Development\.Projects\HA.Estate\DocumentFormatter\templates\Доверенность")))
    asyncio.run(main())
