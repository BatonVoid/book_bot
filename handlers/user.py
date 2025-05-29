# handlers/user.py - Обработчики для обычных пользователей
from aiogram import F, Router
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext

from database.database import DatabaseManager
from keyboards import get_main_keyboard, get_genres_keyboard
from utils import is_admin, format_book_info, format_books_list
from states import SearchStates

router = Router()
db = DatabaseManager()

@router.message(Command("start"))
async def start_command(message: Message):
    """Стартовая команда"""
    user_id = message.from_user.id
    username = message.from_user.username or "Неизвестно"
    
    # Регистрируем пользователя в БД
    await db.add_user(user_id, username)
    
    welcome_text = f"Добро пожаловать, {message.from_user.first_name}! 📚\n\n"
    welcome_text += "Это бот для управления библиотекой книг.\n"
    welcome_text += "Выберите действие из меню ниже:"
    
    await message.answer(welcome_text, reply_markup=get_main_keyboard(is_admin(user_id)))

@router.message(F.text == "👤 Мой профиль")
async def my_profile(message: Message):
    """Показ профиля пользователя"""
    user_id = message.from_user.id
    favorite_books = await db.get_user_favorite_books(user_id)
    
    if not favorite_books:
        profile_text = "📚 Ваш профиль:\n\n❤️ Любимые книги: пусто\n\n"
        profile_text += "Добавьте книги в избранное, чтобы получать персональные рекомендации!"
    else:
        profile_text = "📚 Ваш профиль:\n\n❤️ Любимые книги:\n"
        for book in favorite_books:
            profile_text += f"• {book['title']} - {book['author']} ({book['year']})\n"
        
        # Получаем рекомендации
        recommendations = await db.get_recommendations_for_user(user_id)
        if recommendations:
            profile_text += "\n💡 Рекомендации для вас:\n"
            for rec in recommendations[:3]:  # Показываем топ-3 рекомендации
                profile_text += f"• {rec['title']} - {rec['author']}\n"
    
    # Добавляем кнопки управления избранным
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Добавить в избранное", callback_data="add_favorite")],
        [InlineKeyboardButton(text="➖ Удалить из избранного", callback_data="remove_favorite")]
    ])
    
    await message.answer(profile_text, reply_markup=keyboard)

@router.message(F.text == "📖 Жанры")
async def show_genres(message: Message):
    """Показ жанров"""
    await message.answer("Выберите жанр:", reply_markup=get_genres_keyboard())

@router.callback_query(F.data.startswith("genre_"))
async def handle_genre_selection(callback: CallbackQuery):
    """Обработка выбора жанра"""
    genre = callback.data.split("_")[1]
    page = int(callback.data.split("_")[2]) if len(callback.data.split("_")) > 2 else 0
    
    books = await db.get_books_by_genre(genre, limit=5, offset=page*5)
    total_books = await db.get_books_count_by_genre(genre)
    
    if not books:
        await callback.message.edit_text("В этом жанре пока нет книг 😔")
        return
    
    text = f"📚 Книги жанра '{genre}':\n\n"
    keyboard_buttons = []
    
    for book in books:
        text += format_book_info(book, show_description=False) + "\n\n"
        
        # Кнопка для каждой книги
        keyboard_buttons.append([
            InlineKeyboardButton(
                text=f"📖 {book['title']}", 
                callback_data=f"book_action_{book['id']}"
            )
        ])
    
    # Кнопки навигации
    nav_buttons = []
    if page > 0:
        nav_buttons.append(InlineKeyboardButton(text="⬅️ Назад", callback_data=f"genre_{genre}_{page-1}"))
    if (page + 1) * 5 < total_books:
        nav_buttons.append(InlineKeyboardButton(text="➡️ Далее", callback_data=f"genre_{genre}_{page+1}"))
    
    if nav_buttons:
        keyboard_buttons.append(nav_buttons)
    
    keyboard_buttons.append([InlineKeyboardButton(text="🔙 К жанрам", callback_data="back_to_genres")])
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
    await callback.message.edit_text(text, reply_markup=keyboard)

@router.callback_query(F.data == "back_to_genres")
async def back_to_genres(callback: CallbackQuery):
    """Возврат к жанрам"""
    await callback.message.edit_text("Выберите жанр:", reply_markup=get_genres_keyboard())

@router.callback_query(F.data.startswith("book_action_"))
async def handle_book_action(callback: CallbackQuery):
    """Действия с книгой"""
    book_id = int(callback.data.split("_")[2])
    user_id = callback.from_user.id
    
    book = await db.get_book_by_id(book_id)
    is_favorite = await db.is_book_in_favorites(user_id, book_id)
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="💔 Удалить из избранного" if is_favorite else "❤️ Добавить в избранное",
            callback_data=f"toggle_favorite_{book_id}"
        )],
        [InlineKeyboardButton(text="🔙 Назад", callback_data=f"genre_{book['genre']}_0")]
    ])
    
    text = format_book_info(book, show_description=True)
    
    await callback.message.edit_text(text, reply_markup=keyboard)

@router.callback_query(F.data.startswith("toggle_favorite_"))
async def toggle_favorite(callback: CallbackQuery):
    """Переключение избранного"""
    book_id = int(callback.data.split("_")[2])
    user_id = callback.from_user.id
    
    is_favorite = await db.is_book_in_favorites(user_id, book_id)
    
    if is_favorite:
        await db.remove_from_favorites(user_id, book_id)
        await callback.answer("Книга удалена из избранного ❌")
    else:
        await db.add_to_favorites(user_id, book_id)
        await callback.answer("Книга добавлена в избранное ❤️")
    
    # Обновляем кнопки
    book = await db.get_book_by_id(book_id)
    is_favorite = not is_favorite  # Инвертируем состояние
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="💔 Удалить из избранного" if is_favorite else "❤️ Добавить в избранное",
            callback_data=f"toggle_favorite_{book_id}"
        )],
        [InlineKeyboardButton(text="🔙 Назад", callback_data=f"genre_{book['genre']}_0")]
    ])
    
    await callback.message.edit_reply_markup(reply_markup=keyboard)

@router.message(F.text == "🔍 Поиск книг")
async def search_books_start(message: Message, state: FSMContext):
    """Начало поиска книг"""
    await message.answer("Введите название книги для поиска:")
    await state.set_state(SearchStates.waiting_for_search_query)

@router.message(StateFilter(SearchStates.waiting_for_search_query))
async def search_books_process(message: Message, state: FSMContext):
    """Обработка поиска книг"""
    query = message.text.strip()
    books = await db.search_books_by_title(query)
    
    if not books:
        await message.answer("Книги не найдены 😔\nПопробуйте изменить запрос.")
    else:
        text = f"🔍 Результаты поиска для '{query}':\n\n"
        keyboard_buttons = []
        
        for book in books[:10]:  # Показываем максимум 10 результатов
            text += f"📖 {book['title']} - {book['author']} ({book['year']})\n"
            keyboard_buttons.append([
                InlineKeyboardButton(
                    text=f"📖 {book['title']}", 
                    callback_data=f"book_action_{book['id']}"
                )
            ])
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
        await message.answer(text, reply_markup=keyboard)
    
    await state.clear()

@router.callback_query(F.data == "add_favorite")
async def add_favorite_from_profile(callback: CallbackQuery):
    """Добавление в избранное из профиля"""
    books = await db.get_all_books(limit=10)
    
    if not books:
        await callback.message.edit_text("В базе данных пока нет книг.")
        return
    
    keyboard_buttons = []
    text = "Выберите книгу для добавления в избранное:\n\n"
    
    for book in books:
        text += f"📖 {book['title']} - {book['author']}\n"
        keyboard_buttons.append([
            InlineKeyboardButton(
                text=f"➕ {book['title']}", 
                callback_data=f"add_to_fav_{book['id']}"
            )
        ])
    
    keyboard_buttons.append([InlineKeyboardButton(text="🔙 К профилю", callback_data="back_to_profile")])
    keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
    await callback.message.edit_text(text, reply_markup=keyboard)

@router.callback_query(F.data.startswith("add_to_fav_"))
async def add_to_favorites_process(callback: CallbackQuery):
    """Обработка добавления в избранное"""
    book_id = int(callback.data.split("_")[3])
    user_id = callback.from_user.id
    
    success = await db.add_to_favorites(user_id, book_id)
    
    if success:
        await callback.answer("Книга добавлена в избранное ❤️")
    else:
        await callback.answer("Книга уже в избранном или произошла ошибка ❌")

@router.callback_query(F.data == "remove_favorite")
async def remove_favorite_from_profile(callback: CallbackQuery):
    """Удаление из избранного из профиля"""
    user_id = callback.from_user.id
    favorite_books = await db.get_user_favorite_books(user_id)
    
    if not favorite_books:
        await callback.message.edit_text("У вас нет любимых книг.")
        return
    
    keyboard_buttons = []
    text = "Выберите книгу для удаления из избранного:\n\n"
    
    for book in favorite_books:
        text += f"📖 {book['title']} - {book['author']}\n"
        keyboard_buttons.append([
            InlineKeyboardButton(
                text=f"➖ {book['title']}", 
                callback_data=f"remove_from_fav_{book['id']}"
            )
        ])
    
    keyboard_buttons.append([InlineKeyboardButton(text="🔙 К профилю", callback_data="back_to_profile")])
    keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
    await callback.message.edit_text(text, reply_markup=keyboard)

@router.callback_query(F.data.startswith("remove_from_fav_"))
async def remove_from_favorites_process(callback: CallbackQuery):
    """Обработка удаления из избранного"""
    book_id = int(callback.data.split("_")[3])
    user_id = callback.from_user.id
    
    success = await db.remove_from_favorites(user_id, book_id)
    
    if success:
        await callback.answer("Книга удалена из избранного 💔")
    else:
        await callback.answer("Произошла ошибка при удалении ❌")

@router.callback_query(F.data == "back_to_profile")
async def back_to_profile(callback: CallbackQuery):
    """Возврат к профилю"""
    await my_profile(callback.message)

@router.message(F.text == "🔙 Главное меню")
async def main_menu(message: Message):
    """Главное меню"""
    welcome_text = f"Главное меню 📚\n\n"
    welcome_text += "Выберите действие:"
    
    await message.answer(welcome_text, reply_markup=get_main_keyboard(is_admin(message.from_user.id)))