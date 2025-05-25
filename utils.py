# utils.py - Вспомогательные функции
from config import Config

def is_admin(user_id: int) -> bool:
    """Проверка является ли пользователь администратором"""
    return user_id in Config.ADMIN_IDS

def format_book_info(book: dict, show_description: bool = True) -> str:
    """Форматирование информации о книге для отображения"""
    text = f"📖 {book['title']}\n"
    text += f"👤 Автор: {book['author']}\n"
    text += f"📅 Год: {book['year']}\n"
    text += f"🏷️ Жанр: {book['genre']}"
    
    if book['subgenre']:
        text += f" / {book['subgenre']}"
    
    if show_description:
        description = book['description']
        if len(description) > 200:
            description = description[:200] + "..."
        text += f"\n\n📝 Описание:\n{description}"
    
    return text

def format_books_list(books: list, show_details: bool = False) -> str:
    """Форматирование списка книг"""
    if not books:
        return "Книги не найдены 😔"
    
    text = ""
    for book in books:
        if show_details:
            text += format_book_info(book, show_description=False) + "\n\n"
        else:
            text += f"📖 {book['title']} - {book['author']} ({book['year']})\n"
    
    return text.strip()

def truncate_text(text: str, max_length: int = 100) -> str:
    """Обрезка текста до указанной длины"""
    if len(text) <= max_length:
        return text
    return text[:max_length] + "..."

def validate_year(year_str: str) -> tuple[bool, int]:
    """Валидация года издания"""
    try:
        year = int(year_str.strip())
        if 1000 <= year <= 2030:  # Разумные границы для года издания
            return True, year
        else:
            return False, 0
    except ValueError:
        return False, 0

def clean_text(text: str) -> str:
    """Очистка текста от лишних пробелов и символов"""
    return text.strip().replace('\n', ' ').replace('\t', ' ')

def get_genre_emoji(genre: str) -> str:
    """Получение эмодзи для жанра"""
    genre_emojis = {
        "Литература": "📚",
        "Тех литература": "💻",
        "Художественная": "📖",
        "Классическая": "📜",
        "Детектив": "🕵️",
        "Роман": "💝",
        "Фантастика": "🚀",
        "Драма": "🎭",
        "Программирование": "💻",
        "Инженерия": "🔧",
        "Наука": "🔬",
        "Архитектура": "🏗️",
        "Экономика": "📊",
        "Медицина": "🏥"
    }
    return genre_emojis.get(genre, "📖")

def format_profile_stats(favorite_count: int, recommendations_count: int) -> str:
    """Форматирование статистики профиля"""
    stats = f"📊 Статистика:\n"
    stats += f"❤️ Любимых книг: {favorite_count}\n"
    stats += f"💡 Рекомендаций: {recommendations_count}"
    return stats

def format_admin_stats(total_books: int, total_users: int, literature_books: int, tech_books: int) -> str:
    """Форматирование статистики для админа"""
    stats = "📊 Статистика бота:\n\n"
    stats += f"📚 Всего книг: {total_books}\n"
    stats += f"👥 Всего пользователей: {total_users}\n\n"
    stats += f"📖 Литература: {literature_books} книг\n"
    stats += f"💻 Тех литература: {tech_books} книг"
    return stats