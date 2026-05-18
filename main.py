import flet as ft
import sys
import os
from datetime import datetime

# حل مشکل import
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "core"))

from UserManager import UserManager
from OfflineDictionary import OfflineDictionary

# Colors
COLORS = {
    'bg': '#0a0a0a',
    'card': '#1a1a2e',
    'sidebar': '#111122',
    'accent': '#fbbf24',
    'accent_dark': '#d97706',
    'success': '#10b981',
    'danger': '#ef4444',
    'warning': '#f59e0b',
    'info': '#3b82f6',
    'text': '#f3f4f6',
    'text_secondary': '#9ca3af',
    'text_muted': '#6b7280'
}

# مسیر لوگو
base_dir = os.path.dirname(__file__)
LOGO_PATH = os.path.join(base_dir, "assets", "logo.png")
if not os.path.exists(LOGO_PATH):
    print(f"Warning: Logo not found at {LOGO_PATH}")

# کلید ذخیره در client_storage
STORAGE_USER_KEY = "idelingo_user"

class IDELingoApp:
    def __init__(self):
        self.user_manager = None
        self.current_user = None
        self.page = None
        self.current_index = 0
        self.offline_dict = None
        self.refresh_grammar_callback = None

    def init_backend(self):
        try:
            self.user_manager = UserManager()
            self.offline_dict = OfflineDictionary()
            return True
        except Exception as e:
            print(f"Error: {e}")
            return False

    def main(self, page: ft.Page):
        self.page = page

        page.title = "IDELingo"
        page.theme_mode = ft.ThemeMode.DARK
        page.padding = 0
        page.window_width = 400
        page.window_height = 780
        page.window_resizable = False
        page.bgcolor = COLORS['bg']
        page.theme = ft.Theme(color_scheme_seed=COLORS['accent'], use_material3=True)

        # اپ بار: فقط لوگو با سایز بزرگتر (متن حذف شد)
        if os.path.exists(LOGO_PATH):
            try:
                page.appbar = ft.AppBar(
                    title=ft.Image(src=LOGO_PATH, width=50, height=50, fit=ft.ImageFit.CONTAIN),
                    center_title=True,
                    bgcolor=COLORS['sidebar'],
                    actions=[
                        ft.IconButton(icon=ft.icons.PERSON, icon_color=COLORS['text_secondary'], on_click=self.show_profile)
                    ]
                )
            except:
                page.appbar = ft.AppBar(
                    title=ft.Text("IDELingo", size=20, weight=ft.FontWeight.BOLD, color=COLORS['accent']),
                    center_title=True,
                    bgcolor=COLORS['sidebar'],
                    actions=[
                        ft.IconButton(icon=ft.icons.PERSON, icon_color=COLORS['text_secondary'], on_click=self.show_profile)
                    ]
                )
        else:
            page.appbar = ft.AppBar(
                title=ft.Text("IDELingo", size=20, weight=ft.FontWeight.BOLD, color=COLORS['accent']),
                center_title=True,
                bgcolor=COLORS['sidebar'],
                actions=[
                    ft.IconButton(icon=ft.icons.PERSON, icon_color=COLORS['text_secondary'], on_click=self.show_profile)
                ]
            )

        if self.init_backend():
            # بررسی لاگین خودکار
            self.auto_login()
        else:
            self.show_error_page()

    def auto_login(self):
        """تلاش برای لاگین خودکار با استفاده از اطلاعات ذخیره شده"""
        try:
            user_data = self.page.client_storage.get(STORAGE_USER_KEY)
            if user_data and isinstance(user_data, dict):
                # اطلاعات ذخیره شده شامل id و username است (برای امنیت بیشتر می‌توان توکن ذخیره کرد)
                user_id = user_data.get("id")
                username = user_data.get("username")
                if user_id and username:
                    # لاگین خودکار با فراخوانی متد login با استفاده از username (بدون پسورد)
                    # لازم است متد login را طوری تغییر دهیم که با id هم کار کند. برای سادگی از یک متد خاص استفاده می‌کنیم.
                    # اما UserManager ما متد login را با username و password دارد. می‌توانیم یک متد auto_login در UserManager اضافه کنیم.
                    # به دلیل عدم دسترسی به UserManager در این مرحله، راه‌حل ساده: ذخیره پسورد هش شده؟ نه.
                    # بهترین راه: ایجاد یک متد جدید در UserManager به نام login_by_id که فقط id را بگیرد.
                    # چون دسترسی به تغییر UserManager داریم (قبلاً اصلاح شد)، متد زیر را اضافه می‌کنیم:
                    success = self.user_manager.login_by_id(user_id)
                    if success:
                        self.current_user = self.user_manager.current_user
                        self.show_dashboard()
                        return
        except Exception as e:
            print("Auto login failed:", e)
        # در غیر این صورت صفحه لاگین را نشان بده
        self.show_login()

    def _close_dialog(self, dialog):
        if dialog:
            dialog.open = False
            self.page.update()

    def show_error_page(self):
        self.page.clean()
        self.page.add(
            ft.Container(
                content=ft.Column([
                    ft.Icon(ft.icons.ERROR_OUTLINE, size=80, color=COLORS['danger']),
                    ft.Text("Error", size=28, weight=ft.FontWeight.BOLD, color=COLORS['danger']),
                    ft.Text("Failed to initialize backend", size=16, color=COLORS['text_secondary']),
                    ft.ElevatedButton("Retry", on_click=lambda e: self.init_backend() and self.auto_login(), bgcolor=COLORS['accent'])
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=20),
                alignment=ft.alignment.center, expand=True
            )
        )
        self.page.update()

    def show_login(self):
        self.page.clean()

        # لوگو در صفحه ورود (سایز بزرگ)
        logo_container = ft.Container()
        if os.path.exists(LOGO_PATH):
            try:
                logo_container = ft.Container(
                    content=ft.Image(src=LOGO_PATH, width=200, height=200, fit=ft.ImageFit.CONTAIN),
                    margin=ft.margin.only(top=30, bottom=10)
                )
            except:
                logo_container = ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.icons.SCHOOL, size=80, color=COLORS['accent']),
                        ft.Text("IDELingo", size=32, weight=ft.FontWeight.BOLD, color=COLORS['accent']),
                        ft.Text("Learn English Smarter", size=14, color=COLORS['text_secondary'])
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10),
                    margin=ft.margin.only(top=50, bottom=30)
                )
        else:
            logo_container = ft.Container(
                content=ft.Column([
                    ft.Icon(ft.icons.SCHOOL, size=80, color=COLORS['accent']),
                    ft.Text("IDELingo", size=32, weight=ft.FontWeight.BOLD, color=COLORS['accent']),
                    ft.Text("Learn English Smarter", size=14, color=COLORS['text_secondary'])
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10),
                margin=ft.margin.only(top=50, bottom=30)
            )

        username_field = ft.TextField(
            label="Username or Email", prefix_icon=ft.icons.PERSON,
            border_color=COLORS['text_muted'], focused_border_color=COLORS['accent'],
            color=COLORS['text'], width=300, height=50
        )
        password_field = ft.TextField(
            label="Password", prefix_icon=ft.icons.LOCK, password=True, can_reveal_password=True,
            border_color=COLORS['text_muted'], focused_border_color=COLORS['accent'],
            color=COLORS['text'], width=300, height=50
        )
        error_text = ft.Text("", color=COLORS['danger'], size=14, visible=False)

        def do_login(e):
            if not username_field.value or not password_field.value:
                error_text.value = "Please fill all fields"
                error_text.visible = True
                self.page.update()
                return
            success, msg, user = self.user_manager.login(username_field.value, password_field.value)
            if success:
                self.current_user = user
                # ذخیره اطلاعات کاربر برای لاگین خودکار
                self.page.client_storage.set(STORAGE_USER_KEY, {"id": user["id"], "username": user["username"]})
                self.show_dashboard()
            else:
                error_text.value = msg
                error_text.visible = True
                self.page.update()

        def show_register(e):
            self.show_register()

        self.page.add(
            ft.Container(
                content=ft.Column([
                    logo_container,
                    ft.Container(
                        content=ft.Column([
                            username_field, password_field, error_text,
                            ft.ElevatedButton("Login", on_click=do_login, bgcolor=COLORS['accent'], color=COLORS['bg'], width=300, height=45),
                            ft.TextButton("Create New Account", on_click=show_register, style=ft.ButtonStyle(color=COLORS['accent']))
                        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=15),
                        alignment=ft.alignment.center
                    )
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=20, scroll=ft.ScrollMode.AUTO),
                expand=True
            )
        )
        self.page.update()

    def show_register(self):
        self.page.clean()

        # لوگو در صفحه ثبت نام
        logo_container = ft.Container()
        if os.path.exists(LOGO_PATH):
            try:
                logo_container = ft.Container(
                    content=ft.Image(src=LOGO_PATH, width=100, height=100, fit=ft.ImageFit.CONTAIN),
                    margin=ft.margin.only(top=20, bottom=10)
                )
            except:
                logo_container = ft.Container(
                    content=ft.Text("IDELingo", size=28, weight=ft.FontWeight.BOLD, color=COLORS['accent']),
                    margin=ft.margin.only(top=30, bottom=20)
                )
        else:
            logo_container = ft.Container(
                content=ft.Text("IDELingo", size=28, weight=ft.FontWeight.BOLD, color=COLORS['accent']),
                margin=ft.margin.only(top=30, bottom=20)
            )

        username_field = ft.TextField(label="Username", prefix_icon=ft.icons.PERSON, color=COLORS['text'], width=300, height=50)
        email_field = ft.TextField(label="Email", prefix_icon=ft.icons.EMAIL, color=COLORS['text'], width=300, height=50)
        password_field = ft.TextField(label="Password (min 6 chars)", prefix_icon=ft.icons.LOCK, password=True, can_reveal_password=True, color=COLORS['text'], width=300, height=50)
        error_text = ft.Text("", color=COLORS['danger'], size=14, visible=False)

        def do_register(e):
            if not username_field.value or not email_field.value or not password_field.value:
                error_text.value = "Please fill all fields"
                error_text.visible = True
                self.page.update()
                return
            if len(password_field.value) < 6:
                error_text.value = "Password must be at least 6 characters"
                error_text.visible = True
                self.page.update()
                return
            success, msg = self.user_manager.register(username_field.value, email_field.value, password_field.value)
            if success:
                self.page.snack_bar = ft.SnackBar(content=ft.Text("Registration successful! Please login."), bgcolor=COLORS['success'])
                self.page.snack_bar.open = True
                self.page.update()
                self.show_login()
            else:
                error_text.value = msg
                error_text.visible = True
                self.page.update()

        self.page.add(
            ft.Container(
                content=ft.Column([
                    logo_container,
                    ft.Container(
                        content=ft.Column([
                            username_field, email_field, password_field, error_text,
                            ft.ElevatedButton("Sign Up", on_click=do_register, bgcolor=COLORS['success'], color=COLORS['bg'], width=300, height=45),
                            ft.TextButton("Back to Login", on_click=lambda e: self.show_login(), style=ft.ButtonStyle(color=COLORS['accent']))
                        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=15),
                        alignment=ft.alignment.center
                    )
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=20),
                expand=True
            )
        )
        self.page.update()

    def show_dashboard(self):
        self.page.clean()
        self.current_index = 0

        progress = self.user_manager.get_daily_progress(self.current_user['id'])
        hour = datetime.now().hour
        greeting = "Good Evening" if hour > 18 else "Good Afternoon" if hour > 12 else "Good Morning"

        # تعداد عبارات برای آیکون Phrases
        phrases_count = self.user_manager.db.cursor.execute("SELECT COUNT(*) FROM phrases WHERE user_id = ?", (self.current_user['id'],)).fetchone()[0]

        # کارت‌ها (با قابلیت کلیک)
        def navigate_to_words(e):
            self.nav_change(1)
        def navigate_to_grammar(e):
            self.nav_change(2)
        def navigate_to_phrases(e):
            self.nav_change(4)
        def navigate_to_streak(e):
            self.nav_change(7)  # settings -> learning plan

        stats = ft.Column(spacing=10)
        row1 = ft.Row([
            self._stat_card("📚", f"{progress['words_learned']}", f"/{self.current_user['daily_goal']}", "Words Today", navigate_to_words),
            self._stat_card("📖", f"{progress['grammar_learned']}", "", "Grammar Today", navigate_to_grammar),
            self._stat_card("💬", f"{phrases_count}", "", "Phrases", navigate_to_phrases),
        ], alignment=ft.MainAxisAlignment.SPACE_EVENLY, spacing=5)
        row2 = ft.Row([
            self._stat_card("🔥", f"{self.current_user['current_streak']}", "days", "Streak", navigate_to_streak),
            self._stat_card("🎯", "✅" if progress['goal_achieved'] else "⏳", "", "Daily Goal", None),
            self._stat_card("🏆", f"{self.current_user['level']}", "", "Level", None),
        ], alignment=ft.MainAxisAlignment.SPACE_EVENLY, spacing=5)
        stats.controls.extend([row1, row2])

        quick_add = self._quick_add_section()
        nav_bar = self._bottom_nav_bar()

        self.page.add(
            ft.Column([
                ft.Container(
                    content=ft.Column([
                        ft.Text(f"{greeting}, {self.current_user['username']}! 👋", size=22, weight=ft.FontWeight.BOLD, color=COLORS['text']),
                        ft.Text(datetime.now().strftime("%A, %B %d, %Y"), size=12, color=COLORS['text_secondary']),
                    ], spacing=5),
                    padding=ft.padding.all(20)
                ),
                ft.Container(content=stats, padding=ft.padding.symmetric(horizontal=20)),
                quick_add,
                ft.Container(expand=True),
                nav_bar
            ], spacing=10, expand=True)
        )
        self.page.update()

    def _stat_card(self, icon, value, subtitle, label, on_click=None):
        card = ft.Container(
            content=ft.Column([
                ft.Text(icon, size=24),
                ft.Text(value, size=18, weight=ft.FontWeight.BOLD, color=COLORS['accent']),
                ft.Text(subtitle, size=10, color=COLORS['text_muted']) if subtitle else ft.Container(),
                ft.Text(label, size=10, color=COLORS['text_secondary'])
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=3),
            bgcolor=COLORS['card'], border_radius=10, padding=ft.padding.all(8), width=110, height=100
        )
        if on_click:
            card.on_click = on_click
        return card

    def _quick_add_section(self):
        word_field = ft.TextField(hint_text="Word", border_color=COLORS['text_muted'], focused_border_color=COLORS['accent'], color=COLORS['text'], expand=True, height=45)
        meaning_field = ft.TextField(hint_text="Meaning", border_color=COLORS['text_muted'], focused_border_color=COLORS['accent'], color=COLORS['text'], expand=True, height=45)
        # حذف dropdown زبان

        def add_word(e):
            if not word_field.value:
                self.page.snack_bar = ft.SnackBar(content=ft.Text("❌ Please enter a word!"), bgcolor=COLORS['danger'])
                self.page.snack_bar.open = True
                self.page.update()
                return
            if not meaning_field.value:
                self.page.snack_bar = ft.SnackBar(content=ft.Text("❌ Please enter a meaning!"), bgcolor=COLORS['danger'])
                self.page.snack_bar.open = True
                self.page.update()
                return

            self.user_manager.add_vocabulary(self.current_user['id'], word_field.value, meaning_field.value, "", "English", "medium", "", "")
            # XP حذف شد
            word_field.value = ""
            meaning_field.value = ""
            self.page.snack_bar = ft.SnackBar(content=ft.Text("✅ Word added!"), bgcolor=COLORS['success'])
            self.page.snack_bar.open = True
            self.page.update()
            self.show_dashboard()

        return ft.Container(
            content=ft.Column([
                ft.Text("➕ Quick Add Word", size=16, weight=ft.FontWeight.BOLD, color=COLORS['text']),
                ft.Row([word_field, meaning_field, ft.IconButton(icon=ft.icons.ADD_CIRCLE, icon_color=COLORS['success'], icon_size=40, on_click=add_word)], spacing=10)
            ], spacing=10),
            bgcolor=COLORS['card'], border_radius=12, padding=ft.padding.all(15), margin=ft.margin.symmetric(horizontal=20)
        )

    def _bottom_nav_bar(self):
        items = [
            (ft.icons.HOME, "Home", 0),
            (ft.icons.BOOK, "Words", 1),
            (ft.icons.MENU_BOOK, "Grammar", 2),
            (ft.icons.CHAT, "Practice", 3),
            (ft.icons.FORMAT_QUOTE, "Phrases", 4),
            (ft.icons.PEOPLE, "Community", 5),
            (ft.icons.EMOJI_EVENTS, "Leaderboard", 6),
            (ft.icons.SETTINGS, "Settings", 7),
        ]
        return ft.Container(
            content=ft.Row([self._nav_button(icon, label, idx) for icon, label, idx in items], alignment=ft.MainAxisAlignment.SPACE_AROUND),
            bgcolor=COLORS['sidebar'], padding=ft.padding.symmetric(vertical=8), border_radius=ft.border_radius.only(top_left=15, top_right=15)
        )

    def _nav_button(self, icon, label, index):
        is_selected = (self.current_index == index)
        return ft.IconButton(
            icon=icon,
            icon_size=24,
            icon_color=COLORS['accent'] if is_selected else COLORS['text_muted'],
            on_click=lambda e, i=index: self.nav_change(i),
            tooltip=label
        )

    def show_vocabulary(self):
        self.page.clean()
        self.current_index = 1

        # هدر جدید: عنوان + آیکون سرچ در راست
        header_frame = ft.Container(
            content=ft.Row([
                ft.Text("📝 Vocabulary Manager", size=24, weight=ft.FontWeight.BOLD, color=COLORS['accent'], expand=True),
                ft.IconButton(icon=ft.icons.SEARCH, icon_color=COLORS['accent'], icon_size=24,
                              on_click=lambda e: self.show_search_dialog("vocabulary"))
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            padding=ft.padding.all(20)
        )
        # دکمه Add New Word بزرگ
        add_button = ft.ElevatedButton(
            content=ft.Row([ft.Icon(ft.icons.ADD), ft.Text("Add New Word")], spacing=10),
            on_click=lambda e: self.add_vocabulary_dialog(),
            bgcolor=COLORS['success'], color=COLORS['bg'], style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10))
        )
        # فیلتر زبان و سختی (نگه داشته می‌شود)
        self.vocab_lang_filter = ft.Dropdown(
            options=[ft.dropdown.Option("All"), ft.dropdown.Option("English"), ft.dropdown.Option("Spanish"),
                     ft.dropdown.Option("French"), ft.dropdown.Option("German"), ft.dropdown.Option("Japanese")],
            value="All", width=100, height=40, bgcolor=COLORS['bg'], color=COLORS['text']
        )
        self.vocab_diff_filter = ft.Dropdown(
            options=[ft.dropdown.Option("All"), ft.dropdown.Option("easy"), ft.dropdown.Option("medium"), ft.dropdown.Option("hard")],
            value="All", width=80, height=40, bgcolor=COLORS['bg'], color=COLORS['text']
        )
        filter_frame = ft.Container(
            content=ft.Row([self.vocab_lang_filter, self.vocab_diff_filter], spacing=10),
            padding=ft.padding.symmetric(horizontal=20, vertical=10)
        )
        self.vocab_lang_filter.on_change = self.refresh_vocabulary_list
        self.vocab_diff_filter.on_change = self.refresh_vocabulary_list

        self.vocab_list_container = ft.Column(spacing=10, scroll=ft.ScrollMode.AUTO, expand=True)
        nav_bar = self._bottom_nav_bar()

        self.page.add(
            ft.Column([
                header_frame,
                ft.Container(content=add_button, padding=ft.padding.symmetric(horizontal=20)),
                filter_frame,
                ft.Container(content=self.vocab_list_container, expand=True, padding=ft.padding.symmetric(horizontal=20)),
                nav_bar
            ], spacing=10, expand=True)
        )
        self.refresh_vocabulary_list(None)

    def show_search_dialog(self, target):
        search_field = ft.TextField(hint_text="Search...", width=300)
        result_text = ft.Text("", size=14)
        def do_search(e):
            query = search_field.value
            if not query:
                return
            if target == "vocabulary":
                words = self.user_manager.get_vocabulary(self.current_user['id'], {'search': query})
                if words:
                    result_text.value = f"🔍 Found {len(words)} words containing '{query}'"
                else:
                    result_text.value = f"❌ No words found for '{query}'"
            elif target == "phrases":
                phrases = self.user_manager.get_phrases(self.current_user['id'], query)
                if phrases:
                    result_text.value = f"🔍 Found {len(phrases)} phrases containing '{query}'"
                else:
                    result_text.value = f"❌ No phrases found for '{query}'"
            result_text.update()
        dialog = ft.AlertDialog(
            title=ft.Text(f"Search {target.capitalize()}"),
            content=ft.Column([search_field, result_text], spacing=10),
            actions=[ft.TextButton("Search", on_click=do_search), ft.TextButton("Close", on_click=lambda e: self._close_dialog(dialog))]
        )
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()

    def refresh_vocabulary_list(self, e):
        if not self.vocab_list_container:
            return
        self.vocab_list_container.controls.clear()
        filters = {
            'language': self.vocab_lang_filter.value if self.vocab_lang_filter.value != "All" else None,
            'difficulty': self.vocab_diff_filter.value if self.vocab_diff_filter.value != "All" else None
        }
        filters = {k: v for k, v in filters.items() if v}
        words = self.user_manager.get_vocabulary(self.current_user['id'], filters)
        if not words:
            self.vocab_list_container.controls.append(ft.Container(content=ft.Text("No words yet. Add your first word!", color=COLORS['text_secondary']), padding=ft.padding.all(40)))
        else:
            for word in words[:20]:
                actual_meaning = word[3]
                meaning_display = ft.Text("❓", size=14, color=COLORS['text_secondary'])
                def make_toggle(m, d):
                    return lambda e: self._toggle_meaning(d, m)
                diff_icon = "🟢" if word[6] == "easy" else "🟡" if word[6] == "medium" else "🔴"
                word_card = ft.Container(
                    content=ft.Row([
                        ft.Column([
                            ft.Row([
                                ft.Text(word[2], size=16, weight=ft.FontWeight.BOLD, color=COLORS['accent']),
                                ft.Text(diff_icon, size=12),
                            ], spacing=5),
                            ft.GestureDetector(
                                content=meaning_display,
                                on_tap=make_toggle(actual_meaning, meaning_display)
                            ),
                        ], spacing=3, expand=True),
                        ft.Column([
                            ft.Text(f"🌐 {word[5]}", size=11, color=COLORS['text_muted']),
                            ft.Row([
                                ft.IconButton(icon=ft.icons.EDIT, icon_size=18, icon_color=COLORS['info'], on_click=lambda e, w=word: self.edit_vocabulary_word(w)),
                                ft.IconButton(icon=ft.icons.DELETE, icon_size=18, icon_color=COLORS['danger'], on_click=lambda e, wid=word[0]: self.delete_word(wid)),
                            ], spacing=0)
                        ], horizontal_alignment=ft.CrossAxisAlignment.END, spacing=3),
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    bgcolor=COLORS['card'], border_radius=10, padding=ft.padding.all(12)
                )
                self.vocab_list_container.controls.append(word_card)
        self.page.update()

    def _toggle_meaning(self, text_widget, meaning):
        if text_widget.value == "❓":
            text_widget.value = meaning[:50] + ("..." if len(meaning) > 50 else "")
            text_widget.color = COLORS['text']
        else:
            text_widget.value = "❓"
            text_widget.color = COLORS['text_secondary']
        text_widget.update()

    def edit_vocabulary_word(self, word_data):
        self.page.snack_bar = ft.SnackBar(content=ft.Text(f"Edit: {word_data[2]}"), bgcolor=COLORS['info'])
        self.page.snack_bar.open = True
        self.page.update()

    def delete_word(self, word_id):
        def confirm(e):
            confirm_dialog.open = False
            self.user_manager.delete_vocabulary(word_id)
            self.refresh_vocabulary_list(None)
            self.page.snack_bar = ft.SnackBar(content=ft.Text("✅ Word deleted!"), bgcolor=COLORS['success'])
            self.page.snack_bar.open = True
            self.page.update()
        confirm_dialog = ft.AlertDialog(
            title=ft.Text("Delete Word", color=COLORS['warning']),
            content=ft.Text("Are you sure you want to delete this word?"),
            actions=[
                ft.TextButton("Cancel", on_click=lambda e: self._close_dialog(confirm_dialog)),
                ft.ElevatedButton("Delete", on_click=confirm, bgcolor=COLORS['danger'])
            ]
        )
        self.page.dialog = confirm_dialog
        confirm_dialog.open = True
        self.page.update()

    def add_vocabulary_dialog(self):
        word_field = ft.TextField(label="Word", width=300)
        meaning_field = ft.TextField(label="Meaning", width=300, multiline=True, min_lines=2, max_lines=3)
        example_field = ft.TextField(label="Example (optional)", width=300)
        # حذف dropdown زبان و سختی (سختی را پیش‌فرض medium قرار می‌دهیم)
        diff_dropdown = ft.Dropdown(options=[ft.dropdown.Option("easy"), ft.dropdown.Option("medium"), ft.dropdown.Option("hard")], value="medium", width=300)
        dict_result = ft.Text("", size=12, color=COLORS['text_secondary'])
        def search_dict(e):
            if word_field.value:
                result = self.offline_dict.get_meaning_with_pronunciation(word_field.value)
                dict_result.value = result[:300] + ("..." if len(result) > 300 else "")
                dict_result.update()
        def save_word(e):
            if not word_field.value:
                self.page.snack_bar = ft.SnackBar(content=ft.Text("❌ Please enter a word!"), bgcolor=COLORS['danger'])
                self.page.snack_bar.open = True
                self.page.update()
                return
            if not meaning_field.value:
                self.page.snack_bar = ft.SnackBar(content=ft.Text("❌ Please enter a meaning!"), bgcolor=COLORS['danger'])
                self.page.snack_bar.open = True
                self.page.update()
                return
            self.user_manager.add_vocabulary(self.current_user['id'], word_field.value, meaning_field.value,
                                              example_field.value or "", "English", diff_dropdown.value, "", "")
            self._close_dialog(dialog)
            self.refresh_vocabulary_list(None)
            self.page.snack_bar = ft.SnackBar(content=ft.Text(f"✅ '{word_field.value}' added!"), bgcolor=COLORS['success'])
            self.page.snack_bar.open = True
            self.page.update()
        dialog = ft.AlertDialog(
            title=ft.Text("Add New Word", color=COLORS['accent']),
            content=ft.Container(
                content=ft.Column([
                    word_field, meaning_field, example_field, diff_dropdown,
                    ft.ElevatedButton("🔍 Search in Dictionary", on_click=search_dict, bgcolor=COLORS['info']),
                    dict_result
                ], spacing=15, scroll=ft.ScrollMode.AUTO),
                padding=20, width=380, height=550
            ),
            actions=[
                ft.TextButton("Cancel", on_click=lambda e: self._close_dialog(dialog)),
                ft.ElevatedButton("Save", on_click=save_word, bgcolor=COLORS['success'])
            ]
        )
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()

    def show_grammar(self):
        self.page.clean()
        self.current_index = 2

        # ابتدا فقط favorites را نمایش می‌دهیم
        self.grammar_fav_only = True  # حالت نمایش فقط favorites
        self.grammar_search_field = ft.TextField(hint_text="Search grammar rules...", prefix_icon=ft.icons.SEARCH, expand=True, height=45,
                                   border_color=COLORS['text_muted'], focused_border_color=COLORS['accent'], color=COLORS['text'])
        self.grammar_content = ft.Column(spacing=8, scroll=ft.ScrollMode.AUTO, expand=True)

        def filter_grammar(e=None):
            query = self.grammar_search_field.value.lower() if self.grammar_search_field.value else ""
            self.grammar_content.controls.clear()
            if query:
                # جستجو در کل قوانین
                topics = self.user_manager.get_all_grammar_topics()
                filtered = [t for t in topics if query in t.lower()]
            else:
                if self.grammar_fav_only:
                    # فقط favorites
                    favs = self.user_manager.get_grammar_favorites()
                    filtered = [fav['key'] for fav in favs]
                else:
                    filtered = self.user_manager.get_all_grammar_topics()
            for topic in filtered[:30]:
                info = self.user_manager.get_grammar_info(topic)
                title = info.get('title', topic.replace('_', ' ').title()) if info else topic.replace('_', ' ').title()
                level = info.get('level', 'beginner') if info else 'beginner'
                level_icon = "🔰" if level == 'beginner' else "📘" if level == 'intermediate' else "🎓"
                is_fav = self.user_manager.is_grammar_favorite(topic)
                fav_icon = "❤️" if is_fav else "🤍"
                btn = ft.Container(
                    content=ft.Row([
                        ft.Text(f"{level_icon} {fav_icon}", size=14),
                        ft.Text(title, size=14, color=COLORS['text'], expand=True),
                        ft.Icon(ft.icons.CHEVRON_RIGHT, color=COLORS['text_muted'], size=18)
                    ]),
                    bgcolor=COLORS['card'], border_radius=8, padding=ft.padding.all(12),
                    on_click=lambda e, t=topic: self.open_grammar_topic(t, filter_grammar)
                )
                self.grammar_content.controls.append(btn)
            if not filtered:
                self.grammar_content.controls.append(ft.Container(content=ft.Text("No grammar rules found.", color=COLORS['text_secondary']), padding=ft.padding.all(40)))
            self.page.update()

        self.grammar_search_field.on_change = filter_grammar
        # دکمه تغییر حالت نمایش (نمایش همه / فقط favorites)
        toggle_button = ft.ToggleButton(
            icon=ft.icons.FAVORITE,
            selected=False,
            on_change=lambda e: self.toggle_grammar_display(filter_grammar)
        )
        header_row = ft.Row([
            ft.Text("📖 Grammar Library", size=24, weight=ft.FontWeight.BOLD, color=COLORS['accent'], expand=True),
            toggle_button
        ])
        nav_bar = self._bottom_nav_bar()

        self.page.add(
            ft.Column([
                ft.Container(content=header_row, padding=ft.padding.all(20)),
                ft.Container(content=ft.Text(f"📚 Total Rules: {len(self.user_manager.get_all_grammar_topics())}", size=13, color=COLORS['text_secondary']), padding=ft.padding.symmetric(horizontal=20)),
                ft.Container(content=self.grammar_search_field, padding=ft.padding.all(20)),
                ft.Container(content=self.grammar_content, expand=True, padding=ft.padding.symmetric(horizontal=20)),
                nav_bar
            ], spacing=10, expand=True)
        )
        filter_grammar(None)

    def toggle_grammar_display(self, callback):
        self.grammar_fav_only = not self.grammar_fav_only
        callback()

    def open_grammar_topic(self, topic_key, refresh_callback=None):
        info = self.user_manager.get_grammar_info(topic_key)
        if not info:
            return

        level_icon = "🔰" if info.get('level') == 'beginner' else "📘" if info.get('level') == 'intermediate' else "🎓"
        is_fav = self.user_manager.is_grammar_favorite(topic_key)

        notes = self.user_manager.get_grammar_notes(topic_key)
        notes_column = ft.Column(spacing=10)

        def rebuild_notes():
            notes_column.controls.clear()
            for idx, note in enumerate(notes):
                # هر یادداشت در یک کارت با قابلیت ویرایش
                note_text = note['note']
                timestamp = note['timestamp']
                edit_field = ft.TextField(value=note_text, multiline=True, min_lines=2, visible=False)
                display_text = ft.Text(note_text, size=12, color=COLORS['text_secondary'])
                def save_edit(note_idx, old_note, field, display, card):
                    new_text = field.value
                    if new_text != old_note['note']:
                        # حذف یادداشت قدیمی و اضافه جدید (ساده‌ترین راه)
                        self.user_manager.get_grammar_notes(topic_key).remove(old_note)
                        self.user_manager.save_grammar_note(topic_key, new_text)
                        # به‌روزرسانی لیست notes
                        nonlocal notes
                        notes = self.user_manager.get_grammar_notes(topic_key)
                        rebuild_notes()
                        dialog.update()
                        self.page.snack_bar = ft.SnackBar(content=ft.Text("Note updated!"), bgcolor=COLORS['success'])
                        self.page.snack_bar.open = True
                        self.page.update()
                    field.visible = False
                    display.visible = True
                    card.update()
                def edit_mode(field, display, card):
                    field.visible = True
                    display.visible = False
                    card.update()
                card = ft.Card(
                    content=ft.Column([
                        ft.Text(timestamp, size=10, color=COLORS['text_muted']),
                        display_text,
                        edit_field,
                        ft.Row([
                            ft.TextButton("Edit", on_click=lambda e: edit_mode(edit_field, display_text, card)),
                            ft.TextButton("Save", on_click=lambda e: save_edit(idx, note, edit_field, display_text, card))
                        ], alignment=ft.MainAxisAlignment.END)
                    ], spacing=5),
                    margin=ft.margin.all(5)
                )
                notes_column.controls.append(card)
        rebuild_notes()

        note_field = ft.TextField(hint_text="Write a new note...", multiline=True, min_lines=2, max_lines=3, width=300)
        def add_note(e):
            if note_field.value:
                self.user_manager.save_grammar_note(topic_key, note_field.value)
                note_field.value = ""
                nonlocal notes
                notes = self.user_manager.get_grammar_notes(topic_key)
                rebuild_notes()
                dialog.update()
                self.page.snack_bar = ft.SnackBar(content=ft.Text("✅ Note added!"), bgcolor=COLORS['success'])
                self.page.snack_bar.open = True
                self.page.update()

        def toggle_favorite(e):
            nonlocal is_fav
            if is_fav:
                self.user_manager.remove_grammar_favorite(topic_key)
                is_fav = False
                fav_btn.icon = ft.icons.FAVORITE_BORDER
                fav_btn.icon_color = COLORS['text_secondary']
            else:
                self.user_manager.add_grammar_favorite(topic_key)
                is_fav = True
                fav_btn.icon = ft.icons.FAVORITE
                fav_btn.icon_color = COLORS['danger']
            dialog.update()
            if refresh_callback:
                refresh_callback()

        fav_btn = ft.IconButton(
            icon=ft.icons.FAVORITE if is_fav else ft.icons.FAVORITE_BORDER,
            icon_color=COLORS['danger'] if is_fav else COLORS['text_secondary'],
            on_click=toggle_favorite
        )

        content = ft.Column([
            ft.Text("📐 Structure", weight=ft.FontWeight.BOLD, color=COLORS['accent']),
            ft.Text(info.get('structure', ''), size=13, color=COLORS['text_secondary']),
            ft.Divider(),
            ft.Text("📝 Examples", weight=ft.FontWeight.BOLD, color=COLORS['accent']),
        ] + [ft.Text(f"• {ex}", size=13, color=COLORS['text_secondary']) for ex in info.get('example', ['No examples'])[:3]] + [
            ft.Divider(),
            ft.Text("🎯 Key Usages", weight=ft.FontWeight.BOLD, color=COLORS['accent']),
        ] + [ft.Text(f"• {u}", size=13, color=COLORS['text_secondary']) for u in info.get('usage', ['No usage'])[:3]] + [
            ft.Divider(),
            ft.Text("⚠️ Common Mistakes", weight=ft.FontWeight.BOLD, color=COLORS['warning']),
        ] + [ft.Text(f"• {m}", size=12, color=COLORS['text_secondary']) for m in info.get('common_mistakes', [])[:2]] + [
            ft.Divider(),
            ft.Text("📓 My Notes", weight=ft.FontWeight.BOLD, color=COLORS['accent']),
            notes_column,
            note_field,
            ft.ElevatedButton("➕ Add Note", on_click=add_note, bgcolor=COLORS['success'])
        ], spacing=10, scroll=ft.ScrollMode.AUTO)

        dialog = ft.AlertDialog(
            title=ft.Row([ft.Text(f"{level_icon} ", size=14), ft.Text(info.get('title', topic_key), color=COLORS['accent'], expand=True), fav_btn]),
            content=ft.Container(content=content, padding=15, width=400, height=550),
            actions=[ft.TextButton("Close", on_click=lambda e: self._close_dialog(dialog))]
        )
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()

    def show_practice(self):
        self.page.clean()
        self.current_index = 3

        text_input = ft.TextField(multiline=True, min_lines=4, max_lines=6, hint_text="Write a sentence in English...",
            border_color=COLORS['text_muted'], focused_border_color=COLORS['accent'], color=COLORS['text'], expand=True)
        result_text = ft.Text("", color=COLORS['text_secondary'], size=13)
        correction_var = ft.Checkbox(label="AI Auto-correct (spelling & grammar)", value=True, check_color=COLORS['accent'])

        def check_grammar(e):
            text = text_input.value
            if not text or not text.strip():
                result_text.value = "⚠️ Please write something to practice!"
                result_text.color = COLORS['warning']
                self.page.update()
                return

            if correction_var.value:
                corrected, feedback = self.user_manager.check_grammar_offline(text)
            else:
                corrected, feedback = text, "✅ Message saved (auto-correct disabled)"

            self.user_manager.save_practice_message(self.current_user['id'], text, corrected, feedback)
            # حذف XP
            # self.user_manager.add_xp(self.current_user['id'], 5)  # حذف شد

            if corrected != text:
                result_text.value = f"✨ Suggested: \"{corrected}\"\n\n💡 {feedback}"
                result_text.color = COLORS['warning']
            else:
                result_text.value = f"✅ {feedback}"
                result_text.color = COLORS['success']

            text_input.value = ""
            self.page.update()

        history = self.user_manager.get_practice_history(self.current_user['id'])
        history_col = ft.Column(spacing=8, scroll=ft.ScrollMode.AUTO)
        if history:
            history_col.controls.append(ft.Text("Recent Practice:", size=14, weight=ft.FontWeight.BOLD, color=COLORS['text']))
            for msg, corr, _, ts in history[:10]:
                time_str = ts[11:16] if len(ts) > 16 else ts
                history_col.controls.append(ft.Container(
                    content=ft.Column([
                        ft.Text(f"[{time_str}] You: {msg[:50]}...", size=11, color=COLORS['text_secondary']),
                        ft.Text(f"🤖 AI: {corr[:50]}...", size=11, color=COLORS['success'])
                    ], spacing=3),
                    bgcolor=COLORS['card'], border_radius=6, padding=ft.padding.all(8)
                ))

        nav_bar = self._bottom_nav_bar()

        self.page.add(
            ft.Column([
                ft.Container(content=ft.Text("💬 AI Writing Practice", size=22, weight=ft.FontWeight.BOLD, color=COLORS['accent']), padding=ft.padding.all(20)),
                ft.Container(content=ft.Text("Write sentences and get intelligent AI corrections! (100% offline)",
                                            size=12, color=COLORS['text_secondary'], text_align=ft.TextAlign.CENTER), padding=ft.padding.symmetric(horizontal=20)),
                ft.Container(content=ft.Column([
                    text_input,
                    correction_var,
                    ft.ElevatedButton("Check Grammar ✨", on_click=check_grammar, bgcolor=COLORS['success'], height=45),
                    ft.Divider(),
                    result_text,
                    ft.Divider(),
                    ft.Container(content=history_col, height=200)
                ], spacing=12), expand=True, padding=ft.padding.all(20)),
                nav_bar
            ], spacing=10, expand=True)
        )
        self.page.update()

    def show_phrases(self):
        self.page.clean()
        self.current_index = 4

        header_frame = ft.Container(
            content=ft.Row([
                ft.Text("💬 My Phrase Library", size=24, weight=ft.FontWeight.BOLD, color=COLORS['accent'], expand=True),
                ft.IconButton(icon=ft.icons.SEARCH, icon_color=COLORS['accent'], icon_size=24,
                              on_click=lambda e: self.show_search_dialog("phrases"))
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            padding=ft.padding.all(20)
        )
        add_button = ft.ElevatedButton(
            content=ft.Row([ft.Icon(ft.icons.ADD), ft.Text("Add New Phrase")], spacing=10),
            on_click=lambda e: self.add_phrase_dialog(),
            bgcolor=COLORS['success'], color=COLORS['bg'], style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10))
        )
        self.phrases_container = ft.Column(spacing=10, scroll=ft.ScrollMode.AUTO, expand=True)
        nav_bar = self._bottom_nav_bar()

        def refresh_phrases(e=None):
            self.phrases_container.controls.clear()
            phrases = self.user_manager.get_phrases(self.current_user['id'], None)
            if not phrases:
                self.phrases_container.controls.append(ft.Container(
                    content=ft.Text("No phrases yet. Click '+ Add Phrase' to start learning!", color=COLORS['text_secondary'], text_align=ft.TextAlign.CENTER),
                    padding=ft.padding.all(40)
                ))
            else:
                for idx, phrase in enumerate(phrases[:20], 1):
                    phrase_card = ft.Container(
                        content=ft.Column([
                            ft.Row([
                                ft.Text(f"{idx}.", size=12, color=COLORS['text_muted'], width=30),
                                ft.Text(phrase[2][:60], size=14, weight=ft.FontWeight.BOLD, color=COLORS['accent'], expand=True),
                            ]),
                            ft.Text(f"📖 {phrase[3][:80]}", size=12, color=COLORS['text_secondary']),
                            ft.Row([
                                ft.Text(f"🏷️ {phrase[4]}" if phrase[4] else "", size=10, color=COLORS['text_muted']),
                                ft.Text(f"📅 {phrase[6][:10]}" if phrase[6] else "", size=10, color=COLORS['text_muted']),
                                ft.IconButton(icon=ft.icons.DELETE, icon_size=18, icon_color=COLORS['danger'],
                                            on_click=lambda e, pid=phrase[0]: self.delete_phrase(pid))
                            ], spacing=10)
                        ], spacing=5),
                        bgcolor=COLORS['card'], border_radius=10, padding=ft.padding.all(12)
                    )
                    self.phrases_container.controls.append(phrase_card)
            self.page.update()

        self.page.add(
            ft.Column([
                header_frame,
                ft.Container(content=add_button, padding=ft.padding.symmetric(horizontal=20)),
                ft.Container(content=self.phrases_container, expand=True, padding=ft.padding.symmetric(horizontal=20)),
                nav_bar
            ], spacing=10, expand=True)
        )
        refresh_phrases(None)

    def add_phrase_dialog(self):
        phrase_field = ft.TextField(label="Phrase / Sentence *", multiline=True, min_lines=2, max_lines=4, width=350)
        meaning_field = ft.TextField(label="Translation / Meaning *", multiline=True, min_lines=2, max_lines=4, width=350)
        tags_field = ft.TextField(label="Tags (comma separated)", hint_text="e.g., greeting, travel, business", width=350)
        notes_field = ft.TextField(label="Notes (optional)", multiline=True, min_lines=2, max_lines=3, width=350)

        def save_phrase(e):
            phrase = phrase_field.value
            meaning = meaning_field.value
            if not phrase:
                self.page.snack_bar = ft.SnackBar(content=ft.Text("❌ Please enter a phrase!"), bgcolor=COLORS['danger'])
                self.page.snack_bar.open = True
                self.page.update()
                return
            if not meaning:
                self.page.snack_bar = ft.SnackBar(content=ft.Text("❌ Please enter a meaning!"), bgcolor=COLORS['danger'])
                self.page.snack_bar.open = True
                self.page.update()
                return

            self.user_manager.add_phrase(self.current_user['id'], phrase, meaning, tags_field.value or "", notes_field.value or "")
            self._close_dialog(dialog)
            self.show_phrases()
            self.page.snack_bar = ft.SnackBar(content=ft.Text("✅ Phrase added!"), bgcolor=COLORS['success'])
            self.page.snack_bar.open = True
            self.page.update()

        dialog = ft.AlertDialog(
            title=ft.Text("Add New Phrase", color=COLORS['accent']),
            content=ft.Container(
                content=ft.Column([
                    phrase_field, meaning_field, tags_field, notes_field
                ], spacing=15, scroll=ft.ScrollMode.AUTO),
                padding=20, width=400, height=500
            ),
            actions=[
                ft.TextButton("Cancel", on_click=lambda e: self._close_dialog(dialog)),
                ft.ElevatedButton("Save", on_click=save_phrase, bgcolor=COLORS['success'])
            ]
        )
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()

    def delete_phrase(self, phrase_id):
        def confirm(e):
            self._close_dialog(confirm_dialog)
            self.user_manager.delete_phrase(phrase_id)
            self.show_phrases()
            self.page.snack_bar = ft.SnackBar(content=ft.Text("✅ Phrase deleted!"), bgcolor=COLORS['success'])
            self.page.snack_bar.open = True
            self.page.update()

        confirm_dialog = ft.AlertDialog(
            title=ft.Text("Delete Phrase", color=COLORS['warning']),
            content=ft.Text("Are you sure you want to delete this phrase?"),
            actions=[
                ft.TextButton("Cancel", on_click=lambda e: self._close_dialog(confirm_dialog)),
                ft.ElevatedButton("Delete", on_click=confirm, bgcolor=COLORS['danger'])
            ]
        )
        self.page.dialog = confirm_dialog
        confirm_dialog.open = True
        self.page.update()

    def show_community(self):
        self.page.clean()
        self.current_index = 5

        search_field = ft.TextField(hint_text="Enter username...", prefix_icon=ft.icons.SEARCH, width=250, height=45,
                                   border_color=COLORS['text_muted'], focused_border_color=COLORS['accent'], color=COLORS['text'])
        results_container = ft.Column(spacing=10, scroll=ft.ScrollMode.AUTO, expand=True)

        def search_users(e):
            results_container.controls.clear()
            query = search_field.value
            if not query or len(query) < 2:
                results_container.controls.append(ft.Text("Enter at least 2 characters to search", color=COLORS['text_secondary']))
                self.page.update()
                return

            users = self.user_manager.search_users(query, self.current_user['id'])
            if not users:
                results_container.controls.append(ft.Text("No users found", color=COLORS['text_secondary']))
            else:
                for user in users:
                    user_card = ft.Container(
                        content=ft.Row([
                            ft.Text(user[2], size=32),
                            ft.Column([
                                ft.Text(user[1], size=14, weight=ft.FontWeight.BOLD, color=COLORS['text']),
                                ft.Text(f"Level {user[3]} • {user[4]} XP", size=11, color=COLORS['text_secondary'])
                            ], spacing=3, expand=True),
                            ft.ElevatedButton("View Profile", on_click=lambda e, uid=user[0]: self.view_user_profile(uid), bgcolor=COLORS['info'], height=35)
                        ]),
                        bgcolor=COLORS['card'], border_radius=10, padding=ft.padding.all(12)
                    )
                    results_container.controls.append(user_card)
            self.page.update()

        search_field.on_submit = search_users
        nav_bar = self._bottom_nav_bar()

        self.page.add(
            ft.Column([
                ft.Container(content=ft.Text("👥 Community", size=24, weight=ft.FontWeight.BOLD, color=COLORS['accent']), padding=ft.padding.all(20)),
                ft.Container(content=ft.Row([search_field, ft.ElevatedButton("Search", on_click=search_users, bgcolor=COLORS['accent'])], spacing=10), padding=ft.padding.symmetric(horizontal=20)),
                ft.Container(content=ft.Text("💡 Tip: Search for friends to see their progress!", size=12, color=COLORS['text_secondary']), padding=ft.padding.symmetric(horizontal=20)),
                ft.Container(content=results_container, expand=True, padding=ft.padding.all(20)),
                nav_bar
            ], spacing=10, expand=True)
        )
        self.page.update()

    def view_user_profile(self, target_id):
        profile, error = self.user_manager.get_user_public_profile(target_id)
        if error:
            self.page.snack_bar = ft.SnackBar(content=ft.Text(error), bgcolor=COLORS['danger'])
            self.page.snack_bar.open = True
            self.page.update()
            return

        dialog = ft.AlertDialog(
            title=ft.Text(f"{profile['username']}'s Profile", color=COLORS['accent']),
            content=ft.Container(
                content=ft.Column([
                    ft.Container(content=ft.Text(profile['avatar'], size=50), alignment=ft.alignment.center),
                    ft.Text(profile['username'], size=20, weight=ft.FontWeight.BOLD, color=COLORS['text'], text_align=ft.TextAlign.CENTER),
                    ft.Divider(),
                    ft.Row([
                        ft.Column([ft.Text("⭐ Level", size=12), ft.Text(str(profile['level']), size=18, weight=ft.FontWeight.BOLD, color=COLORS['accent'])], horizontal_alignment=ft.CrossAxisAlignment.CENTER, expand=True),
                        ft.Column([ft.Text("🔥 Streak", size=12), ft.Text(str(profile['streak']), size=18, weight=ft.FontWeight.BOLD, color=COLORS['warning'])], horizontal_alignment=ft.CrossAxisAlignment.CENTER, expand=True),
                    ]),
                    ft.Divider(),
                    ft.Text(f"📚 Today: {profile['today_words']} words", size=13),
                    ft.Text("✅ Goal achieved!" if profile['goal_achieved'] else "⏳ Goal in progress", size=13, color=COLORS['success'] if profile['goal_achieved'] else COLORS['warning'])
                ], spacing=10),
                padding=20, width=350
            ),
            actions=[ft.TextButton("Close", on_click=lambda e: self._close_dialog(dialog))]
        )
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()

    def show_leaderboard(self):
        self.page.clean()
        self.current_index = 6

        leaderboard = self.user_manager.get_leaderboard(50)
        leaderboard_col = ft.Column(spacing=8, scroll=ft.ScrollMode.AUTO)
        leaderboard_col.controls.append(
            ft.Container(
                content=ft.Row([
                    ft.Text("Rank", width=50, weight=ft.FontWeight.BOLD),
                    ft.Text("User", width=150, weight=ft.FontWeight.BOLD, expand=True),
                    ft.Text("Level", width=60, weight=ft.FontWeight.BOLD),
                    ft.Text("Today's Words", width=100, weight=ft.FontWeight.BOLD),
                ]),
                padding=ft.padding.all(10), bgcolor=COLORS['sidebar'], border_radius=8
            )
        )
        for i, (name, avatar, level, score) in enumerate(leaderboard, 1):
            medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
            is_current_user = (name == self.current_user['username'])
            leaderboard_col.controls.append(
                ft.Container(
                    content=ft.Row([
                        ft.Text(medal, width=50),
                        ft.Text(f"{avatar} {name}", width=150, expand=True, weight=ft.FontWeight.BOLD if is_current_user else None,
                               color=COLORS['accent'] if is_current_user else COLORS['text']),
                        ft.Text(f"Lv.{level}", width=60),
                        ft.Text(str(score), width=100, color=COLORS['success'] if i <= 3 else COLORS['text_secondary']),
                    ]),
                    bgcolor=COLORS['accent'] if is_current_user else COLORS['card'],
                    border_radius=8, padding=ft.padding.all(10)
                )
            )
        nav_bar = self._bottom_nav_bar()
        self.page.add(
            ft.Column([
                ft.Container(content=ft.Text("🏆 Leaderboard", size=24, weight=ft.FontWeight.BOLD, color=COLORS['accent']), padding=ft.padding.all(20)),
                ft.Container(content=ft.Text("Top learners today", size=13, color=COLORS['text_secondary']), padding=ft.padding.symmetric(horizontal=20)),
                ft.Container(content=leaderboard_col, expand=True, padding=ft.padding.all(20)),
                nav_bar
            ], spacing=10, expand=True)
        )
        self.page.update()

    def show_settings(self):
        self.page.clean()
        self.current_index = 7

        goal_dropdown = ft.Dropdown(label="Daily Learning Goal", options=[ft.dropdown.Option(str(i)) for i in [5,10,15,20,25,30]],
            value=str(self.current_user['daily_goal']), width=200, color=COLORS['text'])
        def update_goal(e):
            self.user_manager.update_profile(self.current_user['id'], daily_goal=int(goal_dropdown.value))
            self.current_user['daily_goal'] = int(goal_dropdown.value)
            self.page.snack_bar = ft.SnackBar(content=ft.Text("✅ Goal updated!"), bgcolor=COLORS['success'])
            self.page.snack_bar.open = True
            self.page.update()

        avatars = ["😊", "😎", "🤓", "👨‍🎓", "👩‍🎓", "🐱", "🐶", "🦊", "🐼", "⭐"]
        avatar_row = ft.Row([ft.Container(
            content=ft.Text(a, size=32),
            bgcolor=COLORS['card'] if a == self.current_user['avatar'] else COLORS['bg'],
            border_radius=10, padding=10,
            on_click=lambda e, av=a: self._update_avatar(av)
        ) for a in avatars], spacing=10, wrap=True)

        # Plan Tab
        user_plan = self.user_manager.get_user_plan(self.current_user['id'])
        plan_type_dropdown = ft.Dropdown(
            label="Plan Type",
            options=[ft.dropdown.Option("daily"), ft.dropdown.Option("weekly"), ft.dropdown.Option("monthly"), ft.dropdown.Option("custom")],
            value=user_plan.get('plan_type', 'daily'),
            width=200, color=COLORS['text']
        )
        goals_container = ft.Column(spacing=10)
        goal_entries = {}
        def update_plan_inputs(e):
            goals_container.controls.clear()
            plan_type = plan_type_dropdown.value
            goal_entries.clear()
            if plan_type == 'weekly':
                goals = [("📚 Words per week", "weekly_goal_words", user_plan.get('weekly_goal_words', 20)),
                         ("📖 Grammar rules per week", "weekly_goal_grammar", user_plan.get('weekly_goal_grammar', 5)),
                         ("💬 Phrases per week", "weekly_goal_phrases", user_plan.get('weekly_goal_phrases', 10))]
                for label, key, default in goals:
                    row = ft.Row([
                        ft.Text(label, width=180, color=COLORS['text_secondary']),
                        ft.TextField(value=str(default), width=100, height=40, text_align=ft.TextAlign.CENTER)
                    ])
                    goals_container.controls.append(row)
                    goal_entries[key] = row.controls[1]
            elif plan_type == 'monthly':
                goals = [("📚 Words per month", "monthly_goal_words", user_plan.get('monthly_goal_words', 80)),
                         ("📖 Grammar rules per month", "monthly_goal_grammar", user_plan.get('monthly_goal_grammar', 20)),
                         ("💬 Phrases per month", "monthly_goal_phrases", user_plan.get('monthly_goal_phrases', 40))]
                for label, key, default in goals:
                    row = ft.Row([
                        ft.Text(label, width=180, color=COLORS['text_secondary']),
                        ft.TextField(value=str(default), width=100, height=40, text_align=ft.TextAlign.CENTER)
                    ])
                    goals_container.controls.append(row)
                    goal_entries[key] = row.controls[1]
            else:
                goals = [("📚 Words per day", "custom_goal_words", user_plan.get('custom_goal_words', 10)),
                         ("📖 Grammar rules per day", "custom_goal_grammar", user_plan.get('custom_goal_grammar', 3)),
                         ("💬 Phrases per day", "custom_goal_phrases", user_plan.get('custom_goal_phrases', 5))]
                for label, key, default in goals:
                    row = ft.Row([
                        ft.Text(label, width=180, color=COLORS['text_secondary']),
                        ft.TextField(value=str(default), width=100, height=40, text_align=ft.TextAlign.CENTER)
                    ])
                    goals_container.controls.append(row)
                    goal_entries[key] = row.controls[1]
                if plan_type == 'custom':
                    interval_row = ft.Row([
                        ft.Text("⏱️ Interval (days):", width=180, color=COLORS['text_secondary']),
                        ft.TextField(value=str(user_plan.get('custom_interval_days', 1)), width=100, height=40, text_align=ft.TextAlign.CENTER)
                    ])
                    goals_container.controls.append(interval_row)
                    goal_entries['custom_interval_days'] = interval_row.controls[1]
            self.page.update()
        plan_type_dropdown.on_change = update_plan_inputs
        def save_plan(e):
            plan_type = plan_type_dropdown.value
            updates = {}
            for key, entry in goal_entries.items():
                try:
                    updates[key] = int(entry.value)
                except:
                    self.page.snack_bar = ft.SnackBar(content=ft.Text("Please enter valid numbers"), bgcolor=COLORS['warning'])
                    self.page.snack_bar.open = True
                    return
            self.user_manager.update_user_plan(self.current_user['id'], plan_type, **updates)
            self.page.snack_bar = ft.SnackBar(content=ft.Text("✅ Plan updated!"), bgcolor=COLORS['success'])
            self.page.snack_bar.open = True
            self.page.update()

        # Privacy Tab
        privacy = self.user_manager.get_privacy_settings(self.current_user['id'])
        public_profile = ft.Checkbox(label="Make my profile public", value=privacy['profile_public'], check_color=COLORS['accent'])
        def toggle_privacy(e):
            self.user_manager.update_privacy(self.current_user['id'], public_profile.value)
            self.page.snack_bar = ft.SnackBar(content=ft.Text("✅ Privacy settings updated!"), bgcolor=COLORS['success'])
            self.page.snack_bar.open = True
            self.page.update()
        public_profile.on_change = toggle_privacy

        # Logout
        def logout(e):
            def confirm(e):
                self._close_dialog(logout_dialog)
                # حذف اطلاعات ذخیره شده
                self.page.client_storage.remove(STORAGE_USER_KEY)
                self.current_user = None
                self.show_login()
            logout_dialog = ft.AlertDialog(
                title=ft.Text("Logout", color=COLORS['warning']),
                content=ft.Text("Are you sure you want to logout?"),
                actions=[
                    ft.TextButton("Cancel", on_click=lambda e: self._close_dialog(logout_dialog)),
                    ft.ElevatedButton("Logout", on_click=confirm, bgcolor=COLORS['danger'])
                ]
            )
            self.page.dialog = logout_dialog
            logout_dialog.open = True
            self.page.update()

        def delete_account_data(e):
            def confirm(e):
                self._close_dialog(confirm_dialog)
                for table in ['vocabulary', 'phrases', 'practice_chat', 'daily_progress']:
                    self.user_manager.db.cursor.execute(f"DELETE FROM {table} WHERE user_id = ?", (self.current_user['id'],))
                self.user_manager.db.conn.commit()
                self.page.snack_bar = ft.SnackBar(content=ft.Text("✅ All learning data cleared!"), bgcolor=COLORS['success'])
                self.page.snack_bar.open = True
                self.page.update()
                self.show_dashboard()
            confirm_dialog = ft.AlertDialog(
                title=ft.Text("Clear Data", color=COLORS['warning']),
                content=ft.Text("This will delete all your vocabulary, phrases, and practice history. This cannot be undone!"),
                actions=[
                    ft.TextButton("Cancel", on_click=lambda e: self._close_dialog(confirm_dialog)),
                    ft.ElevatedButton("Clear", on_click=confirm, bgcolor=COLORS['danger'])
                ]
            )
            self.page.dialog = confirm_dialog
            confirm_dialog.open = True
            self.page.update()

        tabs = ft.Tabs(
            selected_index=0,
            tabs=[
                ft.Tab(text="⚙️ General", content=ft.Container(
                    content=ft.Column([
                        ft.Text("Daily Learning Goal", size=14, weight=ft.FontWeight.BOLD),
                        goal_dropdown,
                        ft.ElevatedButton("Update Goal", on_click=update_goal, bgcolor=COLORS['info']),
                        ft.Divider(),
                        ft.Text("Avatar", size=14, weight=ft.FontWeight.BOLD),
                        avatar_row,
                    ], spacing=15, scroll=ft.ScrollMode.AUTO),
                    padding=20, expand=True
                )),
                ft.Tab(text="📅 Learning Plan", content=ft.Container(
                    content=ft.Column([
                        ft.Text("Personalized Learning Plan", size=18, weight=ft.FontWeight.BOLD, color=COLORS['accent']),
                        plan_type_dropdown,
                        ft.Container(content=goals_container),
                        ft.ElevatedButton("💾 Save Plan Settings", on_click=save_plan, bgcolor=COLORS['success']),
                        ft.Divider(),
                        ft.Text(f"🔥 Current Streak: {user_plan.get('current_streak', 0)} days", size=13),
                        ft.Text(f"🏆 Longest Streak: {user_plan.get('longest_streak', 0)} days", size=13),
                    ], spacing=15, scroll=ft.ScrollMode.AUTO),
                    padding=20, expand=True
                )),
                ft.Tab(text="🔒 Privacy", content=ft.Container(
                    content=ft.Column([
                        public_profile,
                        ft.Divider(),
                        ft.Text("Account Information", size=14, weight=ft.FontWeight.BOLD),
                        ft.Text(f"Username: {self.current_user['username']}", size=13),
                        ft.Text(f"Email: {self.current_user['email']}", size=13),
                        ft.Divider(),
                        ft.ElevatedButton("Delete Account Data", on_click=delete_account_data, bgcolor=COLORS['danger']),
                        ft.ElevatedButton("Logout", on_click=logout, bgcolor=COLORS['danger']),
                    ], spacing=15, scroll=ft.ScrollMode.AUTO),
                    padding=20, expand=True
                )),
            ],
            expand=True
        )
        nav_bar = self._bottom_nav_bar()
        self.page.add(
            ft.Column([
                ft.Container(content=ft.Text("⚙️ Settings", size=24, weight=ft.FontWeight.BOLD, color=COLORS['accent']), padding=ft.padding.all(20)),
                ft.Container(content=tabs, expand=True),
                nav_bar
            ], spacing=10, expand=True)
        )
        update_plan_inputs(None)

    def _update_avatar(self, new_avatar):
        self.user_manager.update_profile(self.current_user['id'], avatar=new_avatar)
        self.current_user['avatar'] = new_avatar
        self.page.snack_bar = ft.SnackBar(content=ft.Text("✅ Avatar updated!"), bgcolor=COLORS['success'])
        self.page.snack_bar.open = True
        self.page.update()
        self.show_settings()

    def show_profile(self, e):
        stats = self.user_manager.get_grammar_stats()
        words_count = self.user_manager.db.cursor.execute("SELECT COUNT(*) FROM vocabulary WHERE user_id = ?", (self.current_user['id'],)).fetchone()[0]
        phrases_count = self.user_manager.db.cursor.execute("SELECT COUNT(*) FROM phrases WHERE user_id = ?", (self.current_user['id'],)).fetchone()[0]
        favorites_count = len(self.user_manager.get_grammar_favorites())
        dialog = ft.AlertDialog(
            title=ft.Text("User Profile", color=COLORS['accent']),
            content=ft.Container(
                content=ft.Column([
                    ft.Container(content=ft.Text(self.current_user['avatar'], size=50), alignment=ft.alignment.center),
                    ft.Text(self.current_user['username'], size=20, weight=ft.FontWeight.BOLD, color=COLORS['text'], text_align=ft.TextAlign.CENTER),
                    ft.Text(self.current_user['email'], size=13, color=COLORS['text_secondary'], text_align=ft.TextAlign.CENTER),
                    ft.Divider(),
                    ft.Row([
                        ft.Column([ft.Text("⭐ Level", size=12), ft.Text(str(self.current_user['level']), size=18, weight=ft.FontWeight.BOLD, color=COLORS['accent'])], horizontal_alignment=ft.CrossAxisAlignment.CENTER, expand=True),
                        ft.Column([ft.Text("🔥 Streak", size=12), ft.Text(str(self.current_user['current_streak']), size=18, weight=ft.FontWeight.BOLD, color=COLORS['warning'])], horizontal_alignment=ft.CrossAxisAlignment.CENTER, expand=True),
                    ]),
                    ft.Divider(),
                    ft.Row([
                        ft.Column([ft.Text("📚 Words", size=12), ft.Text(str(words_count), size=16, weight=ft.FontWeight.BOLD)], horizontal_alignment=ft.CrossAxisAlignment.CENTER, expand=True),
                        ft.Column([ft.Text("💬 Phrases", size=12), ft.Text(str(phrases_count), size=16, weight=ft.FontWeight.BOLD)], horizontal_alignment=ft.CrossAxisAlignment.CENTER, expand=True),
                        ft.Column([ft.Text("⭐ Favorites", size=12), ft.Text(str(favorites_count), size=16, weight=ft.FontWeight.BOLD)], horizontal_alignment=ft.CrossAxisAlignment.CENTER, expand=True),
                    ]),
                ], spacing=10),
                padding=20, width=380
            ),
            actions=[ft.TextButton("Close", on_click=lambda e: self._close_dialog(dialog))]
        )
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()

    def nav_change(self, index):
        self.current_index = index
        if index == 0:
            self.show_dashboard()
        elif index == 1:
            self.show_vocabulary()
        elif index == 2:
            self.show_grammar()
        elif index == 3:
            self.show_practice()
        elif index == 4:
            self.show_phrases()
        elif index == 5:
            self.show_community()
        elif index == 6:
            self.show_leaderboard()
        elif index == 7:
            self.show_settings()


def main(page: ft.Page):
    app = IDELingoApp()
    app.main(page)


if __name__ == "__main__":
    ft.app(target=main)
