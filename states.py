# states.py - Состояния FSM (Finite State Machine)
from aiogram.fsm.state import State, StatesGroup

class AdminStates(StatesGroup):
    """Состояния для админ панели"""
    
    # Состояния добавления книги
    waiting_for_title = State()
    waiting_for_year = State()
    waiting_for_author = State()
    waiting_for_description = State()
    waiting_for_genre = State()
    waiting_for_subgenre = State()
    
    # Состояния редактирования книги
    edit_waiting_book_id = State()
    edit_waiting_field = State()
    edit_waiting_value = State()

class SearchStates(StatesGroup):
    """Состояния для поиска книг"""
    waiting_for_search_query = State()

class UserStates(StatesGroup):
    """Состояния для обычных пользователей"""
    selecting_favorite_to_add = State()
    selecting_favorite_to_remove = State()
    viewing_recommendations = State()

class BookStates(StatesGroup):
    """Состояния для работы с книгами"""
    viewing_book_details = State()
    selecting_book_from_genre = State()
    browsing_genre_page = State()