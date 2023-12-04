from datetime import datetime

from pydantic import Field

from core.schemas import BaseModelSchema
from users.schemas import UserReadSchema, UserListReadSchema


class GuideCoverImageSchema(BaseModelSchema):
    cover_image: str | None

    class Config:
        from_attributes = True


class GuideListSingleSchema(BaseModelSchema):
    guide_id: int
    title: str
    published: bool
    created_at: datetime
    last_modified: datetime
    cover_image: str | None
    user: UserListReadSchema

    class Config:
        from_attributes = True


class GuideListReadSchema(BaseModelSchema):
    pages: int
    guides: list[GuideListSingleSchema]


class GuideCreateUpdateSchema(BaseModelSchema):
    title: str = Field(min_length=1, max_length=70)
    content: str
    note: str | None
    published: bool


class GuideReadSchema(GuideCreateUpdateSchema):
    guide_id: int
    created_at: datetime
    last_modified: datetime
    cover_image: str | None
    user: UserReadSchema

    class Config:
        from_attributes = True
