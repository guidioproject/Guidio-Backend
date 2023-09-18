from sqlalchemy import asc, desc, func
from sqlalchemy.orm import Session, Query

from core.models import Guide, User, Profession, UserDetail
from guides.constants import RetrieveOrder
from guides.schemas import GuideCreateUpdateSchema


def count_pages(db: Session, page_size: int):
    count_of_guides: int = db.query(Guide.guide_id) \
        .order_by(desc(Guide.last_modified)).count()
    division: tuple[int, int] = divmod(count_of_guides, page_size)
    pages: int = division[0] + 1 if division[1] else division[0]
    return pages


def count_published_guides_pages(db: Session, page_size: int):
    count_of_guides: int = db.query(Guide.guide_id).filter(Guide.published) \
        .order_by(desc(Guide.last_modified)).count()
    division: tuple[int, int] = divmod(count_of_guides, page_size)
    pages: int = division[0] + 1 if division[1] else division[0]
    return pages


def get_initial_list_of_guides(db: Session,
                               search: str = '') -> Query | None:
    guides = db.query(
        Guide.guide_id,
        Guide.title,
        Guide.cover_image,
        UserDetail.avatar,
        User.user_id,
        Profession.name.label('profession')) \
        .filter(Guide.user_id == User.user_id, User.user_id == UserDetail.user_id,
                UserDetail.profession_id == Profession.profession_id,
                func.coalesce(Guide.title, '').ilike(f"%{search}%"),
                )
    return guides


def get_list_of_guides(db: Session,
                       page: int,
                       page_size: int,
                       sort_order: str = RetrieveOrder.descending,
                       search: str = '',
                       published_only: bool = True) -> list | None:
    offset: int = page * page_size

    if sort_order == RetrieveOrder.descending:
        order_by_clause = desc(Guide.last_modified)
    else:
        order_by_clause = asc(Guide.last_modified)

    query = get_initial_list_of_guides(db, search=search)

    if published_only:
        guides = query.filter(Guide.published) \
            .order_by(order_by_clause).offset(offset).limit(page_size).all()
    else:
        guides = query.order_by(order_by_clause).offset(offset).limit(page_size).all()

    return guides


def search_guides(db: Session, title: str, page: int, page_size: int) -> list | None:
    guides: list = get_list_of_guides(db, page=page, page_size=page_size, search=title)
    return guides


def get_guides_by_user_id(db: Session,
                          user_id: int,
                          page: int,
                          page_size: int,
                          user: User) -> list | None:
    if user.user_id == user_id:
        guides = get_list_of_guides(db, page=page, page_size=page_size, published_only=False)
    else:
        guides = get_list_of_guides(db, page=page, page_size=page_size, published_only=True)
    return guides


def get_guide_by_id(db: Session, guide_id: int, user: User) -> Guide | None:
    guide: Guide = db.query(Guide).get(guide_id)
    if not guide:
        return None
    if not guide.user_id == user.user_id and not guide.published:
        return None
    return guide


def save_guide(db: Session,
               data: GuideCreateUpdateSchema,
               user_id: int,
               guide=None) -> Guide:
    if not guide:
        guide = Guide()
    guide.title = data.title
    guide.content = data.content
    guide.note = data.note
    guide.published = data.published
    guide.user_id = user_id
    db.add(guide)
    db.commit()
    db.refresh(guide)
    return guide


def delete_guide(db: Session, guide_id: int) -> None:
    guide = db.query(Guide).get(guide_id)
    db.delete(guide)
    db.commit()
    return None
