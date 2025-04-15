from pydantic import BaseModel


class ErrorResponse(BaseModel):
    """A data model representing an error response.

    This class extends Pydantic's BaseModel to provide a structured error response format.

    Attributes:
        detail (str): A string containing the error message or description of what went wrong.
    """
    detail: str
