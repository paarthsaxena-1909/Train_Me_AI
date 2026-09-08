from pydantic import BaseModel, Field

class VariantCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    specs: str = Field(min_length=1)

class ProductCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    description: str | None = None
    variant: VariantCreate

class VariantResponse(VariantCreate):
    id: int
    
class ProductResponse(BaseModel):
    id: int
    name: str
    description: str | None
    variants: list[VariantResponse] = []
