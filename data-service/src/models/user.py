from pydantic import BaseModel


class UserData(BaseModel):
    is_login: bool
    is_admin: bool
    is_error: bool
