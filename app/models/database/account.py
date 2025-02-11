from typing import List
from app.dependencies.__database__ import Base, Column, Mapped,Table, mapped_column, relationship, ForeignKey, Boolean

################################################################
##              Client / User Structure / Tables              ##
################################################################
class Users(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(unique=True, index=True, nullable=False)
    first_name: Mapped[str] = mapped_column(nullable=False)
    last_name: Mapped[str] = mapped_column(nullable=False)
    email: Mapped[str] = mapped_column(unique=True, index=True, nullable=True)
    hashed_password: Mapped[str] = mapped_column(nullable=False)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    
    public_ips: Mapped[List["PublicIP"]] = relationship("PublicIP", secondary="link_user_ips", back_populates="users")

# Junction table for many-to-many relationship between Users and PublicIP
link_user_ips = Table(
    "link_user_ips",
    Base.metadata,
    Column("user_id", ForeignKey("users.id"), primary_key=True),
    Column("public_ip_id", ForeignKey("public_ips.id"), primary_key=True)
)

class PublicIP(Base):
    __tablename__ = 'public_ips'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    ip_address: Mapped[str] = mapped_column(nullable=False)

    users: Mapped[List["Users"]] = relationship("Users", secondary="link_user_ips", back_populates="public_ips")
