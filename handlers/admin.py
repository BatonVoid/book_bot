# handlers/admin.py - Обработчики для администраторов
from aiogram import F, Router
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext

from database import DatabaseManager
from keyboards import get_admin_keyboard, get_main_keyboard
from utils import is_admin, format_book_info
from states import AdminStates

router = Router()
db = DatabaseManager()

@router.message(F.text == "⚙️ Админ панель")
async def admin_panel(message: Message):
    """Админ панель"""
    if not is_admin(message.from_user.id):
        await message.answer("У вас нет доступа к админ панели ❌")
        return
    
    await message.answer("Админ панель:", reply_markup=get_admin_keyboard())

@router.message(F.text == "➕ Добавить книгу")
async def add_book_start(message: Message, state: FSMContext):
    """Начало добавления книги"""
    if not is_admin(message.from_user.id):
        await message.answer("У вас нет прав для добавления книг ❌")
        return
    
    await message.answer("Введите название книги:")
    await state.set_state(AdminStates.waiting_for_title)

@router.message(StateFilter(AdminStates.waiting_for_title))
async def add_book_title(message: Message, state: FSMContext):
    """Ввод названия книги"""
    await state.update_data(title=message.text.strip())
    await message.answer("Введите год издания:")
    await state.set_state(AdminStates.waiting_for_year)

@router.message(StateFilter(AdminStates.waiting_for_year))
async def add_book_year(message: Message, state: FSMContext):
    """Ввод года издания"""
    try:
        year = int(message.text.strip())
        await state.update_data(year=year)
        await message.answer("Введите автора книги:")
        await state.set_state(AdminStates.waiting_for_author)
    except ValueError:
        await message.answer("Пожалуйста, введите корректный год (число):")

@router.message(StateFilter(AdminStates.waiting_for_author))
async def add_book_author(message: Message, state: FSMContext):
    """Ввод автора книги"""
    await state.update_data(author=message.text.strip())
    await message.answer("Введите описание книги:")
    await state.set_state(AdminStates.waiting_for_description)

@router.message(StateFilter(AdminStates.waiting_for_description))
async def add_book_description(message: Message, state: FSMContext):
    """Ввод описания книги"""
    await state.update_data(description=message.text.strip())
    
    # Выбор жанра
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📚 Литература", callback_data="admin_genre_Литература")],
        [InlineKeyboardButton(text="💻 Тех литература", callback_data="admin_genre_Тех литература")]
    ])
    
    await message.answer("Выберите жанр:", reply_markup=keyboard)
    await state.set_state(AdminStates.waiting_for_genre)

@router.callback_query(F.data.startswith("admin_genre_"), StateFilter(AdminStates.waiting_for_genre))
async def add_book_genre(callback: CallbackQuery, state: FSMContext):
    """Выбор жанра книги"""
    genre = callback.data.split("admin_genre_")[1]
    await state.update_data(genre=genre)
    
    # Поджанры в зависимости от основного жанра
    if genre == "Литература":
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📖 Художественная", callback_data="admin_subgenre_Художественная")],
            [InlineKeyboardButton(text="📚 Классическая", callback_data="admin_subgenre_Классическая")],
            [InlineKeyboardButton(text="🕵️ Детектив", callback_data="admin_subgenre_Детектив")],
            [InlineKeyboardButton(text="💝 Роман", callback_data="admin_subgenre_Роман")],
            [InlineKeyboardButton(text="🚀 Фантастика", callback_data="admin_subgenre_Фантастика")],
            [InlineKeyboardButton(text="🎭 Драма", callback_data="admin_subgenre_Драма")],
            [InlineKeyboardButton(text="⏭️ Пропустить", callback_data="admin_subgenre_")]
        ])
    else:  # Тех литература
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="💻 Программирование", callback_data="admin_subgenre_Программирование")],
            [InlineKeyboardButton(text="🔧 Инженерия", callback_data="admin_subgenre_Инженерия")],
            [InlineKeyboardButton(text="🔬 Наука", callback_data="admin_subgenre_Наука")],
            [InlineKeyboardButton(text="🏗️ Архитектура", callback_data="admin_subgenre_Архитектура")],
            [InlineKeyboardButton(text="📊 Экономика", callback_data="admin_subgenre_Экономика")],
            [InlineKeyboardButton(text="🏥 Медицина", callback_data="admin_subgenre_Медицина")],
            [InlineKeyboardButton(text="⏭️ Пропустить", callback_data="admin_subgenre_")]
        ])
    
    await callback.message.edit_text("Выберите поджанр (или пропустите):", reply_markup=keyboard)
    await state.set_state(AdminStates.waiting_for_subgenre)

@router.callback_query(F.data.startswith("admin_subgenre_"), StateFilter(AdminStates.waiting_for_subgenre))
async def add_book_subgenre(callback: CallbackQuery, state: FSMContext):
    """Выбор поджанра и сохранение книги"""
    subgenre = callback.data.split("admin_subgenre_")[1] if callback.data.split("admin_subgenre_")[1] else None
    
    # Получаем все данные
    data = await state.get_data()
    
    # Добавляем книгу в БД
    book_id = await db.add_book(
        title=data['title'],
        author=data['author'],
        year=data['year'],
        description=data['description'],
        genre=data['genre'],
        subgenre=subgenre
    )
    
    success_text = "✅ Книга успешно добавлена!\n\n"
    success_text += f"📖 Название: {data['title']}\n"
    success_text += f"👤 Автор: {data['author']}\n"
    success_text += f"📅 Год: {data['year']}\n"
    success_text += f"🏷️ Жанр: {data['genre']}"
    if subgenre:
        success_text += f" / {subgenre}"
    success_text += f"\n📝 Описание: {data['description'][:100]}..."
    
    await callback.message.edit_text(success_text)
    await state.clear()

@router.message(F.text == "✏️ Редактировать книги")
async def edit_books_list(message: Message):
    """Список книг для редактирования"""
    if not is_admin(message.from_user.id):
        await message.answer("У вас нет прав для редактирования книг ❌")
        return
    
    books = await db.get_all_books(limit=10)
    
    if not books:
        await message.answer("В базе данных пока нет книг.")
        return
    
    keyboard_buttons = []
    text = "Выберите книгу для редактирования:\n\n"
    
    for book in books:
        text += f"📖 {book['title']} - {book['author']}\n"
        keyboard_buttons.append([
            InlineKeyboardButton(
                text=f"✏️ {book['title']}", 
                callback_data=f"edit_book_{book['id']}"
            )
        ])
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
    await message.answer(text, reply_markup=keyboard)

@router.callback_query(F.data.startswith("edit_book_"))
async def edit_book_menu(callback: CallbackQuery):
    """Меню редактирования конкретной книги"""
    book_id = int(callback.data.split("_")[2])
    book = await db.get_book_by_id(book_id)
    
    text = f"📖 Редактирование: {book['title']}\n\n"
    text += format_book_info(book, show_description=False)
    text += f"\n📝 Описание: {book['description'][:100]}...\n\n"
    text += "Что хотите изменить?"
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📝 Название", callback_data=f"edit_field_{book_id}_title")],
        [InlineKeyboardButton(text="👤 Автора", callback_data=f"edit_field_{book_id}_author")],
        [InlineKeyboardButton(text="📅 Год", callback_data=f"edit_field_{book_id}_year")],
        [InlineKeyboardButton(text="📖 Описание", callback_data=f"edit_field_{book_id}_description")],
        [InlineKeyboardButton(text="🗑️ Удалить книгу", callback_data=f"delete_book_{book_id}")],
        [InlineKeyboardButton(text="🔙 К списку", callback_data="back_to_edit_list")]
    ])
    
    await callback.message.edit_text(text, reply_markup=keyboard)

@router.callback_query(F.data.startswith("edit_field_"))
async def edit_field_start(callback: CallbackQuery, state: FSMContext):
    """Начало редактирования поля"""
    parts = callback.data.split("_")
    book_id = int(parts[2])
    field = parts[3]
    
    field_names = {
        'title': 'название',
        'author': 'автора',
        'year': 'год',
        'description': 'описание'
    }
    
    await callback.message.edit_text(f"Введите новое {field_names[field]}:")
    await state.update_data(book_id=book_id, field=field)
    await state.set_state(AdminStates.edit_waiting_value)

@router.message(StateFilter(AdminStates.edit_waiting_value))
async def edit_field_process(message: Message, state: FSMContext):
    """Обработка редактирования поля"""
    data = await state.get_data()
    book_id = data['book_id']
    field = data['field']
    new_value = message.text.strip()
    
    # Валидация для года
    if field == 'year':
        try:
            new_value = int(new_value)
        except ValueError:
            await message.answer("Пожалуйста, введите корректный год (число):")
            return
    
    # Обновляем в БД
    success = await db.update_book_field(book_id, field, new_value)
    
    if success:
        await message.answer(f"✅ Поле '{field}' успешно обновлено!")
    else:
        await message.answer("❌ Ошибка при обновлении книги.")
    
    await state.clear()

@router.callback_query(F.data.startswith("delete_book_"))
async def confirm_delete_book(callback: CallbackQuery):
    """Подтверждение удаления книги"""  
    book_id = int(callback.data.split("_")[2])
    book = await db.get_book_by_id(book_id)
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Да, удалить", callback_data=f"confirm_delete_{book_id}")],
        [InlineKeyboardButton(text="❌ Отмена", callback_data=f"edit_book_{book_id}")]
    ])
    
    await callback.message.edit_text(
        f"⚠️ Вы уверены, что хотите удалить книгу '{book['title']}'?",
        reply_markup=keyboard
    )

@router.callback_query(F.data.startswith("confirm_delete_"))
async def delete_book_confirmed(callback: CallbackQuery):
    """Удаление книги"""
    book_id = int(callback.data.split("_")[2])
    await db.delete_book(book_id)
    await callback.message.edit_text("✅ Книга успешно удалена!")

@router.callback_query(F.data == "back_to_edit_list")
async def back_to_edit_list(callback: CallbackQuery):
    """Возврат к списку редактирования"""
    await edit_books_list(callback.message)

@router.message(F.text == "📊 Статистика")
async def admin_statistics(message: Message):
    """Статистика для админа"""
    if not is_admin(message.from_user.id):
        await message.answer("У вас нет доступа к статистике ❌")
        return
    
    # Получаем статистику
    total_books = len(await db.get_all_books())
    total_users = len(await db.get_all_users())
    
    literature_books = len(await db.get_books_by_genre("Литература", limit=1000))
    tech_books = len(await db.get_books_by_genre("Тех литература", limit=1000))
    
    stats_text = "📊 Статистика бота:\n\n"
    stats_text += f"📚 Всего книг: {total_books}\n"
    stats_text += f"👥 Всего пользователей: {total_users}\n\n"
    stats_text += f"📖 Литература: {literature_books} книг\n"
    stats_text += f"💻 Тех литература: {tech_books} книг\n"
    
    await message.answer(stats_text)