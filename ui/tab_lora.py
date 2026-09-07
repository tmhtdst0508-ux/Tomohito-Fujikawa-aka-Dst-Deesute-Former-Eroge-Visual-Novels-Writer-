"""
LoRA Tab for KENZEN SeaArt Helper v5.0.0
Manages LoRA library, system model name protection, strength adjustments,
trigger selection with individual weights (1.0-1.5), presets, and Wrap with Name/Hash.
"""

import hashlib
import os
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QListWidget, QComboBox, QGroupBox, QSplitter, QMessageBox, QFileDialog,
    QDoubleSpinBox, QTextEdit, QListWidgetItem, QInputDialog
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QKeySequence, QShortcut
from ..core.config_manager import ConfigManager, format_lora_preset_preview
from ..core.prompt_engine import PromptEngine, sanitize_sd_prompt
from .style import COLOR_ACTION, COLOR_SUCCESS, COLOR_DANGER, safe_copy_to_clipboard
from .widgets import PlainTextOnlyTextEdit


class TabLoRA(QWidget):
    send_to_cockpit = Signal(str)
    send_to_negative_preview = Signal(str)
    send_to_fav = Signal(str, str)

    def __init__(self, config_manager: ConfigManager, prompt_engine: PromptEngine, parent=None):
        super().__init__(parent)
        self.config = config_manager
        self.engine = prompt_engine
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(10)

        # 1. Top Preset Bar
        preset_bar = QHBoxLayout()
        lbl_preset = QLabel("LoRA Presets:")
        lbl_preset.setStyleSheet("font-weight: bold;")
        
        self.cmb_presets = QComboBox()
        self.cmb_presets.currentIndexChanged.connect(self.on_preset_selected)

        btn_save_preset = QPushButton("Save LoRA Preset")
        btn_save_preset.clicked.connect(self.on_save_preset)

        btn_set_default = QPushButton("⭐ Set as Default")
        btn_set_default.setToolTip("Set selected preset as startup default")
        btn_set_default.clicked.connect(self.on_set_default_preset)

        btn_call_default = QPushButton("🔄 Call Default")
        btn_call_default.setToolTip("Restore/apply startup default preset to preview / デフォルトプリセットを展開・復元")
        btn_call_default.clicked.connect(self.on_call_default_preset)

        btn_delete_preset = QPushButton("Delete LoRA Preset")
        btn_delete_preset.setProperty("btnType", "danger")
        btn_delete_preset.clicked.connect(self.on_delete_preset)

        preset_bar.addWidget(lbl_preset)
        preset_bar.addWidget(self.cmb_presets, 1)
        preset_bar.addWidget(btn_save_preset)
        preset_bar.addWidget(btn_set_default)
        preset_bar.addWidget(btn_call_default)
        preset_bar.addWidget(btn_delete_preset)
        layout.addLayout(preset_bar)

        splitter = QSplitter(Qt.Horizontal)

        # 2. Left: LoRA List
        left_box = QGroupBox("Registered LoRA Library")
        left_layout = QVBoxLayout(left_box)
        left_layout.setContentsMargins(8, 14, 8, 8)

        self.lora_list = QListWidget()
        self.lora_list.itemClicked.connect(self.on_lora_selected)
        left_layout.addWidget(self.lora_list)

        list_btn_bar = QHBoxLayout()
        btn_lora_up = QPushButton("▲ Up")
        btn_lora_up.clicked.connect(self.on_move_lora_up)
        btn_lora_down = QPushButton("▼ Down")
        btn_lora_down.clicked.connect(self.on_move_lora_down)
        btn_delete_lora = QPushButton("Delete")
        btn_delete_lora.setProperty("btnType", "danger")
        btn_delete_lora.clicked.connect(self.on_delete_lora)

        list_btn_bar.addWidget(btn_lora_up)
        list_btn_bar.addWidget(btn_lora_down)
        list_btn_bar.addWidget(btn_delete_lora)
        left_layout.addLayout(list_btn_bar)

        splitter.addWidget(left_box)

        # 3. Right: LoRA Details, System Name (Read-Only), Triggers & Wrap
        right_box = QGroupBox("LoRA Configuration & Trigger Wrap")
        right_layout = QVBoxLayout(right_box)
        right_layout.setContentsMargins(8, 14, 8, 8)
        right_layout.setSpacing(8)

        # Separate System Model Name (Read-Only) and Alias (Editable)
        h_names = QHBoxLayout()
        lbl_model_name = QLabel("System Name:")
        lbl_model_name.setFixedWidth(90)
        self.txt_model_name = QLineEdit()
        self.txt_model_name.setReadOnly(True)
        self.txt_model_name.setStyleSheet("background-color: #F1F5F9; color: #475569;")
        self.txt_model_name.setPlaceholderText("(Auto-filled from file / Read-Only)")

        lbl_alias = QLabel("LoRA Alias:")
        lbl_alias.setFixedWidth(75)
        self.txt_alias = QLineEdit()
        self.txt_alias.setPlaceholderText("e.g. character_name")

        h_names.addWidget(lbl_model_name)
        h_names.addWidget(self.txt_model_name, 1)
        h_names.addWidget(lbl_alias)
        h_names.addWidget(self.txt_alias, 1)
        right_layout.addLayout(h_names)

        # File browse for hash
        h_file = QHBoxLayout()
        lbl_file = QLabel("LoRA File:")
        lbl_file.setFixedWidth(90)
        self.txt_file_path = QLineEdit()
        self.txt_file_path.setPlaceholderText("Select safetensors file...")
        btn_browse = QPushButton("Browse...")
        btn_browse.clicked.connect(self.on_browse_file)
        h_file.addWidget(lbl_file)
        h_file.addWidget(self.txt_file_path)
        h_file.addWidget(btn_browse)
        right_layout.addLayout(h_file)

        # Hash & Strength
        h_strength = QHBoxLayout()
        lbl_hash = QLabel("Short Hash:")
        lbl_hash.setFixedWidth(90)
        self.txt_hash = QLineEdit()
        self.txt_hash.setPlaceholderText("10-12 char hash")

        lbl_weight = QLabel("Strength (Weight):")
        self.spin_weight = QDoubleSpinBox()
        self.spin_weight.setRange(0.1, 2.0)
        self.spin_weight.setSingleStep(0.05)
        self.spin_weight.setValue(1.0)

        h_strength.addWidget(lbl_hash)
        h_strength.addWidget(self.txt_hash)
        h_strength.addWidget(lbl_weight)
        h_strength.addWidget(self.spin_weight)
        right_layout.addLayout(h_strength)

        # Triggers Edit & Trigger Selection
        lbl_triggers = QLabel("Registered Trigger Words (Comma separated):")
        self.txt_triggers = QLineEdit()
        self.txt_triggers.setPlaceholderText("e.g. 1girl, green eyes, school uniform")
        self.txt_triggers.textChanged.connect(self.refresh_trigger_checkboxes)
        right_layout.addWidget(lbl_triggers)
        right_layout.addWidget(self.txt_triggers)

        # Negative Prompts
        lbl_nega = QLabel("Recommended Negative Prompts:")
        self.txt_nega = QLineEdit()
        self.txt_nega.setPlaceholderText("e.g. bad hands, missing fingers")
        right_layout.addWidget(lbl_nega)
        right_layout.addWidget(self.txt_nega)

        # Save/Update LoRA Button
        btn_save_lora = QPushButton("💾 Save / Update LoRA Definition in Library")
        btn_save_lora.clicked.connect(self.on_save_lora)
        right_layout.addWidget(btn_save_lora)

        # Trigger Selection List with Weights & Wrap Controls
        grp_wrap = QGroupBox("Trigger Word Selection & Wrap")
        wrap_layout = QVBoxLayout(grp_wrap)
        wrap_layout.setContentsMargins(6, 12, 6, 6)
        wrap_layout.setSpacing(6)

        self.trigger_list = QListWidget()
        self.trigger_list.setSelectionMode(QListWidget.MultiSelection)
        self.trigger_list.setFixedHeight(75)
        wrap_layout.addWidget(self.trigger_list)

        # Trigger Weight Combo & Wrap Buttons
        wrap_btn_bar = QHBoxLayout()
        lbl_tw = QLabel("Trigger Weight:")
        self.cmb_trigger_weight = QComboBox()
        for w in ["1.0", "1.1", "1.2", "1.3", "1.4", "1.5"]:
            self.cmb_trigger_weight.addItem(w)
        self.cmb_trigger_weight.setCurrentText("1.0")

        btn_wrap_name = QPushButton("Wrap with Name <lora:name:w>")
        btn_wrap_name.setProperty("btnType", "action")
        btn_wrap_name.clicked.connect(lambda: self.on_wrap_lora(use_hash=False))

        btn_wrap_hash = QPushButton("Wrap with Hash <lora:hash:w>")
        btn_wrap_hash.setProperty("btnType", "action")
        btn_wrap_hash.clicked.connect(lambda: self.on_wrap_lora(use_hash=True))

        wrap_btn_bar.addWidget(lbl_tw)
        wrap_btn_bar.addWidget(self.cmb_trigger_weight)
        wrap_btn_bar.addWidget(btn_wrap_name)
        wrap_btn_bar.addWidget(btn_wrap_hash)
        wrap_layout.addLayout(wrap_btn_bar)

        right_layout.addWidget(grp_wrap)

        splitter.addWidget(right_box)
        splitter.setStretchFactor(0, 3)
        splitter.setStretchFactor(1, 4)

        layout.addWidget(splitter, 1)

        # 4. Spacious Generated Tag Preview Box
        grp_prev = QGroupBox("Generated Tag Preview (LoRA & Triggers)")
        prev_layout = QVBoxLayout(grp_prev)
        prev_layout.setContentsMargins(8, 14, 8, 8)
        
        self.txt_preview = PlainTextOnlyTextEdit()
        self.txt_preview.setFixedHeight(110)
        self.txt_preview.setPlaceholderText("Output LoRA tags and wrapped triggers will appear here...")
        prev_layout.addWidget(self.txt_preview)

        prev_sub_bar = QHBoxLayout()
        btn_remove_lora = QPushButton("Remove LoRA")
        btn_remove_lora.setProperty("btnType", "warning")
        btn_remove_lora.setToolTip("Remove selected LoRA and its triggers from Preview")
        btn_remove_lora.clicked.connect(self.on_remove_selected_lora)

        btn_forget_lora = QPushButton("Forget LoRA")
        btn_forget_lora.setProperty("btnType", "danger")
        btn_forget_lora.setToolTip("Reset all configuration fields, trigger selections, and preview")
        btn_forget_lora.clicked.connect(self.on_forget_lora)

        btn_clear_prev = QPushButton("Clear Preview")
        btn_clear_prev.setProperty("btnType", "danger")
        btn_clear_prev.clicked.connect(self.on_clear_preview)

        prev_sub_bar.addStretch()
        prev_sub_bar.addWidget(btn_remove_lora)
        prev_sub_bar.addWidget(btn_forget_lora)
        prev_sub_bar.addWidget(btn_clear_prev)
        prev_layout.addLayout(prev_sub_bar)

        layout.addWidget(grp_prev)

        # 5. Bottom Action Bar
        bottom_bar = QHBoxLayout()
        
        btn_get_lora_negative = QPushButton("📥 Send LoRA Negative to Negative Preview")
        btn_get_lora_negative.setToolTip("Sends this LoRA's Negative Prompt directly to the Negative Tab Preview box")
        btn_get_lora_negative.setFixedHeight(38)
        btn_get_lora_negative.clicked.connect(self.on_send_lora_negative)

        btn_send_lora_to_fav = QPushButton("⭐ Send LoRA to Fav")
        btn_send_lora_to_fav.setProperty("btnType", "action")
        btn_send_lora_to_fav.setToolTip("Sends generated LoRA tags from Preview to Favorites Tab")
        btn_send_lora_to_fav.setFixedHeight(38)
        btn_send_lora_to_fav.clicked.connect(self.on_send_lora_to_fav)

        self.btn_send_cockpit = QPushButton("🚀 Send Generated LoRA Tags to Cockpit (Ctrl+Shift+L)")
        self.btn_send_cockpit.setProperty("btnType", "success")
        self.btn_send_cockpit.setToolTip("Sends generated LoRA tags from Preview to Cockpit prompt (Ctrl+Shift+L)")
        self.btn_send_cockpit.setFixedHeight(38)
        self.btn_send_cockpit.clicked.connect(self.on_send_cockpit)

        bottom_bar.addWidget(btn_get_lora_negative)
        bottom_bar.addWidget(btn_send_lora_to_fav)
        bottom_bar.addWidget(self.btn_send_cockpit)
        layout.addLayout(bottom_bar)

        self.refresh_presets(load_default=True)
        self.load_loras()

    def refresh_presets(self, select_preset_name: str = None, load_default: bool = False):
        presets = self.config.get_lora_presets()
        self.cmb_presets.blockSignals(True)
        self.cmb_presets.clear()
        self.cmb_presets.addItem("-- Select LoRA Preset / プリセット選択 --", None)
        target_idx = 0
        if load_default and not select_preset_name:
            default_name = self.config.get_setting("DefaultLoRAPreset", "")
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

    def load_loras(self):
        loras = self.config.get_lora_list()
        self.lora_list.clear()
        for lora in loras:
            alias = lora.get("alias", "Unknown")
            w = lora.get("weight", 1.0)
            item = QListWidgetItem(f"{alias} (w: {w:.2f})")
            item.setData(Qt.UserRole, lora)
            self.lora_list.addItem(item)

    def on_lora_selected(self, item: QListWidgetItem):
        lora = item.data(Qt.UserRole)
        if not lora:
            return
        self.txt_alias.setText(lora.get("alias", ""))
        self.txt_model_name.setText(lora.get("model_name", lora.get("alias", "")))
        self.txt_hash.setText(lora.get("hash", ""))
        self.spin_weight.setValue(float(lora.get("weight", 1.0)))
        self.txt_triggers.setText(lora.get("triggers", ""))
        self.txt_nega.setText(lora.get("negative", ""))
        self.refresh_trigger_checkboxes()

    def refresh_trigger_checkboxes(self):
        raw = self.txt_triggers.text().strip()
        self.trigger_list.clear()
        if raw:
            tokens = [t.strip() for t in raw.split(",") if t.strip()]
            for t in tokens:
                item = QListWidgetItem(t)
                self.trigger_list.addItem(item)
                item.setSelected(True)

    def on_browse_file(self):
        fname, _ = QFileDialog.getOpenFileName(
            self,
            "LoRAファイルを選択 / Select LoRA File",
            "",
            "LoRA Files (*.safetensors *.ckpt *.pt)"
        )
        if fname:
            self.txt_file_path.setText(fname)
            base_name = os.path.splitext(os.path.basename(fname))[0]
            self.txt_model_name.setText(base_name)
            if not self.txt_alias.text().strip():
                self.txt_alias.setText(base_name)
            h_val = self.calculate_short_hash(fname)
            if h_val:
                self.txt_hash.setText(h_val)

    def calculate_short_hash(self, file_path: str) -> str:
        try:
            hasher = hashlib.sha256()
            with open(file_path, "rb") as f:
                chunk = f.read(65536)
                hasher.update(chunk)
            return hasher.hexdigest()[:10]
        except Exception:
            return ""

    def on_wrap_lora(self, use_hash: bool = False):
        alias = self.txt_alias.text().strip()
        model_name = self.txt_model_name.text().strip() or alias
        h_val = self.txt_hash.text().strip()
        w = self.spin_weight.value()

        if use_hash and h_val:
            identifier = h_val
        else:
            identifier = alias if alias else model_name

        if not identifier:
            QMessageBox.warning(
                self,
                "注意 / Warning",
                "LoRAが選択されていません。\nPlease select or register a LoRA first."
            )
            return

        lora_tag = f"<lora:{identifier}:{w:.2f}>"

        # Check if LoRA tag is already in preview
        current_prev = self.txt_preview.toPlainText().strip()
        skipped_items = []
        appended_parts = []

        import re
        # Check duplicate LoRA identifier in preview
        lora_identifier_pattern = rf"<lora:{re.escape(identifier)}:[0-9.]+>"
        if re.search(lora_identifier_pattern, current_prev, re.IGNORECASE):
            skipped_items.append(f"LoRA: {identifier}")
        else:
            appended_parts.append(lora_tag)

        # Process triggers with duplicate check
        selected_items = self.trigger_list.selectedItems()
        try:
            tw_val = float(self.cmb_trigger_weight.currentText())
        except (ValueError, TypeError):
            tw_val = 1.0

        for item in selected_items:
            t_text = item.text().strip()
            if not t_text:
                continue
            # Check if trigger already exists in preview (word/token boundary match)
            if re.search(rf"(?:^|[,\s(]){re.escape(t_text)}(?:[,\s):]|$)", current_prev, re.IGNORECASE):
                skipped_items.append(f"Trigger: {t_text}")
                continue

            if tw_val > 1.0:
                formatted_t = f"({t_text}:{tw_val:.1f})"
            else:
                formatted_t = t_text
            appended_parts.append(formatted_t)

        if appended_parts:
            new_text = " ".join(appended_parts)
            if current_prev:
                combined = f"{current_prev} {new_text}"
            else:
                combined = new_text
            self.txt_preview.setPlainText(combined)

        if skipped_items and not appended_parts:
            QMessageBox.information(
                self,
                "重複スキップ / Duplicates Skipped",
                f"選択された項目は既にプレビューに存在するためスキップされました:\nThe following items already exist in Preview:\n\n{', '.join(skipped_items)}"
            )
        elif skipped_items:
            QMessageBox.information(
                self,
                "追加完了（重複スキップ） / Added with Duplicates Skipped",
                f"タグを追加しました。（重複スキップ: {', '.join(skipped_items)}）\nTags added. Duplicates skipped."
            )

    def on_save_lora(self):
        alias = self.txt_alias.text().strip()
        model_name = sanitize_sd_prompt(self.txt_model_name.text().strip()) or alias
        if not alias:
            QMessageBox.warning(
                self,
                "注意 / Warning",
                "LoRAのエイリアスを入力してください。\nPlease enter a LoRA alias."
            )
            return

        loras = self.config.get_lora_list()
        new_entry = {
            "alias": alias, # Alias name is preserved as-is
            "model_name": model_name,
            "hash": sanitize_sd_prompt(self.txt_hash.text().strip()),
            "weight": self.spin_weight.value(),
            "triggers": sanitize_sd_prompt(self.txt_triggers.text().strip()),
            "negative": sanitize_sd_prompt(self.txt_nega.text().strip())
        }

        # Check existing alias with overwrite confirmation (VBA exact match)
        idx = next((i for i, item in enumerate(loras) if item.get("alias", "").strip().lower() == alias.lower()), None)
        if idx is not None:
            ans = QMessageBox.question(
                self,
                "上書き確認 / Confirm Overwrite",
                f"LoRAエイリアス '{alias}' は既に登録されています。上書きしますか？\nLoRA Alias '{alias}' is already registered. Overwrite?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            if ans != QMessageBox.Yes:
                return
            loras[idx] = new_entry
        else:
            loras.append(new_entry)

        self.config.save_lora_list(loras)
        self.load_loras()
        QMessageBox.information(
            self,
            "完了 / Success",
            f"LoRA '{alias}' を保存しました。\nLoRA '{alias}' saved."
        )

    def on_move_lora_up(self):
        """Moves selected LoRA one position up in the list and saves to JSON."""
        row = self.lora_list.currentRow()
        if row <= 0:
            return
        loras = self.config.get_lora_list()
        if row < len(loras):
            loras[row - 1], loras[row] = loras[row], loras[row - 1]
            self.config.save_lora_list(loras)
            self.load_loras()
            self.lora_list.setCurrentRow(row - 1)

    def on_move_lora_down(self):
        """Moves selected LoRA one position down in the list and saves to JSON."""
        row = self.lora_list.currentRow()
        loras = self.config.get_lora_list()
        if row < 0 or row >= len(loras) - 1:
            return
        loras[row], loras[row + 1] = loras[row + 1], loras[row]
        self.config.save_lora_list(loras)
        self.load_loras()
        self.lora_list.setCurrentRow(row + 1)

    def on_delete_lora(self):
        curr_item = self.lora_list.currentItem()
        if not curr_item:
            return
        lora = curr_item.data(Qt.UserRole)
        alias = lora.get("alias", "")
        ans = QMessageBox.question(
            self,
            "削除確認 / Confirm Delete",
            f"LoRA '{alias}' を削除しますか？\nDelete LoRA '{alias}'?"
        )
        if ans == QMessageBox.Yes:
            loras = self.config.get_lora_list()
            loras = [l for l in loras if l.get("alias") != alias]
            self.config.save_lora_list(loras)
            self.clear_all_ui()
            self.load_loras()
            self.lora_list.clearSelection()

    def on_save_preset(self):
        prev_txt = self.txt_preview.toPlainText().strip()
        if not prev_txt:
            QMessageBox.warning(
                self,
                "注意 / Warning",
                "プレビューボックスにLoRAタグがありません。\nPreview box is empty."
            )
            return

        name, ok = QInputDialog.getText(
            self,
            "LoRAプリセット保存 / Save LoRA Preset",
            "プリセット名を入力してください:\nEnter LoRA preset name:"
        )
        if not ok or not name.strip():
            return

        preset_name = name.strip()
        presets = self.config.get_lora_presets()

        # Check duplicate name with overwrite confirmation (VBA exact match)
        if preset_name in presets:
            ans = QMessageBox.question(
                self,
                "上書き確認 / Confirm Overwrite",
                f"LoRAプリセット '{preset_name}' は既に存在します。上書きしますか？\nLoRA preset '{preset_name}' already exists. Overwrite?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            if ans != QMessageBox.Yes:
                return

        presets[preset_name] = prev_txt
        self.config.save_lora_presets(presets)
        self.refresh_presets()
        self.cmb_presets.setCurrentText(preset_name)
        QMessageBox.information(
            self,
            "完了 / Success",
            f"LoRAプリセット '{preset_name}' を保存しました。\nLoRA preset '{preset_name}' saved."
        )

    def on_set_default_preset(self):
        name = self.cmb_presets.currentData()
        if not name:
            QMessageBox.warning(
                self,
                "注意 / Warning",
                "デフォルトに設定するLoRAプリセットを選択してください。\nPlease select a LoRA preset to set as default."
            )
            return
        self.config.set_setting("DefaultLoRAPreset", name)
        QMessageBox.information(
            self,
            "設定完了 / Success",
            f"LoRAプリセット '{name}' を起動時デフォルトに設定しました！\nLoRA preset '{name}' set as startup default."
        )

    def on_call_default_preset(self):
        default_name = self.config.get_setting("DefaultLoRAPreset", "")
        if not default_name:
            QMessageBox.warning(
                self,
                "注意 / Warning",
                "デフォルトLoRAプリセットが設定されていません。\nNo default LoRA preset has been configured.\n'⭐ Set as Default' でプリセットをデフォルト設定してください。"
            )
            return
        presets = self.config.get_lora_presets()
        if default_name not in presets:
            QMessageBox.warning(
                self,
                "注意 / Warning",
                f"設定されたデフォルトLoRAプリセット '{default_name}' が見つかりません。\nThe configured default LoRA preset '{default_name}' was not found in presets."
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
            f"デフォルトLoRAプリセット '{default_name}' を展開しました！\nRestored default LoRA preset '{default_name}'."
        )

    def on_preset_selected(self, index: int):
        name = self.cmb_presets.currentData()
        if not name:
            self.txt_preview.clear()
            return
        presets = self.config.get_lora_presets()
        if name in presets:
            raw_val = presets[name]
            formatted_text = format_lora_preset_preview(raw_val)
            self.txt_preview.setPlainText(formatted_text)

    def on_delete_preset(self):
        name = self.cmb_presets.currentData()
        if not name:
            return
        ans = QMessageBox.question(
            self,
            "削除確認 / Confirm Delete",
            f"プリセット '{name}' を削除しますか？\nDelete LoRA preset '{name}'?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if ans == QMessageBox.Yes:
            presets = self.config.get_lora_presets()
            if name in presets:
                del presets[name]
                if self.config.get_setting("DefaultLoRAPreset", "") == name:
                    self.config.set_setting("DefaultLoRAPreset", "")
                self.config.save_lora_presets(presets)
                self.refresh_presets()
                self.txt_preview.clear()

    def get_current_lora_prompt(self) -> str:
        """Returns sanitized generated LoRA tags strictly from txt_preview."""
        return sanitize_sd_prompt(self.txt_preview.toPlainText().strip())

    def on_send_cockpit(self):
        preview_txt = self.get_current_lora_prompt()
        if preview_txt:
            self.send_to_cockpit.emit(preview_txt)
        else:
            QMessageBox.warning(
                self,
                "注意 / Warning",
                "送信するLoRAタグがプレビューボックスにありません。\nNo LoRA tags in the preview box."
            )

    def on_send_lora_negative(self):
        nega = sanitize_sd_prompt(self.txt_nega.text().strip())
        if not nega:
            QMessageBox.warning(
                self,
                "注意 / Warning",
                "選択中LoRAに登録されているネガティブプロンプトがありません。\nNo negative prompt registered for this LoRA."
            )
            return
        self.send_to_negative_preview.emit(nega)
        QMessageBox.information(
            self,
            "送信完了 / Success",
            f"LoRAネガティブをNegativeタブのプレビュー欄に転送しました！\nTransferred LoRA Negative to Negative tab preview:\n{nega}"
        )

    def on_send_lora_to_fav(self):
        preview_txt = sanitize_sd_prompt(self.txt_preview.toPlainText().strip())
        if not preview_txt:
            QMessageBox.warning(
                self,
                "注意 / Warning",
                "送信するLoRAタグがプレビューボックスにありません。\nNo LoRA tags in the preview box."
            )
            return
        alias = self.txt_alias.text().strip() or "LoRA Preset"
        self.send_to_fav.emit(preview_txt, f"LoRA: {alias}")
        QMessageBox.information(
            self,
            "送信完了 / Success",
            "LoRAタグをFavoritesタブへ転送しました！\nTransferred LoRA tags to Favorites."
        )

    def on_clear_preview(self):
        self.txt_preview.clear()

    def on_remove_selected_lora(self):
        """
        Removes the currently selected LoRA and its associated triggers from Preview text.
        Shows warning dialog if no LoRA is selected or if the LoRA is not applied in preview.
        """
        import re
        curr_item = self.lora_list.currentItem()
        if not curr_item:
            QMessageBox.warning(
                self,
                "注意 / Warning",
                "削除対象のLoRAをリストから選択してください。\nPlease select a LoRA from the list to remove."
            )
            return

        lora = curr_item.data(Qt.UserRole)
        if not lora:
            return

        alias = str(lora.get("alias") or "").strip()
        model_name = str(lora.get("model_name") or "").strip()
        hash_val = str(lora.get("hash") or "").strip()
        triggers_raw = str(lora.get("triggers") or "").strip()

        preview = self.txt_preview.toPlainText().strip()
        if not preview:
            QMessageBox.warning(
                self,
                "注意 / Warning",
                "プレビューボックスが空です。\nPreview box is empty."
            )
            return

        # Check if LoRA is applied in preview
        identifiers = [name for name in [model_name, hash_val, alias] if name]
        found_in_preview = False
        
        # Check <lora:...> tags
        for ident in identifiers:
            pattern = rf"<lora:{re.escape(ident)}:[^>]+>"
            if re.search(pattern, preview, re.IGNORECASE):
                found_in_preview = True
                break

        # Check trigger tokens if any
        trigger_tokens = [t.strip() for t in triggers_raw.split(",") if t.strip()]
        if not found_in_preview and trigger_tokens:
            for t in trigger_tokens:
                t_pat = rf"(\({re.escape(t)}:[0-9.]+\)|\b{re.escape(t)}\b)"
                if re.search(t_pat, preview, re.IGNORECASE):
                    found_in_preview = True
                    break

        if not found_in_preview:
            QMessageBox.warning(
                self,
                "注意 / Warning",
                f"選択されたLoRA '{alias}' はプレビュー内に適用されていません。\n"
                f"The selected LoRA '{alias}' is not present in the preview."
            )
            return

        # Perform removal
        new_preview = preview
        for ident in identifiers:
            pattern = rf"<lora:{re.escape(ident)}:[^>]+>"
            new_preview = re.sub(pattern, "", new_preview, flags=re.IGNORECASE)

        for t in trigger_tokens:
            t_pat = rf"(\({re.escape(t)}:[0-9.]+\)|\b{re.escape(t)}\b)"
            new_preview = re.sub(t_pat, "", new_preview, flags=re.IGNORECASE)

        # Clean up commas and spaces in new preview
        new_preview = re.sub(r",[\s,]*", ", ", new_preview)
        new_preview = re.sub(r"\s+,\s*", ", ", new_preview)
        new_preview = re.sub(r"^\s*,\s*", "", new_preview)
        new_preview = re.sub(r"\s*,\s*$", "", new_preview)
        new_preview = re.sub(r"[ \t]+", " ", new_preview).strip()

        self.txt_preview.setPlainText(new_preview)
        QMessageBox.information(
            self,
            "削除完了 / Success",
            f"LoRA '{alias}' および関連トリガーをプレビューから削除しました。\n"
            f"Removed LoRA '{alias}' from preview."
        )

    def on_forget_lora(self):
        """
        Clears all configuration fields, trigger selections, dropdown weights, and preview.
        Shows warning dialog if all fields are already empty.
        """
        has_content = any([
            bool(self.txt_alias.text().strip()),
            bool(self.txt_model_name.text().strip()),
            bool(self.txt_file_path.text().strip()),
            bool(self.txt_hash.text().strip()),
            bool(self.txt_triggers.text().strip()),
            bool(self.txt_nega.text().strip()),
            self.trigger_list.count() > 0,
            bool(self.txt_preview.toPlainText().strip()),
            self.lora_list.currentItem() is not None
        ])

        if not has_content:
            QMessageBox.warning(
                self,
                "注意 / Warning",
                "クリアする対象がありません。\nAll fields and preview are already empty."
            )
            return

        self.txt_alias.clear()
        self.txt_model_name.clear()
        self.txt_file_path.clear()
        self.txt_hash.clear()
        self.spin_weight.setValue(1.0)
        self.txt_triggers.clear()
        self.txt_nega.clear()
        self.trigger_list.clear()
        self.cmb_trigger_weight.setCurrentText("1.0")
        self.txt_preview.clear()
        self.lora_list.clearSelection()

        QMessageBox.information(
            self,
            "初期化完了 / Success",
            "LoRA設定項目およびプレビューをすべて初期化しました。\nAll configuration fields and preview reset."
        )

    def clear_all_ui(self):
        """Issue 13: Clears all LoRA UI edit inputs and preview on NUKE."""
        self.txt_alias.clear()
        self.txt_model_name.clear()
        self.txt_file_path.clear()
        self.txt_hash.clear()
        self.spin_weight.setValue(1.0)
        self.txt_triggers.clear()
        self.txt_nega.clear()
        self.trigger_list.clear()
        self.cmb_trigger_weight.setCurrentText("1.0")
        self.txt_preview.clear()
