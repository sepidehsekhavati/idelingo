import sqlite3
from datetime import datetime, timedelta
import json
import os
import re

# ==================== Database ====================
class Database:
    def __init__(self, db_path='idelingo.db'):
        self.db_path = db_path
        self._create_tables()
        self._migrate_database()
        self._create_indexes()
    
    def _get_connection(self):
        """ایجاد یک اتصال جدید (هر بار)"""
        return sqlite3.connect(self.db_path)
    
    def _create_tables(self):
        conn = self._get_connection()
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
        conn.close()
    
    def _migrate_database(self):
        conn = self._get_connection()
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
        finally:
            conn.close()
    
    def _create_indexes(self):
        conn = self._get_connection()
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
        finally:
            conn.close()
    
    # تمام متدهای قبلی که از self.cursor استفاده می‌کردند باید بازنویسی شوند.
    # در زیر متدهای مهم را با استفاده از اتصال موقت بازنویسی می‌کنیم.
    # (برای سایر متدها نیز به همین صورت عمل کنید)
    
    def execute_query(self, query, params=None, fetchone=False, fetchall=False, commit=False):
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            if commit:
                conn.commit()
            if fetchone:
                result = cursor.fetchone()
            elif fetchall:
                result = cursor.fetchall()
            else:
                result = None
            return result
        finally:
            conn.close()
    
    # به عنوان مثال، متد get_user_plan قبلی که در PlanManager استفاده می‌شود:
    def get_user_plan(self, user_id):
        query = 'SELECT * FROM user_plans WHERE user_id = ?'
        row = self.execute_query(query, (user_id,), fetchone=True)
        if not row:
            # ایجاد plan پیش‌فرض
            self.execute_query('INSERT INTO user_plans (user_id, plan_type, last_reset_date) VALUES (?, "daily", ?)',
                               (user_id, datetime.now().strftime("%Y-%m-%d")), commit=True)
            return self.get_user_plan(user_id)
        return {
            'id': row[0], 'user_id': row[1], 'plan_type': row[2], 'weekly_goal_words': row[3],
            'weekly_goal_grammar': row[4], 'weekly_goal_phrases': row[5], 'monthly_goal_words': row[6],
            'monthly_goal_grammar': row[7], 'monthly_goal_phrases': row[8], 'custom_goal_words': row[9],
            'custom_goal_grammar': row[10], 'custom_goal_phrases': row[11], 'custom_interval_days': row[12],
            'current_streak': row[13], 'longest_streak': row[14], 'last_reset_date': row[15]
        }
    
    # سایر متدها (مانند update_user_plan, etc.) باید به همین صورت بازنویسی شوند.
    # از آنجا که تعداد متدها زیاد است، لطفاً کل فایل Database.py را بازنویسی می‌کنیم.
