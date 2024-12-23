from pydantic import BaseModel


class CustomBaseModel(BaseModel):
    """Custom base model that ignores extra fields."""

    class Config:
        extra = "ignore"
