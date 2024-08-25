from typing import ClassVar

from core.common_bundles.base import BaseBundle


class RepeatableBundle(BaseBundle):
    result_var_name: ClassVar
    bundle_desc: ClassVar
