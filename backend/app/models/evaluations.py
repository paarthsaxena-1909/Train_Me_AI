"""API contracts for the stateless avatar-evaluation prototype."""

from pydantic import BaseModel, Field


class EvaluationMessageRequest(BaseModel):
    message: str = Field(min_length=1, max_length=2_000)


class EvaluationMessageResponse(BaseModel):
    response_text: str


class AvatarSessionResponse(BaseModel):
    session_token: str
    session_id: str
    api_url: str

