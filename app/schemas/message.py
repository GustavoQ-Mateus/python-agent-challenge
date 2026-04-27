from pydantic import BaseModel,ConfigDict,Field,field_validator

class messageRequest(BaseModel):
    message: str = Field(..., min_length=1)
    session_id: str | None = Field(default=None,min_length=1,max_length=128)
    @Field_validator("message")
    def validate_message(cls, value: str) -> str:
        message = value.strip()
        if not message:
            raise ValueError("message must not be empty")
        return message
    @Field_validator("session_id")
    @classmethod
    def validate_session_id(cls, value: str | None) -> str | None:
        if value is None:
            return None
        session_id = value.strip()
        if not session_id:
            raise ValueError("session_id must not be empty")
        return session_id

class Source(BaseModel):
    section: str
    model_config = ConfigDict(extra="forbid")

class MessageResponse(BaseModel):
    answer: str
    sources: list[Source]
    model_config = ConfigDict(extra="forbid")