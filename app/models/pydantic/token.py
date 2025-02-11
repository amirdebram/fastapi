from pydantic import BaseModel
from typing import Union

class Token(BaseModel):  
  access_token: str | None = None  
  refresh_token: str | None = None
  token_type: str

class TokenData(BaseModel):
    username: Union[str, None] = None