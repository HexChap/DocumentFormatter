from pydantic import BaseModel


class BaseBundle(BaseModel):
    @classmethod
    def validate_model_schema(cls):
        pass
