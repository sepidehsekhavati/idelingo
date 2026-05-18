import sqlite3
import threading
from datetime import datetime, timedelta
import json
import os
import re

# ==================== Thread-safe connection ====================
_local = threading.local()

def _get_connection():
    """بازگرداندن اتصال دیتابیس مخصوص thread جاری"""
    if not hasattr(_local, 'conn'):
        _local.conn = sqlite3.connect('idelingo.db')
        _local.conn.row_factory = sqlite3.Row  # اختیاری، برای راحتی
    return _local.conn

def _close_connection():
    """بستن اتصال thread جاری (در صورت نیاز)"""
    if hasattr(_local, 'conn'):
        _local.conn.close()
        del _local.conn

# ==================== Database ====================
class Database:
    def __init__(self):
        self._create_tables()
        self._migrate_database()
        self._create_indexes()
    
    def _get_cursor(self):
        """بازگرداندن cursor از اتصال thread-safe"""
        return _get_connection().cursor()
    
    def _commit(self):
        """commit کردن اتصال thread جاری"""
        _get_connection().commit()
    
    def _create_tables(self):
        conn = _get_connection()
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL, email TEXT UNIQUE NOT NULL, password_hash TEXT NOT NULL,
            avatar TEXT DEFAULT '😊', plan TEXT DEFAULT 'free', created_at TEXT NOT NULL,
            last_active TEXT NOT NULL, daily_goal INTEGER DEFAULT 10, current_streak INTEGER DEFAULT 0,
            xp_total INTEGER DEFAULT 0, level INTEGER DEFAULT 1)''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS daily_progress (id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL, date TEXT NOT NULL, words_learned INTEGER DEFAULT 0,
            grammar_learned INTEGER DEFAULT 0, minutes_studied INTEGER DEFAULT 0,
            goal_achieved BOOLEAN DEFAULT FALSE, UNIQUE(user_id, date))''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS vocabulary (id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL, word TEXT NOT NULL, meaning TEXT NOT NULL, example TEXT,
            language TEXT NOT NULL, difficulty TEXT DEFAULT 'medium', next_review TEXT,
            review_count INTEGER DEFAULT 0, tags TEXT, date_added TEXT NOT NULL, notes TEXT,
            error_count INTEGER DEFAULT 0, last_reviewed TEXT)''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS grammar (id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL, rule TEXT NOT NULL, explanation TEXT, example TEXT,
            language TEXT NOT NULL, tags TEXT, date_added TEXT NOT NULL)''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS phrases (id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL, phrase TEXT NOT NULL, meaning TEXT NOT NULL, tags TEXT,
            notes TEXT, date_added TEXT NOT NULL, practice_count INTEGER DEFAULT 0, last_practiced TEXT)''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS user_plans (id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL UNIQUE, plan_type TEXT DEFAULT 'daily',
            weekly_goal_words INTEGER DEFAULT 20, weekly_goal_grammar INTEGER DEFAULT 5,
            weekly_goal_phrases INTEGER DEFAULT 10, monthly_goal_words INTEGER DEFAULT 80,
            monthly_goal_grammar INTEGER DEFAULT 20, monthly_goal_phrases INTEGER DEFAULT 40,
            custom_goal_words INTEGER DEFAULT 10, custom_goal_grammar INTEGER DEFAULT 3,
            custom_goal_phrases INTEGER DEFAULT 5, custom_interval_days INTEGER DEFAULT 1,
            current_streak INTEGER DEFAULT 0, longest_streak INTEGER DEFAULT 0, last_reset_date TEXT)''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS study_sessions (id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL, date TEXT NOT NULL, items_reviewed INTEGER DEFAULT 0,
            correct_count INTEGER DEFAULT 0, xp_earned INTEGER DEFAULT 0)''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS practice_chat (id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL, message TEXT NOT NULL, corrected_text TEXT,
            suggestions TEXT, timestamp TEXT NOT NULL)''')
        conn.commit()
    
    def _migrate_database(self):
        conn = _get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("PRAGMA table_info(vocabulary)")
            columns = [col[1] for col in cursor.fetchall()]
            for col in ['tags', 'notes', 'error_count', 'last_reviewed']:
                if col not in columns:
                    cursor.execute(f"ALTER TABLE vocabulary ADD COLUMN {col} TEXT")
            cursor.execute('CREATE TABLE IF NOT EXISTS privacy_settings (user_id INTEGER PRIMARY KEY, profile_public BOOLEAN DEFAULT 1)')
            cursor.execute('INSERT OR IGNORE INTO privacy_settings (user_id, profile_public) SELECT id, 1 FROM users')
            conn.commit()
        except Exception as e:
            print(f"Migration error: {e}")
    
    def _create_indexes(self):
        conn = _get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_vocabulary_user_id ON vocabulary(user_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_vocabulary_word ON vocabulary(word)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_vocabulary_language ON vocabulary(language)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_vocabulary_difficulty ON vocabulary(difficulty)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_phrases_user_id ON phrases(user_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_phrases_phrase ON phrases(phrase)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_practice_chat_user_id ON practice_chat(user_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_practice_chat_timestamp ON practice_chat(timestamp)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_daily_progress_user_date ON daily_progress(user_id, date)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_user_plans_user_id ON user_plans(user_id)')
            conn.commit()
            print("✅ Database indexes created successfully")
        except Exception as e:
            print(f"Error creating indexes: {e}")
    
    # ========== دسترسی به cursor و conn برای سازگاری با کدهای موجود ==========
    @property
    def cursor(self):
        """بازگرداندن cursor از اتصال thread-safe (برای استفاده در UserManager و PlanManager)"""
        return _get_connection().cursor()
    
    @property
    def conn(self):
        """بازگرداندن اتصال thread-safe"""
        return _get_connection()
    
    def close(self):
        """بستن اتصال thread جاری (در پایان کار برنامه)"""
        _close_connection()
