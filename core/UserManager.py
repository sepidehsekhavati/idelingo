# core/UserManager.py
from Database import Database
from GrammarEnhancer import GrammarEnhancer
from OfflineDictionary import OfflineDictionary  # این خط رو فعال کن
from AdvancedGrammarChecker import AdvancedGrammarChecker
from PlanManager import PlanManager
import hashlib
import secrets
from datetime import datetime, timedelta


class UserManager:
    def __init__(self):
        try:
            self.db = Database()
            self.grammar_enhancer = GrammarEnhancer()
            self.offline_dict = OfflineDictionary()  # این خط رو فعال کن
            self.grammar_checker = AdvancedGrammarChecker()
            self.plan_manager = PlanManager(self.db)
            self.current_user = None
            
            print("🎉 UserManager با موفقیت راه‌اندازی شد!")
            print("✅ تمام کلاس‌ها لود شدند")
            
        except Exception as e:
            print(f"❌ Error in UserManager: {e}")
            import traceback
            traceback.print_exc()
            raise
   
            self.db = Database()
            self.grammar_enhancer = GrammarEnhancer()
            # self.offline_dict = OfflineDictionary()  # حذف شد
            self.grammar_checker = AdvancedGrammarChecker()
            self.plan_manager = PlanManager(self.db)
            self.current_user = None
            
            print("🎉 UserManager با موفقیت راه‌اندازی شد!")
            print("✅ تمام کلاس‌ها لود شدند")
            
        except Exception as e:
            print(f"❌ Error in UserManager: {e}")
            import traceback
            traceback.print_exc()
            raise
    
    def hash_password(self, password):
        """هش کردن پسورد با hashlib (بدون نیاز به bcrypt)"""
        salt = secrets.token_hex(16)
        hash_obj = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), 100000)
        return f"{salt}${hash_obj.hex()}"
    
    def verify_password(self, password, hashed):
        """تایید پسورد با hashlib"""
        try:
            salt, stored_hash = hashed.split('$')
            hash_obj = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), 100000)
            return hash_obj.hex() == stored_hash
        except:
            return False
    
    def register(self, username, email, password):
        """ثبت نام کاربر جدید"""
        try:
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            password_hash = self.hash_password(password)
            
            self.db.cursor.execute(
                'INSERT INTO users (username, email, password_hash, created_at, last_active) VALUES (?, ?, ?, ?, ?)',
                (username, email, password_hash, now, now)
            )
            self.db.conn.commit()
            user_id = self.db.cursor.lastrowid
            
            # ایجاد تنظیمات حریم خصوصی
            self.db.cursor.execute(
                'INSERT INTO privacy_settings (user_id, profile_public) VALUES (?, 1)',
                (user_id,)
            )
            self.db.conn.commit()
            
            return True, "Registration successful!"
        except Exception as e:
            return False, f"Error: {str(e)}"
    
    def login(self, username, password):
        """ورود کاربر"""
        try:
            self.db.cursor.execute(
                'SELECT id, username, email, password_hash, avatar, plan, daily_goal, current_streak, xp_total, level FROM users WHERE username = ? OR email = ?',
                (username, username)
            )
            row = self.db.cursor.fetchone()
            
            if not row:
                return False, "User not found", None
            
            if not self.verify_password(password, row[3]):
                return False, "Wrong password", None
            
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.db.cursor.execute("UPDATE users SET last_active = ? WHERE id = ?", (now, row[0]))
            self.db.conn.commit()
            
            user = {
                'id': row[0],
                'username': row[1],
                'email': row[2],
                'avatar': row[4] or '😊',
                'plan': row[5] or 'free',
                'daily_goal': row[6] or 10,
                'current_streak': row[7] or 0,
                'xp_total': row[8] or 0,
                'level': row[9] or 1
            }
            self.current_user = user
            return True, "Welcome back!", user
            
        except Exception as e:
            return False, f"Error: {str(e)}", None
    
    def add_xp(self, user_id, amount):
        try:
            self.db.cursor.execute("SELECT xp_total, level FROM users WHERE id = ?", (user_id,))
            row = self.db.cursor.fetchone()
            if not row:
                return False
            xp, level = row
            new_xp = xp + amount
            new_level = level
            while new_xp >= new_level * 100:
                new_level += 1
            self.db.cursor.execute("UPDATE users SET xp_total = ?, level = ? WHERE id = ?", (new_xp, new_level, user_id))
            self.db.conn.commit()
            return new_level > level
        except:
            return False
    
    def get_daily_progress(self, user_id):
        try:
            today = datetime.now().strftime("%Y-%m-%d")
            self.db.cursor.execute(
                'SELECT COALESCE(words_learned, 0), COALESCE(grammar_learned, 0), COALESCE(minutes_studied, 0), COALESCE(goal_achieved, 0) FROM daily_progress WHERE user_id = ? AND date = ?',
                (user_id, today)
            )
            row = self.db.cursor.fetchone()
            if row:
                return {
                    'words_learned': row[0],
                    'grammar_learned': row[1],
                    'minutes_studied': row[2],
                    'goal_achieved': bool(row[3])
                }
            return {'words_learned': 0, 'grammar_learned': 0, 'minutes_studied': 0, 'goal_achieved': False}
        except:
            return {'words_learned': 0, 'grammar_learned': 0, 'minutes_studied': 0, 'goal_achieved': False}
    
    def update_daily_progress(self, user_id, words_added=0, grammar_added=0, minutes=0, phrases_added=0):
        try:
            today = datetime.now().strftime("%Y-%m-%d")
            self.db.cursor.execute('''INSERT INTO daily_progress (user_id, date, words_learned, grammar_learned, minutes_studied)
                VALUES (?, ?, ?, ?, ?) ON CONFLICT(user_id, date) DO UPDATE SET
                words_learned = words_learned + ?, grammar_learned = grammar_learned + ?, minutes_studied = minutes_studied + ?''',
                (user_id, today, words_added, grammar_added, minutes, words_added, grammar_added, minutes))
            self.db.conn.commit()
            return True
        except:
            return False
    
    def update_profile(self, user_id, **kwargs):
        for key, value in kwargs.items():
            if key in ['avatar', 'daily_goal']:
                try:
                    self.db.cursor.execute(f"UPDATE users SET {key} = ? WHERE id = ?", (value, user_id))
                    self.db.conn.commit()
                except:
                    pass
    
    def add_vocabulary(self, user_id, word, meaning, example, language, difficulty, tags, notes):
        try:
            today = datetime.now().strftime("%Y-%m-%d")
            next_review = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
            self.db.cursor.execute(
                'INSERT INTO vocabulary (user_id, word, meaning, example, language, difficulty, next_review, tags, date_added, notes, error_count) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0)',
                (user_id, word, meaning, example, language, difficulty, next_review, tags, today, notes)
            )
            self.db.conn.commit()
            self.update_daily_progress(user_id, words_added=1)
            self.add_xp(user_id, 10)
            return self.db.cursor.lastrowid
        except Exception as e:
            print(f"Error adding vocabulary: {e}")
            return None
    
    def get_vocabulary(self, user_id, filters=None):
        query = "SELECT * FROM vocabulary WHERE user_id = ?"
        params = [user_id]
        if filters:
            if filters.get('search'):
                query += " AND (word LIKE ? OR meaning LIKE ?)"
                params.extend([f"%{filters['search']}%", f"%{filters['search']}%"])
            if filters.get('language') and filters['language'] != 'All':
                query += " AND language = ?"
                params.append(filters['language'])
            if filters.get('difficulty') and filters['difficulty'] != 'All':
                query += " AND difficulty = ?"
                params.append(filters['difficulty'])
        query += " ORDER BY date_added DESC"
        self.db.cursor.execute(query, params)
        return self.db.cursor.fetchall()
    
    def update_vocabulary(self, vocab_id, word, meaning, example, language, difficulty):
        self.db.cursor.execute(
            'UPDATE vocabulary SET word = ?, meaning = ?, example = ?, language = ?, difficulty = ? WHERE id = ?',
            (word, meaning, example, language, difficulty, vocab_id)
        )
        self.db.conn.commit()
    
    def delete_vocabulary(self, vocab_id):
        self.db.cursor.execute("DELETE FROM vocabulary WHERE id = ?", (vocab_id,))
        self.db.conn.commit()
    
    def add_phrase(self, user_id, phrase, meaning, tags, notes):
        today = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.db.cursor.execute(
            'INSERT INTO phrases (user_id, phrase, meaning, tags, notes, date_added, practice_count) VALUES (?, ?, ?, ?, ?, ?, 0)',
            (user_id, phrase, meaning, tags, notes, today)
        )
        self.db.conn.commit()
        self.update_daily_progress(user_id, words_added=1)
        self.add_xp(user_id, 5)
        return self.db.cursor.lastrowid
    
    def get_phrases(self, user_id, search=None):
        if search:
            self.db.cursor.execute(
                'SELECT * FROM phrases WHERE user_id = ? AND (phrase LIKE ? OR meaning LIKE ? OR tags LIKE ?) ORDER BY date_added DESC',
                (user_id, f"%{search}%", f"%{search}%", f"%{search}%")
            )
        else:
            self.db.cursor.execute('SELECT * FROM phrases WHERE user_id = ? ORDER BY date_added DESC', (user_id,))
        return self.db.cursor.fetchall()
    
    def update_phrase(self, phrase_id, phrase, meaning, tags, notes):
        self.db.cursor.execute(
            'UPDATE phrases SET phrase = ?, meaning = ?, tags = ?, notes = ? WHERE id = ?',
            (phrase, meaning, tags, notes, phrase_id)
        )
        self.db.conn.commit()
    
    def delete_phrase(self, phrase_id):
        self.db.cursor.execute('DELETE FROM phrases WHERE id = ?', (phrase_id,))
        self.db.conn.commit()
    
    def increment_phrase_practice(self, phrase_id):
        self.db.cursor.execute(
            'UPDATE phrases SET practice_count = practice_count + 1, last_practiced = ? WHERE id = ?',
            (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), phrase_id)
        )
        self.db.conn.commit()
    
    def save_practice_message(self, user_id, message, corrected=None, suggestions=None):
        self.db.cursor.execute(
            'INSERT INTO practice_chat (user_id, message, corrected_text, suggestions, timestamp) VALUES (?, ?, ?, ?, ?)',
            (user_id, message, corrected, suggestions, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        )
        self.db.conn.commit()
    
    def get_practice_history(self, user_id):
        self.db.cursor.execute(
            'SELECT message, corrected_text, suggestions, timestamp FROM practice_chat WHERE user_id = ? ORDER BY timestamp DESC LIMIT 50',
            (user_id,)
        )
        return self.db.cursor.fetchall()
    
    def check_grammar_offline(self, text):
        return self.grammar_checker.check_and_correct(text)
    
    def get_grammar_info(self, topic):
        return self.grammar_enhancer.get_grammar_info(topic)
    
    def get_all_grammar_topics(self):
        return self.grammar_enhancer.get_all_topics()
    
    def search_grammar_rules(self, query):
        return self.grammar_enhancer.search_grammar(query)
    
    def get_grammar_by_level(self, level):
        return self.grammar_enhancer.get_rules_by_level(level)
    
    def add_grammar_favorite(self, topic):
        return self.grammar_enhancer.add_favorite(topic)
    
    def remove_grammar_favorite(self, topic):
        return self.grammar_enhancer.remove_favorite(topic)
    
    def get_grammar_favorites(self):
        return self.grammar_enhancer.get_favorites()
    
    def is_grammar_favorite(self, topic):
        return self.grammar_enhancer.is_favorite(topic)
    
    def get_grammar_notes(self, topic):
        return self.grammar_enhancer.get_notes(topic)
    
    def save_grammar_note(self, topic, note):
        self.grammar_enhancer.save_note(topic, note)
    
    def get_grammar_stats(self):
        return self.grammar_enhancer.get_grammar_stats()
    
    def get_user_plan(self, user_id):
        return self.plan_manager.get_user_plan(user_id)
    
    def update_user_plan(self, user_id, plan_type, **kwargs):
        self.plan_manager.update_plan(user_id, plan_type, **kwargs)
    
    def get_plan_progress(self, user_id, today_stats):
        return self.plan_manager.get_plan_progress(user_id, today_stats)
    
    def get_leaderboard(self, limit=10):
        today = datetime.now().strftime("%Y-%m-%d")
        self.db.cursor.execute(
            'SELECT u.username, u.avatar, u.level, COALESCE(dp.words_learned, 0) as score FROM users u LEFT JOIN daily_progress dp ON u.id = dp.user_id AND dp.date = ? ORDER BY score DESC, u.level DESC LIMIT ?',
            (today, limit)
        )
        return self.db.cursor.fetchall()
    
    def search_users(self, query, current_user_id):
        self.db.cursor.execute(
            'SELECT id, username, avatar, level, xp_total FROM users WHERE username LIKE ? AND id != ? LIMIT 20',
            (f"%{query}%", current_user_id)
        )
        return self.db.cursor.fetchall()
    
    def get_user_public_profile(self, target_id):
        self.db.cursor.execute(
            'SELECT u.username, u.avatar, u.level, u.xp_total, u.current_streak, COALESCE(p.profile_public, 1) as is_public FROM users u LEFT JOIN privacy_settings p ON u.id = p.user_id WHERE u.id = ?',
            (target_id,)
        )
        row = self.db.cursor.fetchone()
        if not row:
            return None, "User not found"
        if not row[5]:
            return None, "This user's profile is private"
        
        today = datetime.now().strftime("%Y-%m-%d")
        self.db.cursor.execute(
            'SELECT words_learned, goal_achieved FROM daily_progress WHERE user_id = ? AND date = ?',
            (target_id, today)
        )
        progress = self.db.cursor.fetchone()
        
        return {
            'username': row[0],
            'avatar': row[1],
            'level': row[2],
            'xp': row[3],
            'streak': row[4],
            'today_words': progress[0] if progress else 0,
            'goal_achieved': progress[1] if progress else False
        }, None
    
    def get_privacy_settings(self, user_id):
        self.db.cursor.execute("SELECT profile_public FROM privacy_settings WHERE user_id = ?", (user_id,))
        row = self.db.cursor.fetchone()
        return {'profile_public': bool(row[0])} if row else {'profile_public': True}
    
    def update_privacy(self, user_id, profile_public):
        self.db.cursor.execute("UPDATE privacy_settings SET profile_public = ? WHERE user_id = ?", (profile_public, user_id))
        self.db.conn.commit()
    
    def close(self):
        self.db.close()
