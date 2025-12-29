from sqlmodel import SQLModel, create_engine, Session, select
from core.database.models import User

# SQLite file will be created in the data directory
sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

engine = create_engine(sqlite_url)

def create_db_and_tables():
    """Create tables if they don't exist."""
    SQLModel.metadata.create_all(engine)

def get_session():
    """Dependency for getting a DB session."""
    with Session(engine) as session:
        yield session

def initialize_default_user():
    """Ensure at least one user exists for the MVP."""
    with Session(engine) as session:
        result = session.exec(select(User).where(User.username == "Admin"))
        user = result.first()
        if not user:
            user = User(username="Admin", level=1, xp=0)
            session.add(user)
            session.commit()
            session.refresh(user)
            print("👤 Default 'Admin' user created!")
