from pydantic import BaseModel, Field

class AssignmentCreate(BaseModel):
    product_lineup_id: int = Field(gt=0)

class AssignmentAnswer(BaseModel):
    question_id: int = Field(gt=0)
    answer: str = Field(min_length=1, max_length=10000)

class AssignmentSubmit(BaseModel):
    answers: list[AssignmentAnswer] = Field(min_length=1)

class GeneratedQuestion(BaseModel):
    question_number: int = Field(gt=0)
    question: str

class AssignmentQuestionResponse(BaseModel):
    id: int
    question_number: int
    question: str
    answer: str | None = None
    evaluation: str | None = None

class AssignmentSummaryResponse(BaseModel):
    id: int
    product_lineup_id: int
    lineup_identifier: str
    status: str | None

class AssignmentResponse(AssignmentSummaryResponse):
    questions: list[AssignmentQuestionResponse] = Field(default_factory=list)
