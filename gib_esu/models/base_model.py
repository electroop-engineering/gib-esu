from pydantic import BaseModel, ConfigDict


class CustomBaseModel(BaseModel):
    """Custom base model that ignores extra fields."""

    model_config = ConfigDict(extra="ignore")
