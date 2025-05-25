# keyboards.py - Модуль клавиатур
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

def get_main_keyboard(is_admin: bool = False) -> ReplyKeyboardMarkup:
    """Основная клавиатура пользователя"""
    buttons = [
        [KeyboardButton(text="👤 Мой профиль")],
        [KeyboardButton(text="📖 Жанры"), KeyboardButton(text="🔍 Поиск книг")]
    ]
    
    if is_admin:
        buttons.append([KeyboardButton(text="⚙️ Админ панель")])
    
    return ReplyKeyboardMarkup(
        keyboard=buttons,
        resize_keyboard=True,
        one_time_keyboard=False
    )

def get_genres_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура выбора жанров"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📚 Литература", callback_data="genre_Литература_0")],
        [InlineKeyboardButton(text="💻 Тех литература", callback_data="genre_Тех литература_0")]
    ])

def get_admin_keyboard() -> ReplyKeyboardMarkup:
    """Клавиатура админ панели"""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="➕ Добавить книгу")],
            [KeyboardButton(text="✏️ Редактировать книги")],
            [KeyboardButton(text="📊 Статистика")],
            [KeyboardButton(text="🔙 Главное меню")]
        ],
        resize_keyboard=True,
        one_time_keyboard=False
    )

def get_book_action_keyboard(book_id: int, is_favorite: bool = False) -> InlineKeyboardMarkup:
    """Клавиатура действий с книгой"""
    favorite_text = "💔 Удалить из избранного" if is_favorite else "❤️ Добавить в избранное"
    
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=favorite_text, callback_data=f"toggle_favorite_{book_id}")],
        [InlineKeyboardButton(text="📖 Подробнее", callback_data=f"book_details_{book_id}")]
    ])

def get_profile_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура профиля пользователя"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Добавить в избранное", callback_data="add_favorite")],
        [InlineKeyboardButton(text="➖ Удалить из избранного", callback_data="remove_favorite")],
        [InlineKeyboardButton(text="🔄 Обновить рекомендации", callback_data="refresh_recommendations")]
    ])

def get_pagination_keyboard(genre: str, current_page: int, total_pages: int) -> InlineKeyboardMarkup:
    """Клавиатура пагинации для списка книг"""
    buttons = []
    
    # Кнопки навигации
    nav_buttons = []
    if current_page > 0:
        nav_buttons.append(InlineKeyboardButton(text="⬅️ Назад", callback_data=f"genre_{genre}_{current_page-1}"))
    if current_page < total_pages - 1:
        nav_buttons.append(InlineKeyboardButton(text="➡️ Далее", callback_data=f"genre_{genre}_{current_page+1}"))
    
    if nav_buttons:
        buttons.append(nav_buttons)
    
    # Кнопка возврата к жанрам
    buttons.append([InlineKeyboardButton(text="🔙 К жанрам", callback_data="back_to_genres")])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_edit_book_keyboard(book_id: int) -> InlineKeyboardMarkup:
    """Клавиатура редактирования книги"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📝 Название", callback_data=f"edit_field_{book_id}_title")],
        [InlineKeyboardButton(text="👤 Автора", callback_data=f"edit_field_{book_id}_author")],
        [InlineKeyboardButton(text="📅 Год", callback_data=f"edit_field_{book_id}_year")],
        [InlineKeyboardButton(text="📖 Описание", callback_data=f"edit_field_{book_id}_description")],
        [InlineKeyboardButton(text="🏷️ Жанр", callback_data=f"edit_field_{book_id}_genre")],
        [InlineKeyboardButton(text="🗑️ Удалить книгу", callback_data=f"delete_book_{book_id}")],
        [InlineKeyboardButton(text="🔙 К списку книг", callback_data="back_to_edit_list")]
    ])

def get_confirm_delete_keyboard(book_id: int) -> InlineKeyboardMarkup:
    """Клавиатура подтверждения удаления"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Да, удалить", callback_data=f"confirm_delete_{book_id}")],
        [InlineKeyboardButton(text="❌ Отмена", callback_data=f"edit_book_{book_id}")]
    ])

def get_genre_selection_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура выбора жанра при добавлении книги"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📚 Литература", callback_data="admin_genre_Литература")],
        [InlineKeyboardButton(text="💻 Тех литература", callback_data="admin_genre_Тех литература")]
    ])

def get_literature_subgenres_keyboard() -> InlineKeyboardMarkup:
    """Поджанры литературы"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📖 Художественная", callback_data="admin_subgenre_Художественная")],
        [InlineKeyboardButton(text="📚 Классическая", callback_data="admin_subgenre_Классическая")],
        [InlineKeyboardButton(text="🕵️ Детектив", callback_data="admin_subgenre_Детектив")],
        [InlineKeyboardButton(text="💝 Роман", callback_data="admin_subgenre_Роман")],
        [InlineKeyboardButton(text="🚀 Фантастика", callback_data="admin_subgenre_Фантастика")],
        [InlineKeyboardButton(text="🎭 Драма", callback_data="admin_subgenre_Драма")],
        [InlineKeyboardButton(text="⏭️ Пропустить", callback_data="admin_subgenre_")]
    ])

def get_technical_subgenres_keyboard() -> InlineKeyboardMarkup:
    """Поджанры технической литературы"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💻 Программирование", callback_data="admin_subgenre_Программирование")],
        [InlineKeyboardButton(text="🔧 Инженерия", callback_data="admin_subgenre_Инженерия")],
        [InlineKeyboardButton(text="🔬 Наука", callback_data="admin_subgenre_Наука")],
        [InlineKeyboardButton(text="🏗️ Архитектура", callback_data="admin_subgenre_Архитектура")],
        [InlineKeyboardButton(text="📊 Экономика", callback_data="admin_subgenre_Экономика")],
        [InlineKeyboardButton(text="🏥 Медицина", callback_data="admin_subgenre_Медицина")],
        [InlineKeyboardButton(text="⏭️ Пропустить", callback_data="admin_subgenre_")]
    ])

def get_favorites_management_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура управления избранным"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📚 Показать по жанрам", callback_data="show_favorites_by_genre")],
        [InlineKeyboardButton(text="🗑️ Очистить избранное", callback_data="clear_favorites")],
        [InlineKeyboardButton(text="🔄 Обновить рекомендации", callback_data="refresh_recommendations")]
    ])