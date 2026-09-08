from pydantic import BaseModel, Field


class QueryCreate(BaseModel):
    product_id: int = Field(gt=0)
    query: str = Field(min_length=1, max_length=4000)


class QueryResponse(BaseModel):
    id: int
    product_id: int
    query: str
    response: str
