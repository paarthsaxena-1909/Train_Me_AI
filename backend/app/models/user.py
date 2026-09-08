from datetime import datetime

from pydantic import BaseModel, ConfigDict


class UserResponse(BaseModel):
    """API-facing representation corresponding to database.models.User."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    created_at: datetime
