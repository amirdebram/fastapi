from datetime import datetime
from passlib.context import CryptContext

from sqlalchemy import func, create_engine, delete, insert, or_, select
from sqlalchemy import Table, Column, ForeignKey, JSON, String, Boolean, Integer
from sqlalchemy.exc import IntegrityError, OperationalError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, DeclarativeMeta, Mapped, aliased, joinedload, mapped_column, relationship

from app.dependencies.__config__ import settings

# Database URL from environment, expecting PostgreSQL
DATABASE_URL = settings.database_url

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class Base(DeclarativeBase):
    """Base class for all ORM models."""
    __abstract__ = True  # Ensure this base class does not create a table
    created_at: Mapped[datetime] = mapped_column(default=func.now())
    updated_at: Mapped[datetime] = mapped_column(default=func.now(), onupdate=func.now())

# Synchronous engine for schema creation (for migration tools like Alembic)
connect_args = {"check_same_thread": False}
sync_engine = create_engine(DATABASE_URL, connect_args=connect_args)

# Asynchronous engine for normal operation
async_engine = create_async_engine(DATABASE_URL)

# Asynchronous session maker
AsyncSessionLocal = async_sessionmaker(
    autoflush=False,
    autocommit=False,
    bind=async_engine,
    class_=AsyncSession
)

async def get_db():
    """Dependency that provides a database session and handles transaction lifecycle."""
    async with AsyncSessionLocal() as db:
        try:
            yield db
        except SQLAlchemyError:
            await db.rollback()
            raise
        finally:
            await db.close()

class DatabaseManager:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_admin_user(self):
        """Get or create a user."""
        from app.models.database.account import Users
        query = await self.session.execute(select(Users).filter_by(username=settings.admin_username))
        user = query.scalars().first()

        if not user:
            user = Users(
                username=settings.admin_username,
                first_name=settings.admin_firstname,
                last_name=settings.admin_lastname,
                email=settings.admin_email,
                hashed_password=bcrypt_context.hash(settings.admin_password),
                is_admin=True,
                is_active=True
            )
            self.session.add(user)
            await self.session.commit()

async def create_database():
    """Creates database schema and initializes admin user."""
    try:
        async with async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    except OperationalError as e:
        raise RuntimeError("Database initialization failed") from e
    except Exception as e:
        raise RuntimeError("Unexpected error during database initialization") from e
    finally:
        async with AsyncSessionLocal() as session:
            db_manager = DatabaseManager(session)
            await db_manager.create_admin_user()