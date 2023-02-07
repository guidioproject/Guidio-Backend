from pydantic import EmailStr

from core.schemas import BaseModelSchema


class UserBaseSchema(BaseModelSchema):
    email: EmailStr
    first_name: str
    last_name: str


class UserUpdateSchema(BaseModelSchema):
    first_name: str
    last_name: str

    class Config:
        schema_extra = {
            "example": {
                "first_name": "John",
                "last_name": "Brown",
            }
        }


class UserReadSchema(UserBaseSchema):
    user_id: int
    is_active: bool

    class Config:
        orm_mode = True