# models.py - Модели базы данных
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, Text, ForeignKey
from typing import Optional

class Base(DeclarativeBase):
    """Базовый класс для всех моделей"""
    pass

class User(Base):
    """Модель пользователя"""
    __tablename__ = 'users'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    telegram_id: Mapped[int] = mapped_column(Integer, unique=True, nullable=False, index=True)
    username: Mapped[Optional[str]] = mapped_column(String(255))
    
    # Связь с избранными книгами
    favorite_books = relationship("FavoriteBook", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User(telegram_id={self.telegram_id}, username='{self.username}')>"

class Book(Base):
    """Модель книги"""
    __tablename__ = 'books'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(500), nullable=False, index=True)
    author: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    year: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    genre: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    subgenre: Mapped[Optional[str]] = mapped_column(String(100), index=True)
    
    # Связь с избранными книгами
    favorite_by_users = relationship("FavoriteBook", back_populates="book", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Book(title='{self.title}', author='{self.author}', year={self.year})>"

class FavoriteBook(Base):
    """Связь пользователя с избранными книгами"""
    __tablename__ = 'favorite_books'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'), nullable=False)
    book_id: Mapped[int] = mapped_column(Integer, ForeignKey('books.id'), nullable=False)
    
    # Связи
    user = relationship("User", back_populates="favorite_books")
    book = relationship("Book", back_populates="favorite_by_users")
    
    def __repr__(self):
        return f"<FavoriteBook(user_id={self.user_id}, book_id={self.book_id})>"