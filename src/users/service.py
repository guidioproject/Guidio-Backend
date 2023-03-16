from sqlalchemy.orm import Session

from auth.service import get_password_hash
from core.models import User, UserDetail, Profession
from users.schemas import UserProfileUpdateSchema, UserPasswordUpdateSchema


def get_professions_by_name(db: Session, name: str) -> list[Profession]:
    professions = db.query(Profession).filter(Profession.name.ilike(f'%{name}%')).all()
    return professions


def get_user_profile_by_id(user_id: int, db: Session) -> tuple[User, UserDetail] | None:
    user = db.query(User).get(user_id)
    user_details = db.query(UserDetail).filter(UserDetail.user_id == user.user_id).first()
    return user, user_details


def update_user_profile(data: UserProfileUpdateSchema,
                        db: Session, db_user: User) -> tuple[User, UserDetail]:
    db_user.email = data.email
    db_user.first_name = data.first_name
    db_user.last_name = data.last_name
    user_detail: UserDetail = db.query(UserDetail)\
        .filter(UserDetail.user_id == db_user.user_id).first()
    if user_detail:
        user_detail.bio = data.bio
        user_detail.profession_id = data.profession_id
    else:
        new_user_detail = UserDetail(user_id=db_user.user_id,
                                     bio=data.bio,
                                     profession_id=data.profession_id)
        db.add(new_user_detail)
    db.commit()
    db.refresh(db_user)
    db.refresh(user_detail)
    return db_user, user_detail


def delete_user_profile(db: Session, user_id: int) -> None:
    user: User = db.query(User).get(user_id)
    db.delete(user)
    db.commit()
    return None


def update_user_password(db: Session,
                         data: UserPasswordUpdateSchema,
                         user: User) -> tuple[User, UserDetail]:
    hashed_password = get_password_hash(data.password)
    user.password = hashed_password
    db.commit()
    db.refresh(user)
    user_details = db.query(UserDetail).filter(UserDetail.user_id == user.user_id).first()
    return user, user_details
