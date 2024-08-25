from typing import TypedDict, Annotated

from pydantic import Field


DATE_PATTERN = r"^([0-9]{1,2})\.([0-9]{1,2})\.([1-2][0-9]{3})$"
DATE_EXAMPLE = "12.08.2024"
DateField = Annotated[str, Field(pattern=DATE_PATTERN, examples=[DATE_EXAMPLE])]
