import aiosqlite
from utils.config import settings

async def init_db():
    async with aiosqlite.connect(settings.database_file) as db:
        # Создаем таблицу групп
        await db.execute('''
            CREATE TABLE IF NOT EXISTS groups (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL
            )
        ''')
        
        # Создаем таблицу пользователей
        await db.execute('''
            CREATE TABLE IF NOT EXISTS users (
                tg_id INTEGER PRIMARY KEY,
                username TEXT,
                role TEXT DEFAULT 'student',
                group_id INTEGER,
                FOREIGN KEY (group_id) REFERENCES groups (id)
            )
        ''')
        
        # Проверяем, есть ли администратор (ты) в базе
        await db.execute('''
            INSERT OR IGNORE INTO users (tg_id, role) 
            VALUES (?, ?)
        ''', (settings.admin_id, 'admin'))
        
        await db.commit()

async def get_user_role(tg_id: int) -> str:
    async with aiosqlite.connect(settings.database_file) as db:
        async with db.execute('SELECT role FROM users WHERE tg_id = ?', (tg_id,)) as cursor:
            row = await cursor.fetchone()
            return row[0] if row else 'student'

async def register_user(tg_id: int, username: str, group_id: int = None):
    async with aiosqlite.connect(settings.database_file) as db:
        await db.execute('''
            INSERT OR IGNORE INTO users (tg_id, username, group_id) 
            VALUES (?, ?, ?)
        ''', (tg_id, username, group_id))
        await db.commit()

async def add_group(name: str) -> int:
    async with aiosqlite.connect(settings.database_file) as db:
        await db.execute('INSERT OR IGNORE INTO groups (name) VALUES (?)', (name,))
        await db.commit()
        async with db.execute('SELECT id FROM groups WHERE name = ?', (name,)) as cursor:
            row = await cursor.fetchone()
            return row[0]

async def set_user_role(tg_id: int, role: str):
    async with aiosqlite.connect(settings.database_file) as db:
        await db.execute('UPDATE users SET role = ? WHERE tg_id = ?', (role, tg_id))
        await db.commit()

async def get_user_by_username(username: str) -> dict:
    # Убираем @ если пользователь ввел его
    username = username.replace('@', '')
    async with aiosqlite.connect(settings.database_file) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute('SELECT * FROM users WHERE username = ?', (username,)) as cursor:
            row = await cursor.fetchone()
            return dict(row) if row else None

async def update_user_group(tg_id: int, group_id: int):
    async with aiosqlite.connect(settings.database_file) as db:
        await db.execute('UPDATE users SET group_id = ? WHERE tg_id = ?', (group_id, tg_id))
        await db.commit()

async def get_all_users_detailed() -> list:
    """Возвращает список пользователей с именами их групп."""
    async with aiosqlite.connect(settings.database_file) as db:
        db.row_factory = aiosqlite.Row
        query = '''
            SELECT u.tg_id, u.username, u.role, g.name as group_name 
            FROM users u 
            LEFT JOIN groups g ON u.group_id = g.id
        '''
        async with db.execute(query) as cursor:
            rows = await cursor.fetchall()
            return [dict(r) for r in rows]

async def delete_user(tg_id: int):
    async with aiosqlite.connect(settings.database_file) as db:
        await db.execute('DELETE FROM users WHERE tg_id = ?', (tg_id,))
        await db.commit()

async def get_group_members(group_id: int) -> list:
    async with aiosqlite.connect(settings.database_file) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute('SELECT tg_id, username FROM users WHERE group_id = ?', (group_id,)) as cursor:
            rows = await cursor.fetchall()
            return [dict(r) for r in rows]

async def remove_user_from_group(tg_id: int):
    async with aiosqlite.connect(settings.database_file) as db:
        await db.execute('UPDATE users SET group_id = NULL WHERE tg_id = ?', (tg_id,))
        await db.commit()

async def delete_group(group_id: int):
    async with aiosqlite.connect(settings.database_file) as db:
        # Убираем привязку пользователей к этой группе перед удалением
        await db.execute('UPDATE users SET group_id = NULL WHERE group_id = ?', (group_id,))
        await db.execute('DELETE FROM groups WHERE id = ?', (group_id,))
        await db.commit()

async def get_groups() -> list:
    async with aiosqlite.connect(settings.database_file) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute('SELECT id, name FROM groups') as cursor:
            rows = await cursor.fetchall()
            return [dict(r) for r in rows]

async def get_user_group_info(tg_id: int) -> dict:
    async with aiosqlite.connect(settings.database_file) as db:
        db.row_factory = aiosqlite.Row
        # Сначала проверяем, есть ли у пользователя группа
        query = '''
            SELECT g.id, g.name 
            FROM groups g 
            JOIN users u ON u.group_id = g.id 
            WHERE u.tg_id = ?
        '''
        async with db.execute(query, (tg_id,)) as cursor:
            row = await cursor.fetchone()
            if row:
                return dict(row)
            
            # Если это админ и у него не назначена группа, пробуем найти первую попавшуюся группу для теста
            if tg_id == settings.admin_id:
                async with db.execute('SELECT id, name FROM groups LIMIT 1') as cursor:
                    row = await cursor.fetchone()
                    return dict(row) if row else None
            
            return None

async def get_group_name_by_id(group_id: int) -> str:
    async with aiosqlite.connect(settings.database_file) as db:
        async with db.execute('SELECT name FROM groups WHERE id = ?', (group_id,)) as cursor:
            row = await cursor.fetchone()
            return row[0] if row else None

async def get_user_id_by_identifier(identifier: str) -> int:
    """Ищет ID пользователя по username или прямому ID."""
    if not identifier: return None
    
    # Если это число (ID)
    if identifier.isdigit():
        async with aiosqlite.connect(settings.database_file) as db:
            async with db.execute('SELECT tg_id FROM users WHERE tg_id = ?', (int(identifier),)) as cursor:
                row = await cursor.fetchone()
                return row[0] if row else None
    
    # Если это username
    username = identifier.replace('@', '').strip()
    async with aiosqlite.connect(settings.database_file) as db:
        async with db.execute('SELECT tg_id FROM users WHERE LOWER(username) = LOWER(?)', (username,)) as cursor:
            row = await cursor.fetchone()
            return row[0] if row else None
