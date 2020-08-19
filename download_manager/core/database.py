import aiosqlite


async def initialize_database(db):
    await db.execute('''
CREATE TABLE IF NOT EXISTS download_url (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    url TEXT,
    path TEXT,
    http_user_agent TEXT,
    http_referer TEXT,
    auth_username TEXT,
    auth_password TEXT,
    cookie_jar TEXT,
    meta TEXT,

    created_at TEXT,
    retries INTEGER,
    downloaded_at TEXT
)
    ''')


async def open_sqlite(app):
    conf = app['config']
    db = await aiosqlite.connect(conf['database_name'])
    db.row_factory = aiosqlite.Row
    await initialize_database(db)
    app['db'] = db


async def close_sqlite(app):
    await app['db'].close()
