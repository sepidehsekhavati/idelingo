import sqlite3
from datetime import datetime, timedelta

class Database:
    def __init__(self):
        self.conn = sqlite3.connect('idelingo.db')
        self.cursor = self.conn.cursor()
        self.create_tables()
        self.migrate_database()
        self.create_indexes()
    
    def migrate_database(self):
        try:
            self.cursor.execute("PRAGMA table_info(vocabulary)")
            columns = [col[1] for col in self.cursor.fetchall()]
            for col in ['tags', 'notes', 'error_count', 'last_reviewed']:
                if col not in columns:
                    self.cursor.execute(f"ALTER TABLE vocabulary ADD COLUMN {col} TEXT")
            self.cursor.execute('CREATE TABLE IF NOT EXISTS privacy_settings (user_id INTEGER PRIMARY KEY, profile_public BOOLEAN DEFAULT 1)')
            self.cursor.execute('INSERT OR IGNORE INTO privacy_settings (user_id, profile_public) SELECT id, 1 FROM users')
            self.conn.commit()
        except Exception as e:
            print(f"Migration error: {e}")
    
    def create_tables(self):
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL, email TEXT UNIQUE NOT NULL, password_hash TEXT NOT NULL,
            avatar TEXT DEFAULT '😊', plan TEXT DEFAULT 'free', created_at TEXT NOT NULL,
            last_active TEXT NOT NULL, daily_goal INTEGER DEFAULT 10, current_streak INTEGER DEFAULT 0,
            xp_total INTEGER DEFAULT 0, level INTEGER DEFAULT 1)''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS daily_progress (id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL, date TEXT NOT NULL, words_learned INTEGER DEFAULT 0,
            grammar_learned INTEGER DEFAULT 0, minutes_studied INTEGER DEFAULT 0,
            goal_achieved BOOLEAN DEFAULT FALSE, UNIQUE(user_id, date))''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS vocabulary (id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL, word TEXT NOT NULL, meaning TEXT NOT NULL, example TEXT,
            language TEXT NOT NULL, difficulty TEXT DEFAULT 'medium', next_review TEXT,
            review_count INTEGER DEFAULT 0, tags TEXT, date_added TEXT NOT NULL, notes TEXT,
            error_count INTEGER DEFAULT 0, last_reviewed TEXT)''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS grammar (id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL, rule TEXT NOT NULL, explanation TEXT, example TEXT,
            language TEXT NOT NULL, tags TEXT, date_added TEXT NOT NULL)''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS phrases (id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL, phrase TEXT NOT NULL, meaning TEXT NOT NULL, tags TEXT,
            notes TEXT, date_added TEXT NOT NULL, practice_count INTEGER DEFAULT 0, last_practiced TEXT)''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS user_plans (id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL UNIQUE, plan_type TEXT DEFAULT 'daily',
            weekly_goal_words INTEGER DEFAULT 20, weekly_goal_grammar INTEGER DEFAULT 5,
            weekly_goal_phrases INTEGER DEFAULT 10, monthly_goal_words INTEGER DEFAULT 80,
            monthly_goal_grammar INTEGER DEFAULT 20, monthly_goal_phrases INTEGER DEFAULT 40,
            custom_goal_words INTEGER DEFAULT 10, custom_goal_grammar INTEGER DEFAULT 3,
            custom_goal_phrases INTEGER DEFAULT 5, custom_interval_days INTEGER DEFAULT 1,
            current_streak INTEGER DEFAULT 0, longest_streak INTEGER DEFAULT 0, last_reset_date TEXT)''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS study_sessions (id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL, date TEXT NOT NULL, items_reviewed INTEGER DEFAULT 0,
            correct_count INTEGER DEFAULT 0, xp_earned INTEGER DEFAULT 0)''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS practice_chat (id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL, message TEXT NOT NULL, corrected_text TEXT,
            suggestions TEXT, timestamp TEXT NOT NULL)''')
        self.conn.commit()
    
    def create_indexes(self):
        try:
            self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_vocabulary_user_id ON vocabulary(user_id)')
            self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_vocabulary_word ON vocabulary(word)')
            self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_phrases_user_id ON phrases(user_id)')
            self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_practice_chat_user_id ON practice_chat(user_id)')
            self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_daily_progress_user_date ON daily_progress(user_id, date)')
            self.conn.commit()
        except Exception as e:
            print(f"Index error: {e}")
    
    def close(self):
        self.conn.close()
