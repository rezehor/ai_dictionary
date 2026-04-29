from pydantic import BaseModel, ConfigDict, Field
from uuid import UUID
from datetime import datetime



class WordLLMResponse(BaseModel):
    """Schema used to enforce the OpenAI Structured Output."""
    word: str = Field(..., description="The word exactly as requested by the user")
    transcription: str = Field(..., description="The US transcription of the word, e.g., ɪnˈvɑːlv")
    short_description: str = Field(..., description="Short description using easy words to understand the new word (maximum 15 words)")
    sentences: list[str] = Field(..., description="3 short and useful sentences with the new word that Americans use often", min_length=3, max_length=3)


class WordBase(BaseModel):
    word: str
    transcription: str
    short_description: str
    sentences: list[str]


class WordCreate(WordBase):
    pass


class WordUpdate(BaseModel):
    word: str | None = None
    transcription: str | None = None
    short_description: str | None = None
    sentences: list[str] | None = None


class WordRead(WordBase):
    id: UUID
    user_id: UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserRead(BaseModel):
    id: UUID
    email: str
    full_name: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
