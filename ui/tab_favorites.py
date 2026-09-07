"""
Favorites Tab for KENZEN SeaArt Helper v5.0.0
Manages saved favorite prompts, descriptions, search, reordering, duplicate prevention,
multi-row deletion, Delete All Favorites, and Mobile JSON export.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QTextEdit, QGroupBox,
    QSplitter, QMessageBox, QApplication, QFileDialog
)
from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtGui import QColor, QBrush
from ..core.config_manager import ConfigManager
from ..core.prompt_engine import sanitize_sd_prompt
from .style import COLOR_ACTION, COLOR_SUCCESS, COLOR_DANGER, safe_copy_to_clipboard
from .widgets import PlainTextOnlyTextEdit


class TabFavorites(QWidget):
    send_to_cockpit = Signal(str)
    pull_cockpit_requested = Signal()

    def __init__(self, config_manager: ConfigManager, parent=None):
        super().__init__(parent)
        self.config = config_manager
        self.fav_history = []
        
        # Flash Animation Setup (3-pulse bright yellow highlight)
        self.flash_timer = QTimer(self)
        self.flash_timer.setInterval(160)
        self.flash_timer.timeout.connect(self._on_flash_tick)
        self.flashing_row = None
        self.flash_step = 0
        
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(10)

        # 1. Top Search Bar
        top_bar = QHBoxLayout()
        lbl_search = QLabel("🔍 Search Favorites / 検索:")
        lbl_search.setStyleSheet("font-weight: bold;")
        self.txt_search = QLineEdit()
        self.txt_search.setPlaceholderText("Search description or prompt / 説明またはプロンプトを検索...")
        self.txt_search.textChanged.connect(self.on_search_changed)
        
        btn_clear_search = QPushButton("Clear")
        btn_clear_search.clicked.connect(lambda: self.txt_search.clear())

        top_bar.addWidget(lbl_search)
        top_bar.addWidget(self.txt_search, 1)
        top_bar.addWidget(btn_clear_search)
        layout.addLayout(top_bar)

        # 2. Splitter: Table on Top, Detail/Edit on Bottom
        splitter = QSplitter(Qt.Vertical)

        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["No.", "Description / タイトル", "Prompt / プロンプト"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Interactive)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.table.setColumnWidth(1, 240)
        
        # Hide vertical header to eliminate duplicate numbers
        self.table.verticalHeader().setVisible(False)
        
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.ExtendedSelection)
        self.table.itemSelectionChanged.connect(self.on_row_selected)
        self.table.cellClicked.connect(self.on_cell_clicked)
        self.table.currentCellChanged.connect(self.on_current_cell_changed)
        splitter.addWidget(self.table)

        # Detail / Edit Box
        detail_box = QGroupBox("Favorite Details & Edit / 詳細・編集")
        detail_layout = QVBoxLayout(detail_box)
        detail_layout.setSpacing(6)

        h_desc = QHBoxLayout()
        lbl_desc = QLabel("Description:")
        lbl_desc.setFixedWidth(80)
        self.txt_desc = QLineEdit()
        self.txt_desc.setPlaceholderText("e.g. 放課後の教室で笑顔を向ける少女")
        h_desc.addWidget(lbl_desc)
        h_desc.addWidget(self.txt_desc)
        detail_layout.addLayout(h_desc)

        h_prompt = QHBoxLayout()
        lbl_pr = QLabel("Prompt:")
        lbl_pr.setFixedWidth(80)
        self.txt_prompt = PlainTextOnlyTextEdit()
        self.txt_prompt.setFixedHeight(75)
        h_prompt.addWidget(lbl_pr)
        h_prompt.addWidget(self.txt_prompt)
        detail_layout.addLayout(h_prompt)

        # Action sub-bar inside detail
        btn_bar_detail = QHBoxLayout()
        
        btn_pull_cockpit = QPushButton("📥 Pull from Cockpit")
        btn_pull_cockpit.setToolTip("Pull current prompt from Cockpit into prompt field")
        btn_pull_cockpit.clicked.connect(lambda: self.pull_cockpit_requested.emit())

        btn_save_new = QPushButton("➕ Add New / 新規登録")
        btn_save_new.clicked.connect(self.on_add_new)

        btn_replace = QPushButton("🔄 Replace Selected / 上書き更新")
        btn_replace.clicked.connect(self.on_update_selected)

        btn_clear_input = QPushButton("🧹 Clear Input / 入力消去")
        btn_clear_input.setToolTip("Clears description and prompt fields without affecting saved data")
        btn_clear_input.clicked.connect(self.on_clear_input)

        btn_undo_fav = QPushButton("↩ Undo Fav")
        btn_undo_fav.setToolTip("Undo last change to favorites")
        btn_undo_fav.clicked.connect(self.on_undo_fav)

        btn_delete = QPushButton("🗑 Delete / 削除")
        btn_delete.setProperty("btnType", "danger")
        btn_delete.clicked.connect(self.on_delete_selected)

        btn_delete_all = QPushButton("💣 Delete All / 全削除")
        btn_delete_all.setProperty("btnType", "danger")
        btn_delete_all.clicked.connect(self.on_delete_all_favorites)

        btn_up = QPushButton("▲ Up")
        btn_up.clicked.connect(self.on_move_up)

        btn_down = QPushButton("▼ Down")
        btn_down.clicked.connect(self.on_move_down)

        btn_bar_detail.addWidget(btn_pull_cockpit)
        btn_bar_detail.addWidget(btn_save_new)
        btn_bar_detail.addWidget(btn_replace)
        btn_bar_detail.addWidget(btn_clear_input)
        btn_bar_detail.addWidget(btn_undo_fav)
        btn_bar_detail.addWidget(btn_delete)
        btn_bar_detail.addWidget(btn_delete_all)
        btn_bar_detail.addStretch()
        btn_bar_detail.addWidget(btn_up)
        btn_bar_detail.addWidget(btn_down)
        detail_layout.addLayout(btn_bar_detail)

        splitter.addWidget(detail_box)
        splitter.setStretchFactor(0, 3)
        splitter.setStretchFactor(1, 2)

        layout.addWidget(splitter, 1)

        # 3. Bottom Main Actions
        bottom_bar = QHBoxLayout()

        btn_send_cockpit = QPushButton("🚀 Send Selected Prompt to Cockpit")
        btn_send_cockpit.setProperty("btnType", "success")
        btn_send_cockpit.setFixedHeight(38)
        btn_send_cockpit.clicked.connect(self.on_send_cockpit)

        btn_copy = QPushButton("📋 Copy to Clipboard")
        btn_copy.setProperty("btnType", "action")
        btn_copy.setFixedHeight(38)
        btn_copy.clicked.connect(self.on_copy_clipboard)

        btn_export_mobile = QPushButton("📱 Export to Mobile JSON (モバイル用JSON出力)")
        btn_export_mobile.setFixedHeight(38)
        btn_export_mobile.clicked.connect(self.on_export_mobile_json)

        bottom_bar.addWidget(btn_send_cockpit, 2)
        bottom_bar.addWidget(btn_copy, 1)
        bottom_bar.addWidget(btn_export_mobile, 1)
        layout.addLayout(bottom_bar)

        self.load_favorites()

    def load_favorites(self):
        favs = self.config.get_favorites()
        self.table.setRowCount(len(favs))
        for row, fav in enumerate(favs):
            item_no = QTableWidgetItem(str(row + 1))
            item_no.setTextAlignment(Qt.AlignCenter)
            item_no.setData(Qt.UserRole, fav)

            item_desc = QTableWidgetItem(fav.get("description", ""))
            item_prompt = QTableWidgetItem(fav.get("prompt", ""))

            self.table.setItem(row, 0, item_no)
            self.table.setItem(row, 1, item_desc)
            self.table.setItem(row, 2, item_prompt)

    def _update_detail_from_row(self, row: int):
        """Immediately displays description and prompt of the specified row into details fields."""
        if 0 <= row < self.table.rowCount():
            desc = ""
            prompt = ""
            item_no = self.table.item(row, 0)
            if item_no:
                fav = item_no.data(Qt.UserRole)
                if isinstance(fav, dict):
                    desc = fav.get("description", "")
                    prompt = fav.get("prompt", "")
            if not desc:
                item_desc = self.table.item(row, 1)
                if item_desc:
                    desc = item_desc.text()
            if not prompt:
                item_pr = self.table.item(row, 2)
                if item_pr:
                    prompt = item_pr.text()

            self.txt_desc.setText(desc)
            self.txt_prompt.setPlainText(prompt)

    def on_cell_clicked(self, row: int, col: int):
        """Immediately updates detail fields on clicking any cell in the table."""
        self._update_detail_from_row(row)

    def on_current_cell_changed(self, currentRow: int, currentColumn: int, previousRow: int, previousColumn: int):
        """Immediately updates detail fields when navigation changes the current cell."""
        if currentRow >= 0:
            self._update_detail_from_row(currentRow)

    def on_row_selected(self):
        selected_rows = list(set([item.row() for item in self.table.selectedItems()]))
        if len(selected_rows) == 1:
            self._update_detail_from_row(selected_rows[0])
        elif len(selected_rows) == 0:
            curr = self.table.currentRow()
            if curr >= 0:
                self._update_detail_from_row(curr)
            else:
                self.txt_desc.clear()
                self.txt_prompt.clear()

    def save_fav_history(self):
        """Saves a copy of current favorites for Undo."""
        import copy
        current_favs = self.config.get_favorites()
        self.fav_history.append(copy.deepcopy(current_favs))
        if len(self.fav_history) > 30:
            self.fav_history.pop(0)

    def on_undo_fav(self):
        """Reverts favorites to previous state."""
        if not self.fav_history:
            QMessageBox.warning(
                self,
                "注意 / Warning",
                "取り消す履歴（Undo）がありません。\nNo favorite history to undo."
            )
            return
        last_state = self.fav_history.pop()
        self.config.set_favorites(last_state)
        self.load_favorites()
        QMessageBox.information(
            self,
            "完了 / Success",
            "お気に入りを直前の状態に復元（Undo）しました！\nFavorites restored to previous state."
        )

    def set_prompt_from_cockpit(self, prompt_text: str):
        """Sets the prompt text from Cockpit into the favorite prompt field."""
        self.txt_prompt.setPlainText(prompt_text.strip())
        self.txt_desc.setFocus()

    def add_from_external(self, prompt: str, description: str = ""):
        self.txt_prompt.setPlainText(prompt)
        self.txt_desc.setText(description)
        self.txt_desc.setFocus()

    def on_clear_input(self):
        """Clears the Description and Prompt input boxes and deselects table rows without affecting saved favorites."""
        self.txt_desc.clear()
        self.txt_prompt.clear()
        self.table.clearSelection()

    def flash_row(self, row: int):
        """Starts the yellow flashing animation (3 pulses) on the specified table row."""
        self.flash_timer.stop()
        if self.flashing_row is not None and self.flashing_row < self.table.rowCount():
            self._restore_row_style(self.flashing_row)

        self.flashing_row = row
        self.flash_step = 0
        self.flash_timer.setInterval(160)
        self.flash_timer.start()
        self._on_flash_tick()

    def _restore_row_style(self, row: int):
        """Restores default background and foreground styling to table row items."""
        if row < 0 or row >= self.table.rowCount():
            return
        for col in range(self.table.columnCount()):
            item = self.table.item(row, col)
            if item:
                item.setBackground(QBrush())
                item.setForeground(QBrush())

    def _on_flash_tick(self):
        """Timer callback to toggle row flash highlight."""
        if self.flashing_row is None or self.flashing_row >= self.table.rowCount():
            self.flash_timer.stop()
            self.flashing_row = None
            return

        self.flash_step += 1
        row = self.flashing_row

        if self.flash_step % 2 == 1:
            # Bright Yellow Flash (#FEF08A with dark amber text #854D0E)
            bg_brush = QBrush(QColor("#FEF08A"))
            fg_brush = QBrush(QColor("#854D0E"))
            for col in range(self.table.columnCount()):
                item = self.table.item(row, col)
                if item:
                    item.setBackground(bg_brush)
                    item.setForeground(fg_brush)
        else:
            # Default style
            self._restore_row_style(row)

        if self.flash_step >= 6:
            self.flash_timer.stop()
            self._restore_row_style(row)
            self.flashing_row = None

    def on_add_new(self):
        raw_prompt = self.txt_prompt.toPlainText().strip()
        prompt = sanitize_sd_prompt(raw_prompt)
        if not prompt:
            QMessageBox.warning(
                self,
                "注意 / Warning",
                "有効なプロンプトを入力してください。\nPlease enter a valid prompt."
            )
            return

        favs = self.config.get_favorites()

        # 50-item Limit Check (VBA exact match)
        if len(favs) >= 50:
            QMessageBox.warning(
                self,
                "上限到達 / Limit Reached",
                "お気に入りの登録上限（50件）に達しています。\n不要な項目を削除するか、エクスポートして整理してください。\n\nFavorites limit (50 items) reached. Please delete old items or export to manage."
            )
            return

        desc = self.txt_desc.text().strip() # Description is preserved as-is
        
        # Check duplicate prompt (normalized whitespace and case)
        import re
        norm_prompt = re.sub(r"\s+", " ", prompt.lower())
        for fav in favs:
            curr_norm = re.sub(r"\s+", " ", str(fav.get("prompt", "")).lower())
            if curr_norm == norm_prompt:
                QMessageBox.warning(
                    self,
                    "重複検知 / Duplicate Detected",
                    f"このプロンプトは既に登録されています:\nThis prompt is already saved as:\n'{fav.get('description')}'"
                )
                return

        self.save_fav_history()
        new_id = (max([int(f.get("id", 0)) for f in favs]) + 1) if favs else 1
        favs.append({"id": new_id, "description": desc, "prompt": prompt})
        self.config.set_favorites(favs)
        self.load_favorites()
        new_row = len(favs) - 1
        self.table.selectRow(new_row)
        if self.table.item(new_row, 0):
            self.table.scrollToItem(self.table.item(new_row, 0))
        self.flash_row(new_row)
        self.txt_desc.clear()
        self.txt_prompt.clear()
        QMessageBox.information(
            self,
            "登録完了 / Success",
            "お気に入りに登録しました！\nAdded to Favorites!"
        )

    def on_update_selected(self):
        selected_rows = list(set([item.row() for item in self.table.selectedItems()]))
        if not selected_rows:
            QMessageBox.warning(
                self,
                "注意 / Warning",
                "更新する行を選択してください。\nPlease select a row to update."
            )
            return
        if len(selected_rows) > 1:
            QMessageBox.warning(
                self,
                "注意 / Warning",
                "更新する行を1行だけ選択してください。\nPlease select exactly one row to update."
            )
            return

        row = selected_rows[0]
        favs = self.config.get_favorites()
        if row < len(favs):
            raw_prompt = self.txt_prompt.toPlainText().strip()
            prompt = sanitize_sd_prompt(raw_prompt)
            if not prompt:
                QMessageBox.warning(
                    self,
                    "注意 / Warning",
                    "有効なプロンプトを入力してください。\nPlease enter a valid prompt."
                )
                return

            # Handle empty description confirmation
            desc = self.txt_desc.text().strip()
            if not desc:
                existing_desc = str(favs[row].get("description", "")).strip()
                if existing_desc:
                    msg = (
                        "説明欄が空欄です。既存の説明をそのまま使用して更新しますか？\n"
                        "Description is empty. Keep existing description and update?\n\n"
                        f"【既存の説明 / Existing Description】\n'{existing_desc}'\n\n"
                        "・『はい / Yes』: 既存の説明を保持して更新 (Keep & Update)\n"
                        "・『いいえ / No』: 更新をキャンセル (Cancel)"
                    )
                    ans = QMessageBox.question(
                        self,
                        "説明欄の確認 / Confirm Description",
                        msg,
                        QMessageBox.Yes | QMessageBox.No,
                        QMessageBox.Yes
                    )
                    if ans != QMessageBox.Yes:
                        return
                    desc = existing_desc
                else:
                    desc = ""

            # Check duplicate against other rows
            import re
            norm_prompt = re.sub(r"\s+", " ", prompt.lower())
            for idx, fav in enumerate(favs):
                if idx != row:
                    curr_norm = re.sub(r"\s+", " ", str(fav.get("prompt", "")).lower())
                    if curr_norm == norm_prompt:
                        QMessageBox.warning(
                            self,
                            "重複検知 / Duplicate Detected",
                            f"このプロンプトは他の行（No.{idx+1}）に既に登録されています:\nThis prompt is already saved in row #{idx+1} as:\n'{fav.get('description')}'"
                        )
                        return

            self.save_fav_history()
            favs[row]["description"] = desc
            favs[row]["prompt"] = prompt
            self.config.set_favorites(favs)
            self.load_favorites()
            self.table.selectRow(row)
            if self.table.item(row, 0):
                self.table.scrollToItem(self.table.item(row, 0))
            self.flash_row(row)
            self._update_detail_from_row(row)
            QMessageBox.information(
                self,
                "更新完了 / Success",
                "お気に入りを更新しました。\nFavorite updated."
            )

    def on_delete_selected(self):
        favs = self.config.get_favorites()
        if not favs:
            QMessageBox.warning(
                self,
                "注意 / Warning",
                "お気に入りリストが空です。\nFavorites list is empty."
            )
            return

        selected_rows = sorted(list(set([item.row() for item in self.table.selectedItems()])), reverse=True)
        if not selected_rows:
            QMessageBox.warning(
                self,
                "注意 / Warning",
                "削除するお気に入りを選択してください。\nPlease select favorite(s) to delete."
            )
            return

        ans = QMessageBox.question(
            self,
            "削除確認 / Confirm Delete",
            f"選択した {len(selected_rows)} 件のお気に入りを削除しますか？\nDelete {len(selected_rows)} selected favorite(s)?"
        )
        if ans == QMessageBox.Yes:
            self.save_fav_history()
            for r in selected_rows:
                if r < len(favs):
                    favs.pop(r)
            self.config.set_favorites(favs)
            self.load_favorites()
            self.txt_desc.clear()
            self.txt_prompt.clear()

    def on_delete_all_favorites(self):
        favs = self.config.get_favorites()
        if not favs:
            QMessageBox.warning(
                self,
                "注意 / Warning",
                "お気に入りリストは既に空です。\nFavorites list is already empty."
            )
            return

        ans = QMessageBox.question(
            self,
            "⚠️ 全削除の確認 / Confirm Delete All",
            f"本当に登録されている全 {len(favs)} 件のお気に入りをすべて削除しますか？\n\nAre you sure you want to delete ALL {len(favs)} favorites?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if ans == QMessageBox.Yes:
            self.save_fav_history()
            self.config.set_favorites([])
            self.load_favorites()
            self.txt_desc.clear()
            self.txt_prompt.clear()
            QMessageBox.information(
                self,
                "削除完了 / Success",
                "すべてのお気に入りを削除しました。\nAll favorites have been deleted."
            )

    def on_move_up(self):
        row = self.table.currentRow()
        if row > 0:
            self.save_fav_history()
            favs = self.config.get_favorites()
            favs[row], favs[row - 1] = favs[row - 1], favs[row]
            self.config.set_favorites(favs)
            self.load_favorites()
            self.table.selectRow(row - 1)

    def on_move_down(self):
        row = self.table.currentRow()
        favs = self.config.get_favorites()
        if 0 <= row < len(favs) - 1:
            self.save_fav_history()
            favs[row], favs[row + 1] = favs[row + 1], favs[row]
            self.config.set_favorites(favs)
            self.load_favorites()
            self.table.selectRow(row + 1)

    def on_search_changed(self, text: str):
        kw = text.strip().lower()
        for r in range(self.table.rowCount()):
            desc = self.table.item(r, 1).text().lower()
            pr = self.table.item(r, 2).text().lower()
            match = (kw in desc or kw in pr) if kw else True
            self.table.setRowHidden(r, not match)

    def on_send_cockpit(self):
        prompt = self.txt_prompt.toPlainText().strip()
        if not prompt:
            row = self.table.currentRow()
            if row >= 0:
                prompt = self.table.item(row, 2).text().strip()

        if prompt:
            cleaned = sanitize_sd_prompt(prompt)
            self.send_to_cockpit.emit(cleaned)
        else:
            QMessageBox.warning(
                self,
                "注意 / Warning",
                "送信するプロンプトが選択されていません。\nNo prompt selected."
            )

    def on_copy_clipboard(self):
        """Issue 3: Copy with empty list validation and safe clipboard handler."""
        favs = self.config.get_favorites()
        if not favs:
            QMessageBox.warning(
                self,
                "注意 / Warning",
                "お気に入りリストが空です。コピーできません。\nFavorites list is empty. Nothing to copy."
            )
            return

        prompt = self.txt_prompt.toPlainText().strip()
        if not prompt:
            row = self.table.currentRow()
            if row >= 0:
                prompt = self.table.item(row, 2).text().strip()

        if prompt:
            cleaned = sanitize_sd_prompt(prompt)
            safe_copy_to_clipboard(cleaned, self)
            QMessageBox.information(
                self,
                "完了 / Success",
                "クリップボードにコピーしました！\nCopied to clipboard!"
            )
        else:
            QMessageBox.warning(
                self,
                "注意 / Warning",
                "コピーするプロンプトが選択されていません。\nNo prompt selected."
            )

    def on_export_mobile_json(self):
        """Issue 8: Stop export if favorites list is empty."""
        favs = self.config.get_favorites()
        if not favs:
            QMessageBox.warning(
                self,
                "注意 / Warning",
                "お気に入りリストが空です。エクスポートできません。\nFavorites list is empty. Nothing to export."
            )
            return

        fname, _ = QFileDialog.getSaveFileName(
            self,
            "モバイル用JSONエクスポート / Export Mobile JSON",
            "KENZEN_Mobile_Fav.json",
            "JSON Files (*.json)"
        )
        if fname:
            try:
                self.config.export_mobile_fav_json(fname)
                QMessageBox.information(
                    self,
                    "エクスポート完了 / Success",
                    f"モバイル用JSONを書き出しました！\nMobile JSON exported to:\n{fname}"
                )
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to export: {e}")
