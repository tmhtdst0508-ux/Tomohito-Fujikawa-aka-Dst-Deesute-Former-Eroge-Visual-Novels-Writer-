"""
Main Window for KENZEN SeaArt Helper v5.0.1
Coordinates all 8 tabs (including Gacha!), cross-tab signals, cooldown locks,
prompt transfer dialogs (Overwrite/Append/Cancel), and NUKE full reset.
"""

import os
from typing import Optional
from PySide6.QtWidgets import (
    QMainWindow, QTabWidget, QStatusBar, QWidget, QVBoxLayout,
    QApplication, QMessageBox
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon, QScreen

from ..core.db_manager import DBManager
from ..core.config_manager import ConfigManager
from ..core.prompt_engine import PromptEngine
from ..core.gemini_api import GeminiAPI
from ..core.path_utils import get_resource_path

from .style import MAIN_STYLESHEET
from .matrix_window import MatrixWindow
from .tab_cockpit import TabCockpit
from .tab_positive import TabPositive
from .tab_negative import TabNegative
from .tab_lora import TabLoRA
from .tab_favorites import TabFavorites
from .tab_gacha import TabGacha
from .tab_mobile import TabMobile
from .tab_io import TabIO


class MainWindow(QMainWindow):
    def __init__(self, config_manager: Optional[ConfigManager] = None, db_manager: Optional[DBManager] = None, parent=None):
        super().__init__(parent)
        
        # 1. Initialize Core Engines & Enforce Database Health
        self.db = db_manager if db_manager is not None else DBManager()
        self.db.enforce_valid_database_or_exit()

        self.config = config_manager if config_manager is not None else ConfigManager()
        self.prompt_engine = PromptEngine(self.db)
        self.gemini_api = GeminiAPI(self.config.get_setting("GeminiAPIKey", ""), self.db)

        # 2. Main Cockpit Setup
        self.setWindowTitle("KENZEN SeaArt Helper v5.1.1")
        self.resize(920, 680)
        self.setStyleSheet(MAIN_STYLESHEET)

        # 3. Matrix Dictionary View Window
        self.matrix_window = MatrixWindow(self.db)
        self.matrix_window.tag_selected.connect(self.on_matrix_tag_selected)
        self.matrix_window.sample_prompt_selected.connect(self.on_sample_prompt_selected)

        # 4. Set Application & Window Icons
        self.set_app_icon()

        # 5. Setup Tabs
        self.init_ui()

    def set_app_icon(self):
        icon_path = get_resource_path("kenzen_icon.ico")
        if os.path.exists(icon_path):
            app_icon = QIcon(icon_path)
            self.setWindowIcon(app_icon)
            QApplication.setWindowIcon(app_icon)
            if hasattr(self, "matrix_window") and self.matrix_window is not None:
                self.matrix_window.setWindowIcon(app_icon)

            import sys
            if sys.platform == "win32":
                self._apply_native_windows_icon(icon_path)

    def _apply_native_windows_icon(self, icon_path: str):
        """Directly sends WM_SETICON to OS HWNDs to guarantee taskbar icon stability."""
        try:
            import ctypes
            IMAGE_ICON = 1
            LR_LOADFROMFILE = 0x00000010
            WM_SETICON = 0x0080
            ICON_SMALL = 0
            ICON_BIG = 1

            user32 = ctypes.windll.user32
            hicon_big = user32.LoadImageW(None, icon_path, IMAGE_ICON, 32, 32, LR_LOADFROMFILE)
            hicon_small = user32.LoadImageW(None, icon_path, IMAGE_ICON, 16, 16, LR_LOADFROMFILE)

            if hicon_big or hicon_small:
                hwnds = [int(self.winId())]
                if hasattr(self, "matrix_window") and self.matrix_window is not None:
                    hwnds.append(int(self.matrix_window.winId()))

                for hwnd in hwnds:
                    if hicon_big:
                        user32.SendMessageW(hwnd, WM_SETICON, ICON_BIG, hicon_big)
                    if hicon_small:
                        user32.SendMessageW(hwnd, WM_SETICON, ICON_SMALL, hicon_small)
        except Exception:
            pass

    def init_ui(self):
        self.tab_widget = QTabWidget(self)
        self.setCentralWidget(self.tab_widget)

        # Instantiate Tabs
        self.tab_cockpit = TabCockpit(self.prompt_engine, self.config, self)
        self.tab_positive = TabPositive(self.config, self)
        self.tab_negative = TabNegative(self.config, self.prompt_engine, self)
        self.tab_lora = TabLoRA(self.config, self.prompt_engine, self)
        self.tab_favorites = TabFavorites(self.config, self)
        self.tab_gacha = TabGacha(self.gemini_api, self.config, self)
        self.tab_mobile = TabMobile(self.config, self)
        self.tab_io = TabIO(self.config, self)

        # Add Tabs
        self.tab_widget.addTab(self.tab_cockpit, "Cockpit")
        self.tab_widget.addTab(self.tab_positive, "Positive")
        self.tab_widget.addTab(self.tab_negative, "Negative")
        self.tab_widget.addTab(self.tab_lora, "LoRA")
        self.tab_widget.addTab(self.tab_favorites, "Favorites")
        self.tab_widget.addTab(self.tab_gacha, "Gacha!")
        self.tab_widget.addTab(self.tab_mobile, "Mobile Memo")
        self.tab_widget.addTab(self.tab_io, "IO / Settings")

        # Cross-Tab Signals
        self.tab_cockpit.open_matrix_requested.connect(self.focus_or_toggle_matrix_window)
        self.tab_cockpit.send_to_fav_requested.connect(self.on_send_to_fav)

        self.tab_positive.send_to_cockpit_beginning.connect(self.on_positive_to_cockpit_beginning)

        # LoRA: Direct append with duplicate prevention (Issue 2)
        self.tab_lora.send_to_cockpit.connect(self.on_lora_to_cockpit)
        self.tab_lora.send_to_negative_preview.connect(self.tab_negative.append_to_preview)
        self.tab_lora.send_to_fav.connect(self.on_send_to_fav)

        self.tab_favorites.send_to_cockpit.connect(lambda txt: self.send_to_cockpit_with_dialog(txt, is_prefix=False))
        self.tab_favorites.pull_cockpit_requested.connect(self.on_pull_cockpit_to_fav)
        self.tab_gacha.send_to_cockpit.connect(lambda txt: self.send_to_cockpit_with_dialog(txt, is_prefix=False))
        self.tab_gacha.send_to_fav.connect(self.on_send_to_fav)
        self.tab_gacha.cooldown_active.connect(self.on_gacha_cooldown)

        self.tab_io.config_reloaded.connect(self.on_config_reloaded)
        # Issue 13: NUKE full UI reset
        self.tab_io.config_reset_all_ui.connect(self.on_nuke_reset_all_ui)

        # Status bar
        self.status_bar = QStatusBar(self)
        self.setStatusBar(self.status_bar)
        total_tags = sum(len(tags) for tags in self.db._tags_by_category_cache.values())
        self.status_bar.showMessage(f"KENZEN SeaArt Helper v5.1.1 - Ready (41 Categories / {total_tags:,} Tags Loaded)")

        # Global Shortcuts (Window-level context so they work across all tabs and focused inputs):
        # Ctrl+Shift+P for inserting Positive Prompt from any tab
        from PySide6.QtGui import QKeySequence, QShortcut
        self.shortcut_pos = QShortcut(QKeySequence("Ctrl+Shift+P"), self)
        self.shortcut_pos.setContext(Qt.WindowShortcut)
        self.shortcut_pos.activated.connect(self.on_shortcut_insert_positive)

        # Ctrl+Shift+L for inserting LoRA tags from any tab
        self.shortcut_lora = QShortcut(QKeySequence("Ctrl+Shift+L"), self)
        self.shortcut_lora.setContext(Qt.WindowShortcut)
        self.shortcut_lora.activated.connect(self.on_shortcut_insert_lora)

    def _clamp_to_visible_screen(self, widget: QWidget):
        """Edge-case Guard 6: Clamps widget inside available virtual desktop geometry to avoid lost off-screen windows."""
        screen = QApplication.screenAt(widget.pos()) or QApplication.primaryScreen()
        if not screen:
            return
        geo = screen.availableGeometry()
        w_geo = widget.geometry()

        new_x = w_geo.x()
        new_y = w_geo.y()

        # Check horizontal bounds
        if new_x + w_geo.width() > geo.right() or new_x < geo.left():
            new_x = max(geo.left(), min(new_x, geo.right() - w_geo.width()))
        # Check vertical bounds
        if new_y + w_geo.height() > geo.bottom() or new_y < geo.top():
            new_y = max(geo.top(), min(new_y, geo.bottom() - w_geo.height()))

        widget.setGeometry(new_x, new_y, min(w_geo.width(), geo.width()), min(w_geo.height(), geo.height()))

    def show_windows_side_by_side(self):
        screen = QApplication.primaryScreen().availableGeometry()
        
        # Ensure matrix window has at least 1060px to display all 4 columns if screen allows
        target_h = min(780, max(680, screen.height() - 80))
        mat_w = 1060
        win_w = 820

        if screen.width() >= (win_w + mat_w + 30):
            # Wide screen (e.g. 1920x1080 or multi-monitor): Side-by-side without horizontal scrollbar
            self.setGeometry(screen.x() + 15, screen.y() + 35, win_w, target_h)
            self.matrix_window.setGeometry(screen.x() + win_w + 25, screen.y() + 35, mat_w, target_h)
        elif screen.width() >= 1200:
            # Medium screen: Prioritize matrix 4 columns with slight overlap or snug fit
            mat_w = min(1060, screen.width() - 100)
            win_w = min(820, screen.width() - 100)
            self.setGeometry(screen.x() + 20, screen.y() + 30, win_w, target_h)
            self.matrix_window.setGeometry(screen.x() + 60, screen.y() + 50, mat_w, target_h)
        else:
            # Narrow screen: Responsive fit, scrollable via ScrollBarAsNeeded
            self.setGeometry(screen.x() + 10, screen.y() + 20, screen.width() - 20, target_h)
            self.matrix_window.setGeometry(screen.x() + 20, screen.y() + 30, screen.width() - 40, target_h)

        self._clamp_to_visible_screen(self)
        self._clamp_to_visible_screen(self.matrix_window)

        self.show()
        self.matrix_window.show()
        self.set_app_icon()
        self._check_and_show_recovery_notice()

    def _check_and_show_recovery_notice(self):
        """Shows informative dialog if configuration was auto-recovered from backup or rescued."""
        if not hasattr(self, "config") or not self.config.recovery_notice:
            return

        notice = self.config.recovery_notice
        self.config.recovery_notice = None # Clear after showing once

        status = notice.get("status")
        corrupted_path = notice.get("corrupted_path", "")
        backup_path = notice.get("backup_path", "")

        if status == "restored_from_backup":
            msg = (
                "【⚠️ 設定ファイルの自動復元 / Config Auto-Restored】\n\n"
                "設定ファイル（KENZEN_Config.json）に破損または構文エラーを検知しました。\n"
                "直前の正常なバックアップ（.bak）から設定を自動復元しました。\n\n"
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                "【破損ファイルの救出退避 / Corrupted File Rescued】\n"
                "破損していたファイルは、データ救出用として以下に保存されています：\n"
                f"{corrupted_path}\n\n"
                f"復元元バックアップ: {backup_path}\n"
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
            )
            QMessageBox.information(self, "自動修復の通知 / Config Auto-Restored", msg)

        elif status == "reset_to_default":
            msg = (
                "【⚠️ 初期設定で起動しました / Reset to Default】\n\n"
                "設定ファイルが破損しており、有効なバックアップも見つからなかったため、\n"
                "初期設定ファイルを作成して起動しました。\n\n"
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                "【破損ファイルの救出退避 / Corrupted File Rescued】\n"
                "破損していたファイルは、データ救出用として以下に保存されています：\n"
                f"{corrupted_path}\n"
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
            )
            QMessageBox.warning(self, "初期設定の通知 / Reset to Default", msg)

    def bring_to_front(self):
        """Brings Main Window and Matrix Window to the front and restores if minimized."""
        if self.isMinimized():
            self.showNormal()
        self.show()
        self.raise_()
        self.activateWindow()

        if hasattr(self, "matrix_window") and self.matrix_window.isVisible():
            if self.matrix_window.isMinimized():
                self.matrix_window.showNormal()
            self.matrix_window.show()
            self.matrix_window.raise_()

    def focus_or_toggle_matrix_window(self):
        if self.matrix_window.isMinimized():
            self.matrix_window.showNormal()
        self._clamp_to_visible_screen(self.matrix_window)
        if not self.matrix_window.isVisible():
            self.matrix_window.show()
        self.matrix_window.show()
        self.matrix_window.raise_()
        self.matrix_window.activateWindow()

    def on_matrix_tag_selected(self, tag_text: str, is_comma: bool):
        self.tab_cockpit.append_tag(tag_text, is_comma=is_comma)
        mode_str = "comma (, )" if is_comma else "space ( )"
        self.status_bar.showMessage(f"Tag added ({mode_str}): {tag_text}", 3000)

    def on_sample_prompt_selected(self, prompt_text: str, target: str = "cockpit"):
        """Transfers sample prompt to Cockpit with overwrite/append/cancel dialog."""
        self.tab_widget.setCurrentIndex(0) # Cockpit tab
        self.send_to_cockpit_with_dialog(prompt_text, is_prefix=False)
        self.bring_to_front()

    def on_shortcut_insert_positive(self):
        """Ctrl+Shift+P: Inserts Positive prompt into Cockpit from any tab (requires non-empty preview)."""
        pos_text = self.tab_positive.get_current_positive_prompt()
        if not pos_text:
            QMessageBox.warning(
                self,
                "注意 / Warning",
                "ポジティブプレビュー欄が空です。適用するタグを選択してください。\nPositive preview is empty."
            )
            return
        self.on_positive_to_cockpit_beginning(pos_text)

    def on_shortcut_insert_lora(self):
        """Ctrl+Shift+L: Appends LoRA tags into Cockpit from any tab (requires non-empty preview)."""
        lora_text = self.tab_lora.get_current_lora_prompt()
        if not lora_text:
            QMessageBox.warning(
                self,
                "注意 / Warning",
                "送信するLoRAタグがプレビューボックスにありません。\nNo LoRA tags in the preview box."
            )
            return
        self.on_lora_to_cockpit(lora_text)

    def on_positive_to_cockpit_beginning(self, text: str):
        """
        Inserts positive tags at the beginning of Cockpit without asking overwrite/append dialog.
        Shows warning dialog ONLY when exact same prompt already exists in Cockpit.
        """
        success = self.tab_cockpit.receive_positive_prompt(text)
        if success:
            self.tab_widget.setCurrentIndex(0)
            self.tab_cockpit.txt_main.setFocus()
            self.status_bar.showMessage("Positive prompt inserted into Cockpit", 3000)

    def on_pull_cockpit_to_fav(self):
        """Pulls Cockpit prompt into Favorites tab input."""
        prompt = self.tab_cockpit.get_prompt()
        if prompt:
            self.tab_favorites.set_prompt_from_cockpit(prompt)
            self.status_bar.showMessage("Cockpit prompt pulled to Favorites input", 3000)
        else:
            QMessageBox.warning(
                self,
                "注意 / Warning",
                "Cockpitのプロンプトが空です。\nCockpit prompt is empty."
            )

    def on_lora_to_cockpit(self, text: str):
        """Issue 2: Appends LoRA tag directly without overwrite dialog, checking for duplicates."""
        self.tab_cockpit.receive_lora_tag(text)
        self.tab_widget.setCurrentIndex(0)
        self.tab_cockpit.txt_main.setFocus()
        self.status_bar.showMessage("LoRA tag transferred to Cockpit", 3000)

    def send_to_cockpit_with_dialog(self, text: str, is_prefix: bool = False):
        """Issue 10: Handles Cockpit prompt insertion with dialog."""
        self.tab_cockpit.receive_prompt_from_external(text, is_prefix=is_prefix)
        self.tab_widget.setCurrentIndex(0)
        self.tab_cockpit.txt_main.setFocus()
        self.status_bar.showMessage("Prompt transferred to Cockpit", 3000)

    def on_send_to_fav(self, prompt: str, description: str = ""):
        self.tab_favorites.add_from_external(prompt, description)
        self.tab_widget.setCurrentIndex(4)
        self.status_bar.showMessage("Prompt transferred to Favorites tab", 3000)

    def on_gacha_cooldown(self, is_locked: bool):
        self.tab_widget.tabBar().setEnabled(not is_locked)
        if is_locked:
            self.status_bar.showMessage("⏳ Gacha Cooling Down (15s)... Tabs and buttons locked.")
        else:
            self.status_bar.showMessage("Ready / 準備完了", 3000)

    def on_config_reloaded(self):
        self.tab_positive.refresh_presets()
        self.tab_positive.load_stock()
        self.tab_negative.refresh_presets()
        self.tab_negative.load_stock()
        self.tab_lora.load_loras()
        self.tab_lora.refresh_presets()
        self.tab_favorites.load_favorites()
        self.tab_mobile.load_memos()
        self.tab_gacha.txt_api_key.setText(self.config.get_setting("GeminiAPIKey", ""))
        self.tab_gacha.update_quota_label()
        self.status_bar.showMessage("All configurations reloaded / 全設定を再読込しました", 3000)

    def on_nuke_reset_all_ui(self):
        """Issue 13: Completely clears all UI editor fields and controls across all tabs."""
        self.tab_cockpit.txt_main.clear()
        self.tab_lora.clear_all_ui()
        self.tab_gacha.clear_all_ui()
        self.tab_favorites.txt_desc.clear()
        self.tab_favorites.txt_prompt.clear()
        self.tab_mobile.txt_content.clear()
        self.on_config_reloaded()
        self.status_bar.showMessage("Factory Reset (NUKE) complete. All UI fields cleared.", 4000)

    def closeEvent(self, event):
        # 1. Edge-case Guard: Block exit if Gacha Gemini API is actively communicating
        if hasattr(self, "tab_gacha") and self.tab_gacha.is_busy():
            QMessageBox.warning(
                self,
                "生成中 / Generating in Progress",
                "⚠️ AIがプロンプト生成中です。\n通信完了まで少々お待ちください。\n\n"
                "AI prompt generation is currently in progress. Please wait until completion."
            )
            event.ignore()
            return

        # 2. Approach A: Confirm exit if Gacha is in 15-second cooldown
        if hasattr(self, "tab_gacha"):
            cd = self.tab_gacha.get_cooldown_remaining()
            if cd > 0:
                ans = QMessageBox.question(
                    self,
                    "終了確認 / Confirm Exit",
                    f"現在 Gacha! のクールダウン中です（残り {cd} 秒）。\n本当に終了しますか？\n\n"
                    f"Gacha is currently cooling down ({cd}s remaining). Do you really want to exit?",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.No
                )
                if ans != QMessageBox.Yes:
                    event.ignore()
                    return

        self.matrix_window.close()
        event.accept()
