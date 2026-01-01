from pydantic import BaseModel

# Schema pentru crearea unui utilizator (ce primim de la Frontend)
class UserCreate(BaseModel):
    email: str
    password: str

# Schema pentru afișarea utilizatorului (ce trimitem înapoi - FĂRĂ parolă!)
class UserOut(BaseModel):
    id: int
    email: str

    class Config:
        from_attributes = True

# Schema pentru Token (Ecusonul)
class Token(BaseModel):
    access_token: str
    token_type: str