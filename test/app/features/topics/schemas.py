from sqlmodel import SQLModel
from pydantic import BaseModel

class TopicCreation(BaseModel):
    nom: str

class TopicResponse(BaseModel):
    id: str

    nom: str
