from pydantic import BaseModel


class TokenData(BaseModel):
    firebase_token: str
