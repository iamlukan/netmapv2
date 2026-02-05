from sqlalchemy.orm import Session
from app.models.user import User

class UserRepository:
    @staticmethod
    def get_by_username(db: Session, username: str):
        return db.query(User).filter(User.username == username).first()

    @staticmethod
    def create_user(db: Session, user: User):
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def get_all(db: Session):
        return db.query(User).all()
