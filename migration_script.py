import asyncio
from sqlalchemy import text
from database.database import DatabaseManager

async def migrate_database():
    """Миграция для добавления полей файлов"""
    db = DatabaseManager()
    
    async with db.engine.begin() as conn:
        try:
            await conn.execute(text("ALTER TABLE books ADD COLUMN file_id VARCHAR(255)"))
            await conn.execute(text("ALTER TABLE books ADD COLUMN file_name VARCHAR(255)"))
            await conn.execute(text("ALTER TABLE books ADD COLUMN file_size INTEGER"))
            await conn.execute(text("ALTER TABLE books ADD COLUMN file_type VARCHAR(50)"))
            print("✅ Миграция успешно выполнена!")
        except Exception as e:
            print(f"❌ Ошибка миграции: {e}")

if __name__ == "__main__":
    asyncio.run(migrate_database())