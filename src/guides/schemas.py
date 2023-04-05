from pydantic import Field
from datetime import datetime

from core.schemas import BaseModelSchema
from users.schemas import UserReadSchema


class GuideListSingleSchema(BaseModelSchema):
    guide_id: int
    title: str
    last_modified: datetime
    published: bool
    cover_image: str | None
    user: UserReadSchema

    class Config:
        orm_mode = True


class GuideListReadSchema(BaseModelSchema):
    pages: int
    guides: list[GuideListSingleSchema]


class GuideCreateUpdateSchema(BaseModelSchema):
    title: str = Field(max_length=70)
    content: str
    note: str | None
    published: bool = False


class GuideReadSchema(GuideCreateUpdateSchema):
    guide_id: int
    last_modified: datetime
    user: UserReadSchema

    class Config:
        orm_mode = True
