# Models

Use Pydantic models in `backend/app/models` for API input and output contracts.
Keep them strongly typed and separate from SQLAlchemy schema models.

Use `ConfigDict(from_attributes=True)` when a response model may be created
from an object or row-shaped result. Validate request data at the controller
boundary and return explicit response models from services.

Database structure belongs to typed SQLAlchemy models in
`backend/database/models`; do not use Pydantic models as migration metadata.
