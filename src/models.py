from datetime import datetime
from typing import List, Optional
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import String, ForeignKey, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship


db = SQLAlchemy()


# --- TABLA USERS ---
class User(db.Model):
    __tablename__ = "user"
    id: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    user_name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(255), nullable=False)

    # Relaciones simples (Uno a Muchos)
    posts: Mapped[List["Post"]] = relationship(back_populates="author")
    comments: Mapped[List["Comment"]] = relationship(back_populates="author")  

    # Relaciones complejas
    # 1. Seguidores: 
    following: Mapped[List["Follower"]] = relationship(
        foreign_keys="[Follower.user_id]", back_populates="follower_user"
    )
    followers: Mapped[List["Follower"]] = relationship(
        foreign_keys="[Follower.following_id]", back_populates="followed_user"
    )

    # 2. Shares (Compartidos):
    shares_sent: Mapped[List["Share"]] = relationship(
        foreign_keys="[Share.sender_id]", back_populates="sender"
    )
    shares_received: Mapped[List["Share"]] = relationship(
        foreign_keys="[Share.receiver_id]", back_populates="receiver"
    )

    def serialize(self):
        return {
            "id": self.id,
            "user_name": self.user_name,
            "email": self.email
        }

# --- TABLA FOLLOWERS ---
class Follower(db.Model):
    __tablename__ = "follower"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)       # Quien sigue
    following_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)  # A quien siguen

    # Relaciones inversas hacia User
    follower_user: Mapped["User"] = relationship(
        foreign_keys=[user_id], back_populates="following"
    )
    followed_user: Mapped["User"] = relationship(
        foreign_keys=[following_id], back_populates="followers"
    )

# --- TABLA POSTS ---
class Post(db.Model):
    __tablename__ = "post"
    id: Mapped[int] = mapped_column(primary_key=True)
    publicacion: Mapped[str] = mapped_column(String(255), nullable=False)
    descripcion: Mapped[Optional[str]] = mapped_column(Text)
    fecha: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)

    # Relaciones
    author: Mapped["User"] = relationship(back_populates="posts")
    comments: Mapped[List["Comment"]] = relationship(back_populates="post")
    shares: Mapped[List["Share"]] = relationship(back_populates="post") # Un post puede ser compartido muchas veces

# --- TABLA SHARES ---
class Share(db.Model):
    __tablename__ = "share"
    id: Mapped[int] = mapped_column(primary_key=True)
    sender_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)    # Quien envía
    receiver_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)  # Quien recibe
    post_id: Mapped[int] = mapped_column(ForeignKey("post.id"), nullable=False)      # Qué post se comparte
    fecha: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relaciones
    sender: Mapped["User"] = relationship(
        foreign_keys=[sender_id], back_populates="shares_sent"
    )
    receiver: Mapped["User"] = relationship(
        foreign_keys=[receiver_id], back_populates="shares_received"
    )
    post: Mapped["Post"] = relationship(back_populates="shares")

# --- TABLA COMMENTS ---
class Comment(db.Model):
    __tablename__ = "comment"
    id: Mapped[int] = mapped_column(primary_key=True)
    texto: Mapped[str] = mapped_column(Text, nullable=False)
    fecha: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)
    post_id: Mapped[int] = mapped_column(ForeignKey("post.id"), nullable=False)

    # Relaciones
    author: Mapped["User"] = relationship(back_populates="comments")
    post: Mapped["Post"] = relationship(back_populates="comments")

