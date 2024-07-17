from langchain_core.pydantic_v1 import BaseModel
from typing import List, Optional
from enum import Enum

class SourceTypes(Enum):
    code = "code"
    repository = "repository"
    documentation = "documentation"
    clarification = "clarification"

class InquiryFields(BaseModel):
    source: SourceTypes
    inquiry: str
    files: Optional[List[str]] = None