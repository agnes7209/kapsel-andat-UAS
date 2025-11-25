import argparse
import getpass

from sqlalchemy.orm import Session

from .database import Base, SessionLocal, engine
from .models import User, UserRole
from .security import get_password_hash


def create_admin(email: str, full_name: str, password: str, session: Session) -> User:
    existing = session.query(User).filter(User.email == email).first()
    if existing:
        raise ValueError("Admin with this email already exists")
    admin = User(
        email=email,
        full_name=full_name,
        hashed_password=get_password_hash(password),
        role=UserRole.ADMIN,
    )
    session.add(admin)
    session.commit()
    session.refresh(admin)
    return admin


def main() -> None:
    parser = argparse.ArgumentParser(description="Initialize database and create admin user")
    parser.add_argument("--email", required=True, help="Admin email")
    parser.add_argument("--name", required=True, help="Admin full name")
    parser.add_argument("--password", help="Admin password (prompt if omitted)")
    args = parser.parse_args()

    password = args.password or getpass.getpass("Password: ")

    Base.metadata.create_all(bind=engine)
    session = SessionLocal()
    try:
        admin = create_admin(args.email, args.name, password, session)
        print(f"Admin created with id={admin.id} and email={admin.email}")
    finally:
        session.close()


if __name__ == "__main__":
    main()
