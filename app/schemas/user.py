from pydantic import BaseModel, EmailStr


# base property shared by models
class UserBase(BaseModel):
    email: EmailStr
    username: str

class UserCreate(UserBase):
    password: str


class UserResponse(UserBase):
    id: int
    is_active: bool

    class config:
        # tell pydantic to read data even if it is ORM object
        from_attributes = True


# for login token
class Token(BaseModel):
    access_token: str
    token_type: str
