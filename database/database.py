# database/database.py - Исправленный менеджер базы данных
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy import select, func, and_, or_
from typing import List, Dict, Any, Optional
import logging

from .models import Base, User, Book, FavoriteBook
from config import Config

logger = logging.getLogger(__name__)

class DatabaseManager:
    """Менеджер для работы с базой данных"""
    
    def __init__(self, database_url: str = None):
        self.database_url = database_url or Config.DATABASE_URL
        self.engine = create_async_engine(self.database_url, echo=False)
        self.session_maker = async_sessionmaker(self.engine, expire_on_commit=False)
    
    # ИСПРАВЛЕНИЕ: Убираем async из get_session
    def get_session(self) -> AsyncSession:
        """Получение сессии базы данных"""
        return self.session_maker()
    
    async def init_db(self):
        """Инициализация базы данных"""
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("База данных инициализирована")
    
    # =============== МЕТОДЫ ДЛЯ РАБОТЫ С ПОЛЬЗОВАТЕЛЯМИ ===============
    
    async def add_user(self, telegram_id: int, username: str = None) -> User:
        """Добавление или обновление пользователя"""
        async with self.get_session() as session:
            # Проверяем, существует ли пользователь
            result = await session.execute(
                select(User).where(User.telegram_id == telegram_id)
            )
            existing_user = result.scalar_one_or_none()
            
            if existing_user:
                # Обновляем username если изменился
                if existing_user.username != username:
                    existing_user.username = username
                    await session.commit()
                return existing_user
            
            # Создаем нового пользователя
            user = User(telegram_id=telegram_id, username=username)
            session.add(user)
            await session.commit()
            await session.refresh(user)
            logger.info(f"Добавлен новый пользователь: {telegram_id}")
            return user
    
    async def get_user_by_telegram_id(self, telegram_id: int) -> Optional[User]:
        """Получение пользователя по Telegram ID"""
        async with self.get_session() as session:
            result = await session.execute(
                select(User).where(User.telegram_id == telegram_id)
            )
            return result.scalar_one_or_none()
    
    async def get_all_users(self) -> List[Dict[str, Any]]:
        """Получение всех пользователей"""
        async with self.get_session() as session:
            result = await session.execute(select(User))
            users = result.scalars().all()
            
            return [
                {
                    'id': user.id,
                    'telegram_id': user.telegram_id,
                    'username': user.username
                }
                for user in users
            ]
    
    # =============== МЕТОДЫ ДЛЯ РАБОТЫ С КНИГАМИ ===============
    
    async def add_book(self, title: str, author: str, year: int, description: str, 
                  genre: str, subgenre: str = None, file_id: str = None, 
                  file_name: str = None, file_size: int = None, file_type: str = None) -> int:

        async with self.get_session() as session:
            book = Book(
                title=title,
                author=author,
                year=year,
                description=description,
                genre=genre,
                subgenre=subgenre,
                file_id=file_id,
                file_name=file_name,
                file_size=file_size,
                file_type=file_type
            )
            session.add(book)
            await session.commit()
            await session.refresh(book)
            logger.info(f"Добавлена книга: {title} - {author}" + 
                    (f" с файлом {file_name}" if file_id else ""))
            return book.id

    async def get_book_by_id(self, book_id: int) -> Optional[Dict[str, Any]]:
        """Получение книги по ID с информацией о файле"""
        async with self.get_session() as session:
            result = await session.execute(
                select(Book).where(Book.id == book_id)
            )
            book = result.scalar_one_or_none()
            
            if book:
                return {
                    'id': book.id,
                    'title': book.title,
                    'author': book.author,
                    'year': book.year,
                    'description': book.description,
                    'genre': book.genre,
                    'subgenre': book.subgenre,
                    'file_id': book.file_id,
                    'file_name': book.file_name,
                    'file_size': book.file_size,
                    'file_type': book.file_type
                }
            return None
    
    async def get_all_books(self, limit: int = None, offset: int = 0) -> List[Dict[str, Any]]:
        """Получение всех книг"""
        async with self.get_session() as session:
            query = select(Book).offset(offset).order_by(Book.id.desc())
            if limit:
                query = query.limit(limit)
            
            result = await session.execute(query)
            books = result.scalars().all()
            
            return [
                {
                    'id': book.id,
                    'title': book.title,
                    'author': book.author,
                    'year': book.year,
                    'description': book.description,
                    'genre': book.genre,
                    'subgenre': book.subgenre
                }
                for book in books
            ]
    
    async def get_books_by_genre(self, genre: str, limit: int = 5, offset: int = 0) -> List[Dict[str, Any]]:
        """Получение книг по жанру"""
        async with self.get_session() as session:
            result = await session.execute(
                select(Book)
                .where(Book.genre == genre)
                .offset(offset)
                .limit(limit)
                .order_by(Book.year.desc())
            )
            books = result.scalars().all()
            
            return [
                {
                    'id': book.id,
                    'title': book.title,
                    'author': book.author,
                    'year': book.year,
                    'description': book.description,
                    'genre': book.genre,
                    'subgenre': book.subgenre
                }
                for book in books
            ]
    
    async def get_books_count_by_genre(self, genre: str) -> int:
        """Подсчет книг по жанру"""
        async with self.get_session() as session:
            result = await session.execute(
                select(func.count(Book.id)).where(Book.genre == genre)
            )
            return result.scalar()
    
    async def search_books_by_title(self, query: str) -> List[Dict[str, Any]]:
        """Поиск книг по названию и автору"""
        async with self.get_session() as session:
            result = await session.execute(
                select(Book)
                .where(or_(
                    Book.title.ilike(f'%{query}%'),
                    Book.author.ilike(f'%{query}%')
                ))
                .order_by(Book.year.desc())
                .limit(20)
            )
            books = result.scalars().all()
            
            return [
                {
                    'id': book.id,
                    'title': book.title,
                    'author': book.author,
                    'year': book.year,
                    'description': book.description,
                    'genre': book.genre,
                    'subgenre': book.subgenre
                }
                for book in books
            ]
    
    async def update_book_field(self, book_id: int, field: str, value: Any) -> bool:
        """Обновление поля книги"""
        async with self.get_session() as session:
            result = await session.execute(
                select(Book).where(Book.id == book_id)
            )
            book = result.scalar_one_or_none()
            
            if book:
                setattr(book, field, value)
                await session.commit()
                logger.info(f"Обновлено поле {field} книги ID {book_id}")
                return True
            return False
    
    async def delete_book(self, book_id: int) -> bool:
        """Удаление книги"""
        async with self.get_session() as session:
            result = await session.execute(
                select(Book).where(Book.id == book_id)
            )
            book = result.scalar_one_or_none()
            
            if book:
                await session.delete(book)
                await session.commit()
                logger.info(f"Удалена книга ID {book_id}")
                return True
            return False
    
    # =============== МЕТОДЫ ДЛЯ РАБОТЫ С ИЗБРАННЫМ ===============
    
    async def add_to_favorites(self, telegram_id: int, book_id: int) -> bool:
        """Добавление книги в избранное"""
        async with self.get_session() as session:
            # Получаем пользователя
            user_result = await session.execute(
                select(User).where(User.telegram_id == telegram_id)
            )
            user = user_result.scalar_one_or_none()
            
            if not user:
                return False
            
            # Проверяем, нет ли уже в избранном
            existing_result = await session.execute(
                select(FavoriteBook).where(
                    and_(FavoriteBook.user_id == user.id, FavoriteBook.book_id == book_id)
                )
            )
            existing = existing_result.scalar_one_or_none()
            
            if existing:
                return False  # Уже в избранном
            
            # Добавляем в избранное
            favorite = FavoriteBook(user_id=user.id, book_id=book_id)
            session.add(favorite)
            await session.commit()
            logger.info(f"Пользователь {telegram_id} добавил книгу {book_id} в избранное")
            return True
    
    async def remove_from_favorites(self, telegram_id: int, book_id: int) -> bool:
        """Удаление книги из избранного"""
        async with self.get_session() as session:
            # Получаем пользователя
            user_result = await session.execute(
                select(User).where(User.telegram_id == telegram_id)
            )
            user = user_result.scalar_one_or_none()
            
            if not user:
                return False
            
            # Находим запись в избранном
            favorite_result = await session.execute(
                select(FavoriteBook).where(
                    and_(FavoriteBook.user_id == user.id, FavoriteBook.book_id == book_id)
                )
            )
            favorite = favorite_result.scalar_one_or_none()
            
            if favorite:
                await session.delete(favorite)
                await session.commit()
                logger.info(f"Пользователь {telegram_id} удалил книгу {book_id} из избранного")
                return True
            return False
    
    async def is_book_in_favorites(self, telegram_id: int, book_id: int) -> bool:
        """Проверка, находится ли книга в избранном"""
        async with self.get_session() as session:
            # Получаем пользователя
            user_result = await session.execute(
                select(User).where(User.telegram_id == telegram_id)
            )
            user = user_result.scalar_one_or_none()
            
            if not user:
                return False
            
            # Проверяем наличие в избранном
            result = await session.execute(
                select(FavoriteBook).where(
                    and_(FavoriteBook.user_id == user.id, FavoriteBook.book_id == book_id)
                )
            )
            return result.scalar_one_or_none() is not None
    
    async def get_user_favorite_books(self, telegram_id: int) -> List[Dict[str, Any]]:
        """Получение избранных книг пользователя"""
        async with self.get_session() as session:
            # Получаем пользователя
            user_result = await session.execute(
                select(User).where(User.telegram_id == telegram_id)
            )
            user = user_result.scalar_one_or_none()
            
            if not user:
                return []
            
            # Получаем избранные книги
            result = await session.execute(
                select(Book)
                .join(FavoriteBook, Book.id == FavoriteBook.book_id)
                .where(FavoriteBook.user_id == user.id)
                .order_by(Book.title)
            )
            books = result.scalars().all()
            
            return [
                {
                    'id': book.id,
                    'title': book.title,
                    'author': book.author,
                    'year': book.year,
                    'description': book.description,
                    'genre': book.genre,
                    'subgenre': book.subgenre
                }
                for book in books
            ]
    
    async def get_recommendations_for_user(self, telegram_id: int) -> List[Dict[str, Any]]:
        """Получение рекомендаций на основе жанров любимых книг"""
        async with self.get_session() as session:
            # Получаем пользователя
            user_result = await session.execute(
                select(User).where(User.telegram_id == telegram_id)
            )
            user = user_result.scalar_one_or_none()
            
            if not user:
                return []
            
            # Получаем жанры любимых книг
            favorite_genres_result = await session.execute(
                select(Book.genre, Book.subgenre)
                .join(FavoriteBook, Book.id == FavoriteBook.book_id)
                .where(FavoriteBook.user_id == user.id)
                .distinct()
            )
            favorite_genres = favorite_genres_result.all()
            
            if not favorite_genres:
                return []
            
            # Получаем ID любимых книг чтобы исключить их из рекомендаций
            favorite_books_result = await session.execute(
                select(FavoriteBook.book_id).where(FavoriteBook.user_id == user.id)
            )
            favorite_book_ids = [row[0] for row in favorite_books_result.all()]
            
            # Строим условия для поиска рекомендаций
            genre_conditions = []
            for genre, subgenre in favorite_genres:
                if subgenre:
                    genre_conditions.append(
                        and_(Book.genre == genre, Book.subgenre == subgenre)
                    )
                else:
                    genre_conditions.append(Book.genre == genre)
            
            # Ищем книги похожих жанров, исключая уже любимые
            if favorite_book_ids:
                query = select(Book).where(
                    and_(
                        or_(*genre_conditions),
                        ~Book.id.in_(favorite_book_ids)  # Исключаем любимые книги
                    )
                ).order_by(Book.year.desc()).limit(5)
            else:
                query = select(Book).where(
                    or_(*genre_conditions)
                ).order_by(Book.year.desc()).limit(5)
            
            result = await session.execute(query)
            books = result.scalars().all()
            
            return [
                {
                    'id': book.id,
                    'title': book.title,
                    'author': book.author,
                    'year': book.year,
                    'description': book.description,
                    'genre': book.genre,
                    'subgenre': book.subgenre
                }
                for book in books
            ]