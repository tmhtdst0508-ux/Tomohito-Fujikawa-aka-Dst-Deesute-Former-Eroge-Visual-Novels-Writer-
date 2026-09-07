"""
Positive Tab for KENZEN SeaArt Helper v5.0.0
Dual listbox layout (Stock on Left, Applied on Right), Presets, Preview Window on selection,
and Cockpit insertion at the beginning.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QListWidget, QListWidgetItem, QComboBox, QGroupBox, QMessageBox, QInputDialog,
    QTextEdit
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QKeySequence, QShortcut
from ..core.config_manager import ConfigManager
from ..core.prompt_engine import sanitize_sd_prompt
from .style import COLOR_ACTION, COLOR_SUCCESS, COLOR_DANGER
from .widgets import PlainTextOnlyTextEdit


class TabPositive(QWidget):
    send_to_cockpit_beginning = Signal(str)

    def __init__(self, config_manager: ConfigManager, parent=None):
        super().__init__(parent)
        self.config = config_manager
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(10)

        # 1. Top Preset Bar
        preset_bar = QHBoxLayout()
        lbl_preset = QLabel("Presets:")
        lbl_preset.setStyleSheet("font-weight: bold;")
        
        self.cmb_presets = QComboBox()
        self.cmb_presets.currentIndexChanged.connect(self.on_preset_selected)

        btn_save_preset = QPushButton("Save New Preset")
        btn_save_preset.clicked.connect(self.on_save_preset)

        btn_set_default = QPushButton("⭐ Set as Default")
        btn_set_default.setToolTip("Set selected preset as startup default")
        btn_set_default.clicked.connect(self.on_set_default_preset)

        btn_call_default = QPushButton("🔄 Call Default")
        btn_call_default.setToolTip("Restore/apply startup default preset to fields / デフォルトプリセットを展開・復元")
        btn_call_default.clicked.connect(self.on_call_default_preset)

        btn_delete_preset = QPushButton("Delete Preset")
        btn_delete_preset.setProperty("btnType", "danger")
        btn_delete_preset.clicked.connect(self.on_delete_preset)

        preset_bar.addWidget(lbl_preset)
        preset_bar.addWidget(self.cmb_presets, 1)
        preset_bar.addWidget(btn_save_preset)
        preset_bar.addWidget(btn_set_default)
        preset_bar.addWidget(btn_call_default)
        preset_bar.addWidget(btn_delete_preset)
        layout.addLayout(preset_bar)

        # 2. Dual Listbox (Stock on Left, Center Buttons, Applied on Right)
        dual_layout = QHBoxLayout()
        dual_layout.setSpacing(8)

        # Left Column: Stock
        left_box = QGroupBox("Positive Tag Stock / 手持ちタグ一覧")
        left_layout = QVBoxLayout(left_box)

        input_bar = QHBoxLayout()
        self.txt_new_tag = QLineEdit()
        self.txt_new_tag.setPlaceholderText("Enter new positive tag(s)...")
        self.txt_new_tag.returnPressed.connect(self.on_add_stock_tag)
        
        btn_add = QPushButton("Add")
        btn_add.clicked.connect(self.on_add_stock_tag)

        btn_bulk_import = QPushButton("Bulk Import...")
        btn_bulk_import.setToolTip("Import raw comma-separated prompt text into Stock")
        btn_bulk_import.clicked.connect(self.on_bulk_import)

        input_bar.addWidget(self.txt_new_tag, 1)
        input_bar.addWidget(btn_add)
        input_bar.addWidget(btn_bulk_import)
        left_layout.addLayout(input_bar)

        self.list_stock = QListWidget()
        self.list_stock.setSelectionMode(QListWidget.MultiSelection)
        left_layout.addWidget(self.list_stock)

        stock_btn_bar = QHBoxLayout()
        btn_stock_up = QPushButton("▲ Up")
        btn_stock_up.clicked.connect(lambda: self.on_move_up(self.list_stock, is_stock=True))
        btn_stock_down = QPushButton("▼ Down")
        btn_stock_down.clicked.connect(lambda: self.on_move_down(self.list_stock, is_stock=True))
        btn_stock_del = QPushButton("Delete Stock")
        btn_stock_del.setProperty("btnType", "danger")
        btn_stock_del.clicked.connect(self.on_delete_stock)

        stock_btn_bar.addWidget(btn_stock_up)
        stock_btn_bar.addWidget(btn_stock_down)
        stock_btn_bar.addWidget(btn_stock_del)
        left_layout.addLayout(stock_btn_bar)

        dual_layout.addWidget(left_box, 1)

        # Center Transfer Arrow Buttons (Issue 6: Sized properly without text clipping)
        center_btn_layout = QVBoxLayout()
        center_btn_layout.addStretch()
        
        btn_add_to_apply = QPushButton("➡ Add")
        btn_add_to_apply.setMinimumWidth(85)
        btn_add_to_apply.setFixedHeight(36)
        btn_add_to_apply.setProperty("btnType", "action")
        btn_add_to_apply.setToolTip("Add selected Stock tags to Applied List")
        btn_add_to_apply.clicked.connect(self.on_transfer_to_apply)

        btn_remove_from_apply = QPushButton("⬅ Remove")
        btn_remove_from_apply.setMinimumWidth(85)
        btn_remove_from_apply.setFixedHeight(36)
        btn_remove_from_apply.setToolTip("Remove selected tags from Applied List")
        btn_remove_from_apply.clicked.connect(self.on_transfer_to_stock)

        center_btn_layout.addWidget(btn_add_to_apply)
        center_btn_layout.addWidget(btn_remove_from_apply)
        center_btn_layout.addStretch()
        dual_layout.addLayout(center_btn_layout)

        # Right Column: Applied Tags
        right_box = QGroupBox("Applied Tags / 適用タグ一覧")
        right_layout = QVBoxLayout(right_box)

        self.list_applied = QListWidget()
        self.list_applied.setSelectionMode(QListWidget.MultiSelection)
        # Issue 7: Preview on item selection only
        self.list_applied.itemSelectionChanged.connect(self.update_preview_from_selection)
        right_layout.addWidget(self.list_applied)

        applied_btn_bar = QHBoxLayout()
        btn_app_select_all = QPushButton("Select All")
        btn_app_select_all.clicked.connect(self.on_select_all_applied)
        btn_app_up = QPushButton("▲ Up")
        btn_app_up.clicked.connect(lambda: self.on_move_up(self.list_applied, is_stock=False))
        btn_app_down = QPushButton("▼ Down")
        btn_app_down.clicked.connect(lambda: self.on_move_down(self.list_applied, is_stock=False))
        btn_app_del = QPushButton("Remove")
        btn_app_del.setProperty("btnType", "danger")
        btn_app_del.clicked.connect(self.on_remove_applied)

        applied_btn_bar.addWidget(btn_app_select_all)
        applied_btn_bar.addWidget(btn_app_up)
        applied_btn_bar.addWidget(btn_app_down)
        applied_btn_bar.addWidget(btn_app_del)
        right_layout.addLayout(applied_btn_bar)

        dual_layout.addWidget(right_box, 1)
        layout.addLayout(dual_layout, 1)

        # 3. Preview Area (Issue 7: Empty initially, displays selected items)
        prev_box = QGroupBox("Applied Tags Preview / 選択プレビュー")
        prev_layout = QVBoxLayout(prev_box)
        self.txt_preview = PlainTextOnlyTextEdit()
        self.txt_preview.setFixedHeight(55)
        self.txt_preview.setPlaceholderText("Select tags in the Applied Tags list to preview here...")
        prev_layout.addWidget(self.txt_preview)

        prev_sub_bar = QHBoxLayout()
        btn_clear_prev = QPushButton("Clear Preview")
        btn_clear_prev.setProperty("btnType", "danger")
        btn_clear_prev.clicked.connect(self.on_clear_preview)
        prev_sub_bar.addStretch()
        prev_sub_bar.addWidget(btn_clear_prev)
        prev_layout.addLayout(prev_sub_bar)

        layout.addWidget(prev_box)

        # 4. Bottom Action Bar
        bottom_bar = QHBoxLayout()
        
        self.btn_apply_cockpit = QPushButton("🚀 Send Applied Tags to Cockpit Beginning (Ctrl+Shift+P)")
        self.btn_apply_cockpit.setToolTip("Inserts tags at the BEGINNING of Cockpit main prompt")
        self.btn_apply_cockpit.setProperty("btnType", "success")
        self.btn_apply_cockpit.setFixedHeight(38)
        self.btn_apply_cockpit.clicked.connect(self.on_apply_cockpit)

        bottom_bar.addWidget(self.btn_apply_cockpit)
        layout.addLayout(bottom_bar)

        self.load_stock()
        self.refresh_presets(load_default=True)

    def refresh_presets(self, select_preset_name: str = None, load_default: bool = False):
        presets = self.config.get_positive_presets()
        self.cmb_presets.blockSignals(True)
        self.cmb_presets.clear()
        self.cmb_presets.addItem("-- Select Preset / プリセット選択 --", None)
        target_idx = 0
        if load_default and not select_preset_name:
            default_name = self.config.get_setting("DefaultPositivePreset", "")
            if default_name and default_name in presets:
                select_preset_name = default_name

        for idx, name in enumerate(presets.keys()):
            self.cmb_presets.addItem(name, name)
            if select_preset_name and name == select_preset_name:
                target_idx = idx + 1
        self.cmb_presets.setCurrentIndex(target_idx)
        self.cmb_presets.blockSignals(False)
        if target_idx > 0:
            self.on_preset_selected(target_idx)

    def on_set_default_preset(self):
        name = self.cmb_presets.currentData()
        if not name:
            QMessageBox.warning(
                self,
                "注意 / Warning",
                "デフォルトに設定するプリセットを選択してください。\nPlease select a preset to set as default."
            )
            return
        self.config.set_setting("DefaultPositivePreset", name)
        QMessageBox.information(
            self,
            "設定完了 / Success",
            f"プリセット '{name}' を起動時デフォルトに設定しました！\nPreset '{name}' set as startup default."
        )

    def on_call_default_preset(self):
        default_name = self.config.get_setting("DefaultPositivePreset", "")
        if not default_name:
            QMessageBox.warning(
                self,
                "注意 / Warning",
                "デフォルトプリセットが設定されていません。\nNo default preset has been configured.\n'⭐ Set as Default' でプリセットをデフォルト設定してください。"
            )
            return
        presets = self.config.get_positive_presets()
        if default_name not in presets:
            QMessageBox.warning(
                self,
                "注意 / Warning",
                f"設定されたデフォルトプリセット '{default_name}' が見つかりません。\nThe configured default preset '{default_name}' was not found in presets."
            )
            return
        idx = self.cmb_presets.findData(default_name)
        if idx >= 0:
            self.cmb_presets.setCurrentIndex(idx)
        else:
            self.refresh_presets(select_preset_name=default_name)
        self.on_preset_selected(self.cmb_presets.currentIndex())
        QMessageBox.information(
            self,
            "復元完了 / Restored",
            f"デフォルトプリセット '{default_name}' を展開しました！\nRestored default preset '{default_name}'."
        )

    def on_select_all_applied(self):
        self.list_applied.selectAll()
        self.update_preview_from_selection()

    def on_bulk_import(self):
        import re
        text, ok = QInputDialog.getMultiLineText(
            self,
            "生プロンプト一括インポート / Bulk Import Positive Tags",
            "カンマ区切りのプロンプトテキストを貼り付けてください:\nPaste raw comma-separated prompt text:"
        )
        if not ok or not text.strip():
            return

        # Strip weight brackets, dangerous chars and values e.g. (tag:1.3), [tag], {tag}
        raw = sanitize_sd_prompt(text)
        raw = re.sub(r":[0-9.]+", "", raw)
        raw = re.sub(r"[()\[\]{}]", "", raw)
        tokens = [t.strip() for t in raw.split(",") if t.strip()]
        
        existing = set([self.list_stock.item(i).text() for i in range(self.list_stock.count())])
        added_count = 0
        for t in tokens:
            t_clean = sanitize_sd_prompt(t).strip()
            if t_clean and t_clean not in existing:
                self.list_stock.addItem(t_clean)
                existing.add(t_clean)
                added_count += 1
        
        if added_count > 0:
            self.save_stock()
            QMessageBox.information(
                self,
                "インポート完了 / Success",
                f"{added_count} 個の新しいタグをストックに追加しました！\nAdded {added_count} new tags to Stock."
            )
        else:
            QMessageBox.information(
                self,
                "インポート結果 / Result",
                "追加されたタグはありません（すべて既存または空でした）。\nNo new tags added (all were duplicates or empty)."
            )

    def load_stock(self):
        stock = self.config.get_positive_stock()
        self.list_stock.clear()
        self.list_applied.clear()
        
        seen_stock = set()
        unique_stock = []
        for tag in stock:
            t_clean = str(tag).strip()
            if t_clean and t_clean.lower() not in seen_stock:
                seen_stock.add(t_clean.lower())
                unique_stock.append(t_clean)
                self.list_stock.addItem(t_clean)

        if len(unique_stock) != len(stock):
            self.config.set_positive_stock(unique_stock)

        # Clear selection and preview on init
        self.list_applied.clear()
        self.list_applied.clearSelection()
        self.txt_preview.clear()

    def save_stock(self):
        stock = [self.list_stock.item(i).text().strip() for i in range(self.list_stock.count()) if self.list_stock.item(i).text().strip()]
        self.config.set_positive_stock(stock)

    def update_preview_from_selection(self):
        """Issue 7: Preview shows ONLY selected items in Applied list. Cleared if none selected."""
        selected = self.list_applied.selectedItems()
        if selected:
            tags = [item.text() for item in selected]
            self.txt_preview.setPlainText(", ".join(tags))
        else:
            self.txt_preview.clear()

    def on_clear_preview(self):
        """Clears selection in Applied list and clears preview text."""
        self.list_applied.clearSelection()
        self.txt_preview.clear()

    def on_add_stock_tag(self):
        text = self.txt_new_tag.text().strip()
        if not text:
            return
        cleaned = sanitize_sd_prompt(text)
        tokens = [t.strip() for t in cleaned.split(",") if t.strip()]
        if not tokens:
            return

        existing_stock = {self.list_stock.item(i).text().strip().lower() for i in range(self.list_stock.count())}
        existing_applied = {self.list_applied.item(i).text().strip().lower() for i in range(self.list_applied.count())}

        added_count = 0
        duplicate_tags = []

        for t in tokens:
            t_lower = t.lower()
            if t_lower in existing_stock:
                duplicate_tags.append(t)
                continue
            self.list_stock.addItem(t)
            existing_stock.add(t_lower)
            if t_lower not in existing_applied:
                self.list_applied.addItem(t)
                existing_applied.add(t_lower)
            added_count += 1

        self.txt_new_tag.clear()

        if added_count > 0:
            self.save_stock()

        if duplicate_tags and added_count == 0:
            QMessageBox.warning(
                self,
                "重複検知 / Duplicate Detected",
                f"入力されたタグは既にストックに存在します:\nThe following tag(s) are already in Stock:\n\n{', '.join(duplicate_tags)}"
            )
        elif duplicate_tags:
            QMessageBox.information(
                self,
                "追加完了 / Added",
                f"{added_count} 個の新しいタグを追加しました。（重複スキップ: {', '.join(duplicate_tags)}）\nAdded {added_count} tag(s). Duplicates skipped."
            )

    def on_transfer_to_apply(self):
        selected = self.list_stock.selectedItems()
        existing_applied = {self.list_applied.item(i).text().strip().lower() for i in range(self.list_applied.count())}
        for item in selected:
            t = item.text().strip()
            if t and t.lower() not in existing_applied:
                self.list_applied.addItem(t)
                existing_applied.add(t.lower())

    def on_transfer_to_stock(self):
        selected = self.list_applied.selectedItems()
        for item in selected:
            self.list_applied.takeItem(self.list_applied.row(item))
        self.update_preview_from_selection()

    def on_delete_stock(self):
        selected = self.list_stock.selectedItems()
        if not selected:
            QMessageBox.warning(
                self,
                "注意 / Warning",
                "削除するストック項目を選択してください。\nPlease select stock item(s) to delete."
            )
            return
        for item in selected:
            self.list_stock.takeItem(self.list_stock.row(item))
        self.save_stock()

    def on_remove_applied(self):
        selected = self.list_applied.selectedItems()
        if not selected:
            QMessageBox.warning(
                self,
                "注意 / Warning",
                "除外する適用項目を選択してください。\nPlease select applied item(s) to remove."
            )
            return
        for item in selected:
            self.list_applied.takeItem(self.list_applied.row(item))
        self.update_preview_from_selection()

    def on_move_up(self, list_widget: QListWidget, is_stock: bool):
        row = list_widget.currentRow()
        if row > 0:
            item = list_widget.takeItem(row)
            list_widget.insertItem(row - 1, item)
            list_widget.setCurrentRow(row - 1)
            if is_stock:
                self.save_stock()
            else:
                self.update_preview_from_selection()

    def on_move_down(self, list_widget: QListWidget, is_stock: bool):
        row = list_widget.currentRow()
        if 0 <= row < list_widget.count() - 1:
            item = list_widget.takeItem(row)
            list_widget.insertItem(row + 1, item)
            list_widget.setCurrentRow(row + 1)
            if is_stock:
                self.save_stock()
            else:
                self.update_preview_from_selection()

    def on_preset_selected(self, index: int):
        name = self.cmb_presets.currentData()
        if not name:
            self.list_applied.clearSelection()
            self.txt_preview.clear()
            return
        presets = self.config.get_positive_presets()
        if name in presets:
            tags = [t.strip() for t in presets[name] if t.strip()]
            self.list_applied.clear()
            for t in tags:
                item = QListWidgetItem(t)
                self.list_applied.addItem(item)
                item.setSelected(True)
            self.list_applied.selectAll()
            self.txt_preview.setPlainText(", ".join(tags))

    def on_save_preset(self):
        selected = self.list_applied.selectedItems()
        if not selected:
            selected = [self.list_applied.item(i) for i in range(self.list_applied.count())]
        tags = [item.text().strip() for item in selected if item.text().strip()]

        if not tags:
            QMessageBox.warning(
                self,
                "注意 / Warning",
                "プリセットに保存する適用タグがありません。\nNo applied tags to save as preset."
            )
            return

        name, ok = QInputDialog.getText(
            self,
            "プリセット保存 / Save Preset",
            "プリセット名を入力してください:\nEnter preset name:"
        )
        if not ok or not name.strip():
            return

        preset_name = name.strip()
        presets = self.config.get_positive_presets()

        # Check duplicate name with overwrite confirmation (VBA exact match)
        if preset_name in presets:
            ans = QMessageBox.question(
                self,
                "上書き確認 / Confirm Overwrite",
                f"プリセット '{preset_name}' は既に存在します。上書きしますか？\nPreset '{preset_name}' already exists. Overwrite?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            if ans != QMessageBox.Yes:
                return

        presets[preset_name] = tags
        self.config.data["PositivePresets"] = presets
        self.config.save()
        self.refresh_presets()
        self.cmb_presets.setCurrentText(preset_name)
        QMessageBox.information(
            self,
            "完了 / Success",
            f"ポジティブプリセット '{preset_name}' を保存しました。\nPositive preset '{preset_name}' saved."
        )

    def on_delete_preset(self):
        name = self.cmb_presets.currentData()
        if not name:
            return
        ans = QMessageBox.question(
            self,
            "削除確認 / Confirm Delete",
            f"プリセット '{name}' を削除しますか？\nDelete preset '{name}'?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if ans == QMessageBox.Yes:
            presets = self.config.get_positive_presets()
            if name in presets:
                del presets[name]
                self.config.data["PositivePresets"] = presets
                if self.config.get_setting("DefaultPositivePreset", "") == name:
                    self.config.set_setting("DefaultPositivePreset", "")
                self.config.save()
                self.refresh_presets()
                self.list_applied.clear()
                self.txt_preview.clear()

    def get_current_positive_prompt(self) -> str:
        """Returns preview text strictly from txt_preview without fallback."""
        return self.txt_preview.toPlainText().strip()

    def on_apply_cockpit(self):
        prev_text = self.get_current_positive_prompt()
        if prev_text:
            self.send_to_cockpit_beginning.emit(prev_text)
        else:
            QMessageBox.warning(
                self,
                "注意 / Warning",
                "ポジティブプレビュー欄が空です。適用するタグを選択してください。\nPositive preview is empty. Please select tags."
            )
